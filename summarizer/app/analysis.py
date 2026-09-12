from pydantic import BaseModel, Field
from .models import FieldServiceReport


class ReportAnalysis(BaseModel):
    report_id: str
    duration_conflict: bool = False
    parts_conflict: bool = False
    insufficient_information: bool = False
    warnings: list[str] = Field(default_factory=list)
    status: str = "complete"


def get_visit_duration_hours(report: FieldServiceReport) -> float:
    """Calculate elapsed visit time from the trusted arrival and departure timestamps."""
    elapsed_time = (report.departed_at - report.arrived_at).total_seconds() / 3600.0
    return elapsed_time


def assess_report_quality(report: FieldServiceReport) -> ReportAnalysis:
    """Classify duration, parts, and evidence-quality problems without guessing."""
    warnings: list[str] = []

    elapsed_hours = get_visit_duration_hours(report)

    if elapsed_hours < 0 or report.stated_duration_hours < 0:
        warnings.append("The visit timestamps do not describe a valid interval.")

    duration_conflict = abs(elapsed_hours - report.stated_duration_hours) > 0.1

    if duration_conflict:
        warnings.append(
            "The stated duration does not match the recorded arrival and departure times."
        )

    parts_conflict = bool(report.parts_used) and (
        "no parts" in report.resolution.lower()
        or "no parts required" in report.resolution.lower()
    )

    if parts_conflict:
        warnings.append(
            "The parts listed in the report do not match with the resolution."
        )

    insufficient_information = (
        len(report.resolution.strip()) < 15
        and len(report.technician_notes.strip()) < 15
    )

    if insufficient_information:
        warnings.append(
            "The report does not contain sufficient information for a reliable summary."
        )

    status = "complete"

    if insufficient_information or elapsed_hours < 0 or report.stated_duration_hours < 0:
        status = "incomplete"
    elif duration_conflict or parts_conflict:
        status = "unclear"


    return ReportAnalysis(
        report_id=report.report_id,
        duration_conflict=duration_conflict,
        parts_conflict=parts_conflict,
        insufficient_information=insufficient_information,
        warnings=warnings,
        status=status,
    )