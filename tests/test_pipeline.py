from decimal import Decimal
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

from pipeline.analysis import (
    Partner, annual_indicators, average_ranks, headroom, replacement, risk,
    sensitivity, spearman,
)
from pipeline.build import dataset, load_json, observations, query


D = Decimal


def partner(code, value, unspecified=False):
    return Partner(code, {"en": code, "ar": code}, D(value), unspecified)


def test_replacement_worked_formula_and_cap():
    assert replacement(D("40"), D("100"), D("0.25")) == D("0.375")
    assert replacement(D("10"), D("100"), D("0.5")) == 1
    assert replacement(None, D("100"), D("0.25")) is None


def test_single_supplier():
    row = annual_indicators(2024, [partner("a", 125)])
    assert row["total"] == 125
    assert row["top1"] == row["top3"] == 1
    assert row["hhi"] == 10000
    assert row["risk"] == "high"
    assert all(row["scenario"][key] == 0 for key in ("low", "central", "high"))
    assert sum(p["share"] for p in row["partners"]) == 1


def test_equal_shares_at_2500_are_medium():
    row = annual_indicators(2024, [partner(code, 10) for code in "abcd"])
    assert row["top1"] == .25
    assert row["top3"] == .75
    assert row["hhi"] == 2500
    assert row["risk"] == "medium"
    assert row["reason"] == "hhi"
    assert row["scenario"]["central"] == .75


@pytest.mark.parametrize(("share", "hhi", "expected"), [
    (".50", 2499, ("high", "top1")),
    (".29", D("2500.001"), ("high", "hhi")),
    (".30", 1499, ("medium", "top1")),
    (".29", 1500, ("medium", "hhi")),
    (".29", 1499, ("low", "low")),
])
def test_risk_boundaries(share, hhi, expected):
    assert risk(D(share), hhi) == expected


def test_world_excluded_and_unspecified_not_ranked():
    path = Path(__file__).parent / "fixtures/comtrade-small.json"
    rows = dataset(load_json(path))
    ref = {
        "H6": {"848180": {}},
        "partner": {
            "380": {"text": "Italy", "PartnerCodeIsoAlpha2": "IT"},
            "156": {"text": "China", "PartnerCodeIsoAlpha2": "CN"},
            "899": {"text": "Areas, nes", "isGroup": False},
        },
    }
    partners, world, revision = observations(rows, 2024, "848180", ref, {"IT": "إيطاليا", "CN": "الصين"})
    assert world == 100
    assert revision == "HS 2022"
    assert {p.code for p in partners} == {"380", "156", "899"}
    row = annual_indicators(2024, partners)
    assert row["top1"] == .4
    assert row["top3"] == .75
    assert row["hhi"] == 3450
    assert row["scenario"]["central"] == .375
    assert row["partners"][-1]["unspecified"] is True


def test_unranked_partners_roll_up_after_hhi():
    ranked = [partner(str(number), 1) for number in range(11)]
    unranked = [partner("z", 8, True), partner("x", 1, True)]
    row = annual_indicators(2024, ranked + unranked)
    assert row["hhi"] == 1900  # 11 × 5² + 40² + 5²
    assert row["top1"] == .05
    assert row["top3"] == .15
    assert row["risk"] == "medium"
    chart = row["partners"]
    assert [p["code"] for p in chart[-2:]] == ["other", "unspecified"]
    assert chart[-2]["value"] == 3
    assert chart[-1]["value"] == 9
    assert sum(p["share"] for p in chart) == pytest.approx(1, abs=.01)


def test_headroom_with_missing_year_and_unreported_current_partner():
    data = {
        2021: [partner("a", 12), partner("b", 23), partner("c", 10), partner("u", 9, True)],
        2023: [partner("a", 50), partner("b", 22), partner("u", 1, True)],
    }
    result = headroom(data)
    assert result["value"] == 11
    assert result["ratio"] == .22
    assert result["example"] == {
        "name": {"en": "c", "ar": "c"}, "latest": 0, "peak": 10, "peak_year": 2021,
        "content_type": "calculated",
    }
    assert headroom({2023: data[2023]})["value"] == 0
    assert headroom({}) is None
    assert annual_indicators(2023, []) is None
    assert headroom({2023: [partner("u", 1, True)]}) is None


def test_headroom_ratio_caps_at_one():
    data = {2022: [partner("b", 100)], 2023: [partner("a", 50), partner("b", 10)]}
    assert headroom(data)["value"] == 90
    assert headroom(data)["ratio"] == 1


def test_spearman_midranks_and_missing_overlap():
    assert average_ranks({"a": 3, "b": 3, "c": 2}) == {"a": 1.5, "b": 1.5, "c": 3}
    left = {"a": 3, "b": 3, "c": 2, "x": 4}
    right = {"a": 3, "b": 2, "c": 1, "z": 9}
    rho, count = spearman(left, right)
    assert count == 3
    assert rho == pytest.approx(3**.5 / 2)
    assert spearman({"a": 2, "b": 1}, {"a": 1, "b": 2}) == (-1, 2)
    assert spearman(left, {"a": 1, "b": 2}) == (None, 2)
    assert spearman(left, {"a": 1}) == (None, 1)


def test_sensitivity_rank_movements_with_cap():
    def year(value):
        return annual_indicators(2025, [partner("a", value)] + [partner(key, 10) for key in "bcdefgh"])
    products = [{"hs6": code, "years": [year(value)]}
                for code, value in [("a", 15), ("b", 20), ("c", 80)]]
    result = sensitivity(products)
    assert result["assumption_stability"] == "depends"
    assert result["most_moved"] == {
        "scenario": [{"hs6": "a", "change": .5}, {"hs6": "b", "change": .5}],
        "hhi": [],
    }
    assert len(result["correlations"]) == 6
    assert all(r["count"] == 3 for r in result["correlations"])
    assert sensitivity([])["assumption_stability"] is None


def test_sensitivity_uses_each_group_coverage_independently():
    def product(code, hhi_by_year, gap):
        return {
            "hs6": code,
            "years": [
                {"year": year, "hhi": hhi,
                 "scenario": {"low": gap, "central": gap, "high": 1}}
                for year, hhi in hhi_by_year.items()
            ],
        }
    rows = [
        product("a", {2023: 8000, 2024: 6000, 2025: 3000}, .5),
        product("b", {2023: 6000, 2024: 3000, 2025: 8000}, .4),
        product("c", {2023: 3000, 2024: 8000, 2025: 6000}, .3),
        product("d", {2025: 10000}, .6),
    ]
    result = sensitivity(rows)
    assert result["most_moved"] == {
        "scenario": [{"hs6": "c", "change": 1.5}, {"hs6": "d", "change": 1.5}],
        "hhi": [{"hs6": "a", "change": 2.0}, {"hs6": "b", "change": 2.0},
                {"hs6": "c", "change": 2.0}],
    }
    assert len(result["correlations"]) == 15
    pair = next(row for row in result["correlations"]
                if (row["left"], row["right"]) == ("r_low", "hhi_2025"))
    assert pair["count"] == 4


def test_public_request_has_one_period_and_all_partners():
    parsed = urlparse(query(2025, "848180"))
    params = parse_qs(parsed.query)
    assert parsed.path == "/public/v1/preview/C/A/HS"
    assert params["period"] == ["2025"]
    assert params["reporterCode"] == ["682"]
    assert params["flowCode"] == ["M"]
    assert params["cmdCode"] == ["848180"]
    assert params["maxRecords"] == ["500"]
    assert "partnerCode" not in params
    keyed = urlparse(query(2025, "848180", "not-in-url"))
    assert keyed.path == "/data/v1/get/C/A/HS"
    assert "not-in-url" not in keyed.geturl()


def test_response_cap_is_not_accepted():
    with pytest.raises(ValueError, match="cap"):
        dataset({"count": 500, "data": [{}] * 500})
