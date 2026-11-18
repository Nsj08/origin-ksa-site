"""The owner approval boundary must withstand edits, revocations and malformed rows."""
import copy
import csv
import json
from pathlib import Path
import pytest
from scripts.review import FIELDS, ledger, project

DATA = Path(__file__).parent / 'fixtures' / 'review-rows.json'


def test_pending_then_approved_then_revoked():
    f=json.loads(DATA.read_text())
    pending, proposed, candidate = f['products'], f['maker'], f['match']
    assert project(copy.deepcopy(pending),[proposed],[candidate]) == pending
    approved = project(copy.deepcopy(pending),[dict(proposed,approved='yes')],[dict(candidate,approved='yes')])
    assert approved[0]['makers'][0]['source'] == proposed['source']
    assert approved[0]['lcgpa']['status'] == 'listed'
    assert project(approved,[dict(proposed,approved='no')],[candidate]) == pending


def test_approval_is_literal_and_list_evidence_is_official(tmp_path):
    case=json.loads(DATA.read_text())
    def write(name,row):
        with (tmp_path/(name+'.csv')).open('w',newline='') as target:
            writer=csv.DictWriter(target,fieldnames=FIELDS)
            writer.writeheader()
            writer.writerow(row)
    write('makers',dict(case['maker'],approved='YES'))
    with pytest.raises(ValueError,match='approval'): ledger('makers',tmp_path)
    write('lcgpa_matches',dict(case['match'],source='https://example.invalid/document'))
    with pytest.raises(ValueError,match='LCGPA'): ledger('lcgpa_matches',tmp_path)


def test_duplicate_approval_fails_closed():
    case=json.loads(DATA.read_text())
    approved=dict(case['match'],approved='yes')
    with pytest.raises(ValueError,match='Multiple'):
        project(case['products'],[],[approved,approved])
