import json
from pathlib import Path
from collections.abc import Iterator

from .models import FieldServiceReport, InvalidReport


def read_report_records(
    file_path: str | Path,
) -> Iterator[tuple[int, FieldServiceReport | InvalidReport]]:
    """Yield one safe record result per non-empty JSONL line."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            raw_report: object = None
            try:
                raw_report = json.loads(line)
                report = FieldServiceReport.model_validate(raw_report)
                yield line_number, report
            except (json.JSONDecodeError, TypeError, ValueError):
                raw_id = "unknown"
                raw_asset = "Unknown asset"
                if isinstance(raw_report, dict):
                    raw_id = str(raw_report.get("report_id") or "unknown")
                    raw_asset = str(raw_report.get("asset") or "Unknown asset")
                yield line_number, InvalidReport(
                    report_id=raw_id,
                    asset=raw_asset,
                    reason="The report could not be validated for customer publication.",
                )


def load_valid_reports(
    file_path: str | Path = Path(__file__).parent / "service_reports.jsonl"
) -> list[FieldServiceReport]:
    """Load only valid reports for single-record lookup endpoints."""
    return [
        record
        for _, record in read_report_records(file_path)
        if isinstance(record, FieldServiceReport)
    ]