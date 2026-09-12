# Contributor Guidance

- Treat `spec.md`, `plan.md`, `tasks.md`, `criteria_checklist.md`, and
  `data/summary_requirements.md` as the behavioral contract.
- Never publish raw `technician_notes`, technician IDs, personal data, access
  details, or internal validation reasons.
- Keep deterministic validation and the final publication gate authoritative;
  model output is optional wording assistance only.
- Preserve one-result-per-record batch behavior, including malformed JSONL.
- Use the existing Python tests and CLI verification command before
  describing a change as complete.
- Do not add credentials, generated output containing sensitive source data, or
  unrelated refactors.