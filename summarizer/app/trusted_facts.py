from pydantic import BaseModel, Field

from .analysis import ReportAnalysis
from .models import FieldServiceReport
from .safety import SafetyAnalysis, get_safe_findings, get_safe_recommendations


class TrustedFacts(BaseModel):
    report_id: str = Field(..., description="The unique identifier for the field service report.")
    asset: str = Field(..., description="The asset associated with the field service report.")
    visit_date: str = Field(..., description="The date of the field service visit in YYYY-MM-DD format.")

    findings: str = Field(..., description="A summary of the findings from the field service report.")
    actions_taken: str = Field(..., description="A summary of the actions taken during the field service visit.")
    parts_fitted: list[str] = Field(default_factory=list, description="A list of parts fitted during the field service visit.")
    outstanding_or_recommended: str
    time_on_site: str

    status:str
    caveats: list[str] = Field(default_factory=list)

def create_trusted_facts(
    report: FieldServiceReport,
    analysis: ReportAnalysis,
    safety: SafetyAnalysis,
) -> TrustedFacts:
    """Construct the allowlisted facts that may reach wording or publication stages."""
    caveats = list(analysis.warnings)

    if safety.contains_personal_information:
        caveats.append("Personal contact information was detected and must not be published.")

    if safety.contains_physical_security_information:
        caveats.append("Physical-security information was detected and must not be published.")

    if safety.contains_technical_information:
        caveats.append("Technician or internal identifiers must not be published.")

    elapsed_hours = (report.departed_at - report.arrived_at).total_seconds() / 3600

    if analysis.duration_conflict or elapsed_hours < 0:
        time_on_site = "Unclear due to conflicting duration information"
    else:
        total_minutes = round(elapsed_hours * 60)
        if total_minutes % 60 == 0:
            time_on_site = f"{total_minutes / 60:.1f} hours"
        else:
            time_on_site = f"{total_minutes // 60} hours {total_minutes % 60:02d} minutes"

    outstanding = get_safe_recommendations(report.technician_notes)
    findings = get_safe_findings(report.technician_notes)


    return TrustedFacts(
        report_id=report.report_id,
        asset=report.asset,
        visit_date=report.arrived_at.date().isoformat(),
        findings=findings or "The reported issue was assessed.",
        actions_taken=report.resolution,
        parts_fitted=[] if analysis.parts_conflict else report.parts_used,
        outstanding_or_recommended=outstanding or "No outstanding work or recommendations recorded.",
        time_on_site=time_on_site,
        status=analysis.status,
        caveats=caveats,
    )