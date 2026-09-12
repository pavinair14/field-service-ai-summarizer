# Field Service AI Summarizer

Customer-safe field-service summaries for the Northgate FM portal. The service
is deliberately safety-first: validation, redaction, evidence checks, and the
final publication gate remain deterministic even when optional model assistance
is configured.

## Run locally

Open PowerShell in the project root:

```powershell
cd C:\Users\p.muthumanickam\Documents\field-service-ai-summarizer-copy
```

Install the Python dependencies once:

```powershell
cd summarizer
python -m pip install -r requirements.txt
```

Keep the input report file in `data/service_reports.jsonl`. The summarizer
automatically reads that file and writes its results to `output/`.

Run the summarizer with the short command:

```powershell
python run_summarizer.py
```

The command processes all reports and updates these files:

- `output/results.jsonl`: one structured result per input record.
- `output/summaries.md`: Markdown customer-facing summaries grouped by asset and visit.

To read the summaries in PowerShell:

```powershell
Get-Content ..\output\summaries.md
```

Optional custom paths are supported when needed:

```powershell
python run_summarizer.py path\to\reports.jsonl --output path\to\results.jsonl --human-output path\to\summaries.md
```

Expected console output for the supplied dataset:

```text
{"count": 20, "statuses": {"complete": 16, "unclear": 2, "incomplete": 2}}
```

The CLI does not require a frontend, web server, or model credentials. It uses
the deterministic safe summarizer by default. If `PORT_URL` and `PORT_API_KEY`
are configured, model-assisted wording may be attempted, but deterministic
validation and the final publication gate remain authoritative.

The CLI processes every non-empty JSONL record independently and updates both
the structured JSONL result and human-readable summary output. A malformed
record receives its own safe result and cannot stop later records.

Customer summaries contain asset, visit date, findings, actions taken, parts
fitted, outstanding or recommended work, time on site, status, and a customer
caveat. Internal validation reasons, raw notes, technician IDs, and internal
report identifiers are not written to customer-facing output.

Status values are `complete`, `incomplete`, `unclear`, and `unsafe`. Missing or
contradictory evidence produces a caveat instead of a guess. Visit duration is
calculated from arrival/departure timestamps; a material mismatch is marked
unclear. A whole-hour duration is displayed as `2.0 hours`, and mixed durations
as readable hours and minutes.

## Safety boundary

Technician notes are untrusted data, never instructions. The pipeline extracts
only recommendation-bearing, non-sensitive sentences from notes. It blocks
category-level patterns for names, contact details, phone numbers, email
addresses, addresses, technician identifiers, keys, access locations, and
security codes. The model receives trusted facts only, and its asset, date, and
parts claims are checked against those facts. Invalid or unsafe model output
falls back to deterministic text.

## Verification

```powershell
cd summarizer
pytest -q
python run_summarizer.py
```

Current verification: 12 focused summarizer tests pass; the CLI processes all 20
supplied reports as 16 complete, 2 incomplete, and 2 unclear results. The
known cases are FSR-3005 and FSR-3006 for contradictions, FSR-3007 and
FSR-3008 for insufficient evidence, FSR-3003 and FSR-3014 for withheld
personal/security content, FSR-3009 for instruction-like notes, and FSR-3011
for long multi-asset recommendations.

The `output/` evidence set also contains canonical structured results, readable
summaries, a report-by-report review, a demonstration, and an effort
declaration. These artifacts are generated evidence, not runtime dependencies.

## Comparison and review outcome

The attached reference projects reinforced three changes made here: stream
JSONL with record-level continuation, keep safe deterministic output when a
model is unavailable, and record evidence without copying raw notes. A real
review issue found and corrected here was an over-broad security regex that
classified ordinary text such as `alarm cleared` as access information. The
final check now requires access context such as a code, pin, location, or key.

The open conflict decision is conservative: publish reliable safe context,
mark the result `unclear`, and request follow-up rather than choosing either
contradictory value. Retrieval is intentionally out of scope because the
supplied report is the source of truth.
