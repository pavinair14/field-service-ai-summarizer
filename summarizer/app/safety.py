import re
from typing import Callable, ClassVar

from pydantic import BaseModel, Field

from .models import FieldServiceReport


class SafetyAnalysis(BaseModel):
    report_id: str = Field(..., description="The unique identifier for the field service report.")
    contains_personal_information: bool = Field(..., description="Indicates whether the report contains personal information.")
    contains_physical_security_information: bool = Field(..., description="Indicates whether the report contains physical security information.")
    contains_technical_information: bool = Field(..., description="Indicates whether the report contains technical information.")
    warnings: list[str] = Field(..., description="A list of warnings generated during the safety analysis.")

    EMAIL_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    PHONE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)")
    SECURITY_CODE_PATTERNS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(r"\b(?:access|entry|security|alarm|door|gate|site)\s+(?:code|pin|number)\b", re.IGNORECASE),
        re.compile(r"\b(?:plant(?:[- ]?room)|key(?:[- ]?location)?|spare\s+key)\b", re.IGNORECASE),
        re.compile(r"\b(?:plant(?:[- ]?room)?\s+access\s+(?:code|pin|number)|door\s+(?:code|pin|number)|alarm\s+(?:code|pin|number))\b", re.IGNORECASE),
    ]
    TECHNICIAN_ID_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"\bT-\d+\b", re.IGNORECASE)
    PERSONAL_NAME_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"\b(?:site contact|facilities manager|manager|contact|engineer)\s+(?:is|was|:)?\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+",
    )
    ADDRESS_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"\b(?:home|personal)\s+address\b|\b\d{1,5}\s+[A-Z][A-Za-z]+\s+(?:Lane|Road|Street|Court|Drive|Avenue|Way|Close|Place|Road|Rd|St|Ave)\b"
    )

    @classmethod
    def detect_physical_security_information(cls, text: str) -> bool:
        """Detect category-level access and physical-security language in untrusted text."""
        for pattern in cls.SECURITY_CODE_PATTERNS:
            if pattern.search(text):
                return True
        return False

    @classmethod
    def detect_personal_information(cls, text: str) -> bool:
        """Detect contact, name, or address categories without relying on sample values."""
        return bool(
            cls.EMAIL_PATTERN.search(text)
            or cls.PHONE_PATTERN.search(text)
            or cls.PERSONAL_NAME_PATTERN.search(text)
            or cls.ADDRESS_PATTERN.search(text)
        )

    @classmethod
    def create_from_report(cls, report: FieldServiceReport) -> "SafetyAnalysis":
        """Create operator-only safety flags without copying sensitive source text."""
        text = " ".join([report.asset, report.resolution, report.technician_notes])

        warnings: list[str] = []

        contains_personal_information = bool(
            cls.detect_personal_information(text)
        )
        contains_physical_security_information = cls.detect_physical_security_information(text)
        contains_technical_information = bool(report.technician_id or cls.TECHNICIAN_ID_PATTERN.search(text))

        if contains_personal_information:
            warnings.append("Personal contact information detected.")
        if contains_physical_security_information:
            warnings.append("Physical security information detected.")
        if contains_technical_information:
            warnings.append("Technical/internal identifier detected.")

        return cls(
            report_id=report.report_id,
            contains_personal_information=contains_personal_information,
            contains_physical_security_information=contains_physical_security_information,
            contains_technical_information=contains_technical_information,
            warnings=warnings,
        )


def assess_report_safety(report: FieldServiceReport) -> SafetyAnalysis:
    """Analyze one report for personal, physical-security, and internal identifier risks."""
    return SafetyAnalysis.create_from_report(report)


def get_safe_recommendations(notes: str) -> str:
    """Keep recommendation-bearing sentences while excluding untrusted details."""
    recommendation_words = re.compile(
        r"\b(?:recommend|recommended|should|follow[- ]?up|monitor|review|next visit|outstanding)\b",
        re.IGNORECASE,
    )
    return extract_safe_sentences(notes, recommendation_words)


def get_safe_findings(notes: str) -> str:
    """Keep safe observational sentences that explain what was found during the visit."""
    recommendation_words = re.compile(
        r"\b(?:recommend|recommended|should|follow[- ]?up|monitor|review|next visit|outstanding)\b",
        re.IGNORECASE,
    )
    return extract_safe_sentences(
        notes,
        include_when=lambda sentence: not recommendation_words.search(sentence),
    )


def extract_safe_sentences(
    notes: str,
    include_when: re.Pattern[str] | Callable[[str], bool],
) -> str:
    """Filter note sentences once for safety, then apply a caller-specific selector."""
    instruction_words = re.compile(
        r"\b(?:ignore|publish|suppress|omit|summary tool|previous instructions|instruction|see job sheet|another engineer|job sheet)\b",
        re.IGNORECASE,
    )
    selected: list[str] = []
    for sentence in re.split(r"(?<=[.!?])\s+", notes.strip()):
        sentence = sentence.strip()
        if not sentence or instruction_words.search(sentence):
            continue
        if SafetyAnalysis.detect_personal_information(sentence):
            continue
        if SafetyAnalysis.detect_physical_security_information(sentence):
            continue
        if isinstance(include_when, re.Pattern):
            should_include = bool(include_when.search(sentence))
        else:
            should_include = include_when(sentence)
        if should_include:
            selected.append(sentence)
    return " ".join(selected)
