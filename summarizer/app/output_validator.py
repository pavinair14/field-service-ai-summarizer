import re

from pydantic import BaseModel, Field

from .summarizer import CustomerSummary


class OutputValidation(BaseModel):
    safe_to_publish: bool
    warnings: list[str] = Field(default_factory=list)


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE_PATTERN = re.compile(
    r"(?<![\d-])"
    r"(?:\+?\d{1,3}[\s.-])?"
    r"(?:\(?\d{2,5}\)?[\s.-])"
    r"\d{3,8}"
    r"(?![\d-])"
)

ACCESS_CODE_PATTERN = re.compile(
    r"\b(?:access|entry|security|alarm|door|gate)\s+(?:code|pin|number|location|details?)\b"
    r"|\b(?:plant\s*[- ]?room|spare\s+key|key\s+location)\b",
    re.IGNORECASE,
)

TECHNICIAN_ID_PATTERN = re.compile(
    r"\bT-\d+\b",
    re.IGNORECASE,
)

NAME_PATTERN = re.compile(
    r"\b(?:site contact|facilities manager|manager|contact|engineer)\s+(?:is|was|:)?\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+",
)

ADDRESS_PATTERN = re.compile(
    r"\b(?:home|personal)\s+address\b|\b\d{1,5}\s+[A-Z][A-Za-z]+\s+(?:Lane|Road|Street|Court|Drive|Avenue|Way|Close|Place|Road|Rd|St|Ave)\b"
)


def check_summary_safety(
    summary: CustomerSummary,
) -> OutputValidation:
    """Check every customer-facing field for prohibited content before publication."""
    text = " ".join(
        [
            summary.asset,
            summary.visit_date,
            summary.findings,
            summary.actions_taken,
            " ".join(summary.parts_fitted),
            summary.outstanding_or_recommended,
            summary.time_on_site,
            summary.caveat,
        ]
    )

    warnings = []

    if EMAIL_PATTERN.search(text):
        warnings.append(
            "Customer summary contains an email address."
        )

    if PHONE_PATTERN.search(text):
        warnings.append(
            "Customer summary contains a phone number."
        )

    if ACCESS_CODE_PATTERN.search(text):
        warnings.append(
            "Customer summary contains physical-security information."
        )

    if TECHNICIAN_ID_PATTERN.search(text):
        warnings.append(
            "Customer summary contains a technician or internal identifier."
        )

    if NAME_PATTERN.search(text):
        warnings.append("Customer summary contains a personal name.")

    if ADDRESS_PATTERN.search(text):
        warnings.append("Customer summary contains an address.")

    return OutputValidation(
        safe_to_publish=len(warnings) == 0,
        warnings=warnings,
    )