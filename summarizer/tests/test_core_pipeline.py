from datetime import datetime
import json
from pathlib import Path

from app.analysis import assess_report_quality
from app.models import FieldServiceReport
from app.report_loader import load_valid_reports, read_report_records
from app.safety import assess_report_safety
from app.trusted_facts import create_trusted_facts


def make_report(**overrides):
    data = {
        "report_id": "TEST-001",
        "asset": "AHU-01",
        "technician_id": "T-001",
        "arrived_at": datetime(2026, 1, 10, 9, 0),
        "departed_at": datetime(2026, 1, 10, 11, 0),
        "stated_duration_hours": 2.0,
        "parts_used": ["Filter"],
        "resolution": "Replaced blocked filter and restored normal operation.",
        "technician_notes": "Recommend checking filter condition during the next visit.",
    }
    data.update(overrides)
    return FieldServiceReport(**data)


def get_trusted_facts(report):
    return create_trusted_facts(
        report,
        assess_report_quality(report),
        assess_report_safety(report),
    )


def test_report_model_and_supplied_dataset_load():
    report = make_report()
    assert report.asset == "AHU-01"

    reports_path = Path(__file__).parents[2] / "data" / "service_reports.jsonl"
    reports = load_valid_reports(reports_path)
    assert len(reports) == 20
    assert reports[-1].asset == "Pump P-03"


def test_quality_assessment_handles_normal_conflicting_and_sparse_reports():
    assert assess_report_quality(make_report()).status == "complete"

    duration_result = assess_report_quality(
        make_report(departed_at=datetime(2026, 1, 10, 12, 0))
    )
    assert duration_result.status == "unclear"
    assert duration_result.duration_conflict is True

    parts_result = assess_report_quality(
        make_report(
            parts_used=["PART-1"],
            resolution="Inspection only, no parts required this visit.",
        )
    )
    assert parts_result.status == "unclear"
    assert parts_result.parts_conflict is True

    sparse_result = assess_report_quality(
        make_report(resolution="Attended site.", technician_notes="See job sheet.")
    )
    assert sparse_result.status == "incomplete"
    assert sparse_result.insufficient_information is True


def test_trusted_facts_withhold_conflicting_parts_and_sensitive_values():
    facts = get_trusted_facts(
        make_report(
            parts_used=["PART-1"],
            resolution="Inspection only, no parts required this visit.",
            technician_notes=(
                "Contact engineer at john@example.com. "
                "Plant room access code is 123456."
            ),
        )
    )
    assert facts.parts_fitted == []
    assert "john@example.com" not in str(facts.caveats)
    assert "123456" not in str(facts.caveats)


def test_malformed_json_gets_one_record_and_later_records_continue(tmp_path):
    input_path = tmp_path / "reports.jsonl"
    input_path.write_text(
        json.dumps(make_report().model_dump(mode="json"))
        + "\nnot valid json\n"
        + json.dumps(make_report(report_id="TEST-002").model_dump(mode="json"))
        + "\n",
        encoding="utf-8",
    )

    records = list(read_report_records(input_path))
    assert len(records) == 3
    assert records[0][1].report_id == "TEST-001"
    assert records[1][1].report_id == "unknown"
    assert records[2][1].report_id == "TEST-002"
