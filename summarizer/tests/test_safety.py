from datetime import datetime

from app.models import FieldServiceReport
from app.output_validator import check_summary_safety
from app.safety import assess_report_safety
from app.summarizer import CustomerSummary


def make_report(**overrides):
    data = {
        "report_id": "FSR-123",
        "asset": "Asset 1",
        "technician_id": "T-123456",
        "arrived_at": datetime(2023, 1, 1, 8, 0),
        "departed_at": datetime(2023, 1, 1, 10, 0),
        "stated_duration_hours": 2.0,
        "parts_used": [],
        "resolution": "Resolution 1",
        "technician_notes": "Technician notes 1",
    }
    data.update(overrides)
    return FieldServiceReport(**data)


def make_summary(**overrides):
    data = {
        "asset": "AHU-01",
        "visit_date": "2026-01-10",
        "findings": "The filter was blocked.",
        "actions_taken": "The filter was replaced.",
        "parts_fitted": ["Filter"],
        "outstanding_or_recommended": "Check the filter condition during the next visit.",
        "time_on_site": "2.0 hours",
        "caveat": "",
    }
    data.update(overrides)
    return CustomerSummary(**data)


def test_safety_detects_personal_and_security_categories():
    assert assess_report_safety(
        make_report(technician_notes="Contact john.doe@example.com")
    ).contains_personal_information
    assert assess_report_safety(
        make_report(technician_notes="Call +1 (555) 123-4567")
    ).contains_personal_information
    assert assess_report_safety(
        make_report(technician_notes="Home address: 22 Cedar Lane.")
    ).contains_personal_information
    assert assess_report_safety(
        make_report(technician_notes="The access code is 1234")
    ).contains_physical_security_information


def test_clean_report_has_no_personal_or_security_flags():
    result = assess_report_safety(make_report(technician_id=""))
    assert result.contains_personal_information is False
    assert result.contains_physical_security_information is False
    assert result.contains_technical_information is False


def test_supplied_sensitive_report_is_detected():
    result = assess_report_safety(
        make_report(
            technician_notes=(
                "Site contact is Margaret Oyelaran, mobile 07700 900412. "
                "Spare key held at 14 Alderman Court."
            )
        )
    )
    assert result.contains_personal_information
    assert result.contains_physical_security_information


def test_clean_summary_is_publishable():
    result = check_summary_safety(make_summary())
    assert result.safe_to_publish is True
    assert result.warnings == []


def test_publication_gate_rejects_sensitive_summary_content():
    for findings, warning_word in [
        ("Contact john@example.com.", "email"),
        ("Call 01234 567890.", "phone"),
        ("The plant room access code is 123456.", "security"),
        ("Technician T-123 completed the work.", "technician"),
        ("Visit the home address at 22 Cedar Lane.", "address"),
    ]:
        result = check_summary_safety(make_summary(findings=findings))
        assert result.safe_to_publish is False
        assert any(warning_word in warning.lower() for warning in result.warnings)
