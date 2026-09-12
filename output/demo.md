# Demonstration

## 1. Run the summarizer

```powershell
cd summarizer
python run_summarizer.py ..\data\service_reports.jsonl `
  -o ..\output\results.jsonl `
  --human-output ..\output\summaries.md
```

## 2. Review a normal report

Open `output/summaries.md` and find the Chiller CH-04 visit. It contains the
visit date, filter-drier action, fitted part, and calculated 2 hours 30 minutes
on site. No technician ID or raw note is displayed.

## 3. Review a safety-sensitive report

Find the Boiler BLR-02 result. The safe ignition-electrode outcome remains
available, while personal and physical-security details from the internal note
do not appear in the customer view.

## 4. Review uncertainty

Find Chiller CH-01 or Cooling tower CT-02. The result is `unclear` and asks
for follow-up rather than silently choosing between conflicting duration or
parts evidence.

## 5. Verify batch behavior

```powershell
cd summarizer
python run_summarizer.py ..\data\service_reports.jsonl `
  -o ..\output\results.jsonl `
  --human-output ..\output\summaries.md
```

Observed result: 20 records processed, 16 complete, 2 incomplete, and 2
unclear. A model is not required for the demonstration.
