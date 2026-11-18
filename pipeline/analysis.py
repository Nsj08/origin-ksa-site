"""Origin KSA formulas, independent of retrieval and presentation.

Values are nominal US dollars. Do the arithmetic with Decimal, and convert to
JSON numbers only when returning the public indicators. Retain separate raw
partner categories for HHI even where the chart combines unspecified entries.
"""

from dataclasses import dataclass
from decimal import Decimal
from itertools import combinations, groupby
from math import sqrt


GROWTH = {"low": Decimal("0.10"), "central": Decimal("0.25"), "high": Decimal("0.50")}
CHART_COUNTRIES = 8
CHART_TOTAL_NAMES = {
    "other": {"en": "Other suppliers", "ar": "موردون آخرون"},
    "unspecified": {"en": "Unspecified", "ar": "غير محدد"},
}


@dataclass(frozen=True)
class Partner:
    code: str
    name: dict
    value: Decimal
    unspecified: bool = False


def risk(top1, hhi):
    """Return the risk label and the first condition that establishes it."""
    if top1 >= Decimal("0.50"):
        return "high", "top1"
    if hhi > 2500:
        return "high", "hhi"
    if top1 >= Decimal("0.30"):
        return "medium", "top1"
    if hhi >= 1500:
        return "medium", "hhi"
    return "low", "low"


def replacement(largest, total, growth):
    """Share of the lost USD value replaced under the selected assumption."""
    if largest is None or largest <= 0:
        return None
    return min(Decimal(1), growth * (total - largest) / largest)


def countries(partners):
    return sorted(
        (p for p in partners if not p.unspecified and p.value > 0),
        key=lambda p: (-p.value, p.code),
    )


def chart_row(code, name, value, total, *, unspecified=False, aggregate=False):
    return {
        "code": code,
        "name": name,
        "value": float(value),
        "share": float(value / total),
        "unspecified": unspecified,
        "aggregate": aggregate,
        "content_type": "calculated" if aggregate else "observed",
    }


def annual_indicators(year, partners):
    """Calculate first from the full input, then roll up the public chart."""
    total = sum(p.value for p in partners)
    if total <= 0:
        return None
    ranked = countries(partners)
    largest = ranked[0].value if ranked else None
    top1 = largest / total if largest is not None else None
    top3 = sum(p.value for p in ranked[:3]) / total if ranked else None
    hhi = 10000 * sum(p.value**2 for p in partners) / total**2
    label, reason = risk(top1, hhi) if top1 is not None else (None, None)

    chart = [chart_row(p.code, p.name, p.value, total) for p in ranked[:CHART_COUNTRIES]]
    other = sum(p.value for p in ranked[CHART_COUNTRIES:])
    unspecified = sum(p.value for p in partners if p.unspecified)
    for code, value in (("other", other), ("unspecified", unspecified)):
        if value:
            chart.append(chart_row(
                code, CHART_TOTAL_NAMES[code], value, total,
                aggregate=True, unspecified=code == "unspecified",
            ))

    scenario = {"content_type": "hypothetical"}
    for key, growth in GROWTH.items():
        replaced = replacement(largest, total, growth)
        scenario[key] = float(replaced) if replaced is not None else None
    return {
        "year": year,
        "total": float(total),
        "partners": chart,
        "top1": float(top1) if top1 is not None else None,
        "top3": float(top3) if top3 is not None else None,
        "hhi": float(hhi),
        "risk": label,
        "reason": reason,
        "scenario": scenario,
        "content_type": "calculated",
    }


def headroom(history):
    """Compare each country peak to its latest observed value.

    An absent country in an accepted product-year contributes zero in that
    year. Missing product-years do not enter the calculation. Unspecified
    partners cannot contribute country-level headroom.
    """
    if not history:
        return None
    latest_year = max(history)
    latest_ranked = countries(history[latest_year])
    if not latest_ranked:
        return None
    main = latest_ranked[0]
    current = {p.code: p.value for p in latest_ranked}
    peaks = {}
    for year in sorted(history):
        for p in countries(history[year]):
            if p.code != main.code and (p.code not in peaks or p.value >= peaks[p.code][0].value):
                peaks[p.code] = p, year
    gaps = {code: max(0, p.value - current.get(code, 0))
            for code, (p, _) in peaks.items()}
    extra = sum(gaps.values())
    result = {
        "value": float(extra),
        "ratio": float(min(1, extra / main.value)),
        "content_type": "calculated",
    }
    if extra:
        code = min(gaps, key=lambda code: (-gaps[code], code))
        p, peak_year = peaks[code]
        result["example"] = {
            "name": p.name, "latest": float(current.get(code, 0)),
            "peak": float(p.value), "peak_year": peak_year,
            "content_type": "calculated",
        }
    return result


def average_ranks(values):
    """Assign rank one to the greatest value and midranks to exact ties."""
    ordered = sorted(values, key=values.get, reverse=True)
    ranks = {}
    start = 1
    for _, keys in groupby(ordered, key=values.get):
        group = list(keys)
        rank = start + (len(group) - 1) / 2
        ranks.update(dict.fromkeys(group, rank))
        start += len(group)
    return ranks


def spearman(left, right):
    """Pearson correlation of midranks, reranked over the shared products."""
    common = sorted(left.keys() & right.keys())
    count = len(common)
    if count < 2:
        return None, count
    left = average_ranks({code: left[code] for code in common})
    right = average_ranks({code: right[code] for code in common})
    center = (count + 1) / 2
    xs = [left[code] - center for code in common]
    ys = [right[code] - center for code in common]
    denominator = sqrt(sum(x*x for x in xs) * sum(y*y for y in ys))
    if not denominator:
        return None, count
    rho = sum(x*y for x, y in zip(xs, ys)) / denominator
    return rho, count


def rank_spans(series):
    """Find rank changes among products present in every series in this group."""
    if len(series) < 2:
        return {}
    codes = sorted(set.intersection(*(set(values) for values in series)))
    if len(codes) < 2:
        return {}
    ranks = [average_ranks({code: values[code] for code in codes}) for values in series]
    return {code: max(rank[code] for rank in ranks) - min(rank[code] for rank in ranks)
            for code in codes}


def largest_rank_moves(spans):
    largest = max(spans.values(), default=0)
    return [{"hs6": code, "change": span} for code, span in spans.items()
            if span == largest and span > 0]


def sensitivity(products):
    """Compare latest-product scenario rankings and three HHI vintages."""
    recent_years = sorted({y["year"] for p in products for y in p["years"]})[-3:]
    data = {}
    series = []
    for label, growth in GROWTH.items():
        key = f"r_{label}"
        series.append({"key": key, "label": label, "year": None, "growth": float(growth)})
        data[key] = {p["hs6"]: p["years"][-1]["scenario"][label] for p in products
                     if p["years"] and p["years"][-1]["scenario"][label] is not None}
    for year in recent_years:
        key = f"hhi_{year}"
        series.append({"key": key, "label": "HHI", "year": year, "growth": None})
        data[key] = {p["hs6"]: y["hhi"] for p in products for y in p["years"] if y["year"] == year}

    correlations = []
    for left, right in combinations(data, 2):
        rho, count = spearman(data[left], data[right])
        correlations.append({"left": left, "right": right, "rho": rho, "count": count})

    scenario_spans = rank_spans([data[f"r_{label}"] for label in GROWTH])
    hhi_spans = rank_spans([data[f"hhi_{year}"] for year in recent_years])
    stability = None
    if scenario_spans:
        stability = "depends" if any(scenario_spans.values()) else "stable"
    return {
        "content_type": "calculated",
        "series": series,
        "correlations": correlations,
        "most_moved": {
            "scenario": largest_rank_moves(scenario_spans),
            "hhi": largest_rank_moves(hhi_spans),
        },
        "assumption_stability": stability,
    }
