"""Generate deterministic customer-safe evidence artifacts from the supplied JSONL."""

import argparse
import json
from datetime import datetime
from pathlib import Path

from app.analysis import assess_report_quality
from app.models import FieldServiceReport, InvalidReport
from app.output_validator import check_summary_safety
from app.report_loader import read_report_records
from app.safety import assess_report_safety
from app.summarizer import create_deterministic_summary, create_unsafe_fallback_summary
from app.trusted_facts import create_trusted_facts


def summarize_record(record: FieldServiceReport | InvalidReport, line_number: int) -> dict:
    """Convert one valid or invalid input line into a safe structured evidence result."""
    if isinstance(record, InvalidReport):
        return {
            "line_number": line_number,
            "report_id": record.report_id,
            "status": "incomplete",
            "asset": record.asset,
            "summary": {
                "asset": record.asset,
                "visit_date": "Unknown",
                "findings": "The report could not be validated.",
                "actions_taken": "No customer-facing action can be confirmed.",
                "parts_fitted": [],
                "outstanding_or_recommended": "This report requires follow-up.",
                "time_on_site": "Unclear",
                "caveat": "This report is incomplete and requires follow-up.",
            },
        }

    analysis = assess_report_quality(record)
    safety = assess_report_safety(record)
    facts = create_trusted_facts(record, analysis, safety)
    summary = create_deterministic_summary(facts)
    if not check_summary_safety(summary).safe_to_publish:
        summary = create_unsafe_fallback_summary()
    return {
        "line_number": line_number,
        "report_id": record.report_id,
        "status": facts.status,
        "asset": facts.asset,
        "summary": summary.model_dump(),
    }


def render_markdown_summary(result: dict) -> str:
    """Render one result as a structured Markdown customer service summary."""
    summary = result["summary"]
    report_reference = result.get("report_id", "Unknown")
    visit_date = _format_visit_date(summary["visit_date"])
    time_on_site = _format_duration(summary["time_on_site"])
    follow_up = summary["outstanding_or_recommended"]
    if follow_up == "No outstanding work or recommendations recorded.":
        follow_up = "No further action is currently recorded."

    parts = summary["parts_fitted"]
    parts_section = "\n".join(f"- {part}" for part in parts) or "No parts were fitted."
    caveat_section = (
        f"\n### Status note\n\n{summary['caveat']}\n"
        if summary["caveat"] and result["status"] != "complete"
        else ""
    )
    return "\n".join(
        [
            f"## {summary['asset']}",
            "",
            f"**Report reference:** {report_reference}  ",
            f"**Visit date:** {visit_date}",
            "",
            "### Summary",
            "",
            f"{summary['findings']} {summary.get('actions_taken', summary['findings'])}",
            "",
            "### Work completed",
            "",
            summary.get("actions_taken", summary["findings"]),
            "",
            "### Parts used",
            "",
            parts_section,
            "",
            "### Follow-up",
            "",
            follow_up,
            "",
            "### Time on site",
            "",
            time_on_site,
            caveat_section,
            "",
        ]
    )


def _format_visit_date(value: str) -> str:
    """Format an ISO visit date in plain customer-facing day-month-year wording."""
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%d %B %Y")
    except ValueError:
        return value


def _format_duration(value: str) -> str:
    """Normalize duration grammar without changing an unclear duration statement."""
    if value == "0 hours 30 minutes":
        return "30 minutes"
    if value.startswith("0 hours "):
        return value.removeprefix("0 hours ")
    if value.startswith("1 hours "):
        return value.replace("1 hours ", "1 hour ", 1)
    if value == "1.0 hours":
        return "1 hour"
    return value


def main() -> int:
    """Run the deterministic batch pipeline and write JSONL plus human-readable outputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    project_root = Path(__file__).resolve().parents[1]
    parser.add_argument(
        "input",
        type=Path,
        nargs="?",
        default=project_root / "data" / "service_reports.jsonl",
        help="Input JSONL report file (default: ../data/service_reports.jsonl)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=project_root / "output" / "results.jsonl",
        help="Structured JSONL output (default: ../output/results.jsonl)",
    )
    parser.add_argument(
        "--human-output",
        type=Path,
        default=project_root / "output" / "summaries.md",
        help="Markdown customer summaries (default: ../output/summaries.md)",
    )
    args = parser.parse_args()

    results = [
        summarize_record(record, line_number)
        for line_number, record in read_report_records(args.input)
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.human_output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "".join(json.dumps(result, ensure_ascii=True) + "\n" for result in results),
        encoding="utf-8",
    )
    args.human_output.write_text(
        "# Customer Service Summaries\n\n"
        + "\n".join(render_markdown_summary(result) for result in results),
        encoding="utf-8",
    )

    counts: dict[str, int] = {}
    for result in results:
        counts[result["status"]] = counts.get(result["status"], 0) + 1
    print(json.dumps({"count": len(results), "statuses": counts}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
