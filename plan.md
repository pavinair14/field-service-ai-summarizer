# Project Plan

## 1. Objective

Build a small CLI service summary application that reads field-service reports, applies strict customer-safe summarisation rules, and writes approved structured and readable output files.

## 2. Architectural approach

### Processing model

- Use a hybrid pipeline: deterministic validation and safety gates around an LLM-assisted extraction and summarisation step.
- Send the LLM only validated, sanitized, structured facts; never send unrestricted technician notes or raw sensitive content.
- Use the same core pipeline for CLI output and tests so results are consistent in exports and verification.
- Process JSONL records one at a time so one malformed or unsafe record does not prevent later reports from being assessed.

### Python CLI

- Load `data/service_reports.jsonl` and process it through one batch command.
- Parse each JSON object and apply a summarisation pipeline that:
  - validates required fields,
  - handles malformed JSON and invalid records with a record-level incomplete/error result,
  - calculates time on site from valid arrival and departure timestamps,
  - compares calculated duration with stated duration and flags a material mismatch,
  - treats resolution and parts as primary evidence for completed work,
  - extracts safe observational findings from technician notes without copying unrestricted notes,
  - withholds parts when the parts list conflicts with an inspection-only resolution,
  - applies category-based redaction for personal and security-sensitive data,
  - suppresses or blocks unsafe content from any field, including free-text notes,
  - normalises conflicting or incomplete inputs,
  - sends safe facts to a configured LLM for structured extraction and plain-language wording,
  - validates the LLM response and falls back to a deterministic caveat when the request fails or returns unsafe/invalid content,
  - creates customer-safe summaries.
- Write structured JSONL containing only customer-safe output: the asset reference, visit date, findings, actions taken, parts fitted, outstanding items or recommendations, time on site, summary text, and status metadata for completed/incomplete/unclear cases. Do not expose raw source fields.
- Keep operator-only validation reasons separate from customer-facing text and never echo raw notes in diagnostics.
- Keep model configuration in environment variables, exclude credentials from source control, and support deterministic tests without a live model call.

## 3. Core design decisions

### 3.1 Safe-by-default summarisation

The backend should treat redaction and safety as the highest-priority rules. It should implement allowlisted content generation: only customer-safe facts are included and all personal or access-related details are excluded.

### 3.2 Category-based protection, not exact-string matching

The implementation must protect categories of sensitive information, not just the exact values seen in the sample dataset. This includes personal names, phone numbers, emails, addresses, key locations, plant-room information, door codes, alarm codes, and other physical security data.

### 3.3 Conservative handling of uncertainty

When a report contains conflicting or missing information, the system should not guess. It should emit a clear status such as “incomplete” or “needs follow-up,” rather than inventing a confident summary.

### 3.4 Explicit conflict policy

The specification leaves open the exact preference order for conflicting fields. The implementation will document and apply a consistent policy:

1. Prefer objective, customer-safe observations from the resolution and technician notes over incomplete metadata.
2. Prefer the most recent explicit field that clearly describes the actual work performed or asset status.
3. If the contradiction still prevents a reliable summary, publish an incomplete/unclear status and customer-facing caveat instead of guessing.

### 3.5 Prompt-injection resistance

The tool must treat technician notes as untrusted input. Notes that instruct the tool to suppress information or change the summary must be ignored as instructions and used only as signals to review the content for safety.

### 3.6 Constrained LLM assistance

This is not a retrieval problem. The source information is already available in the report dataset. The LLM is used only to organise sanitized facts into findings, actions, parts, recommendations, and plain customer language. It must return a strict structured response, use only supplied facts, and never decide the publication policy.

### 3.7 Record-level failure isolation

Malformed JSON, missing required fields, invalid timestamps, and unsafe or contradictory evidence must produce a safe record-level result and allow the remaining input records to be processed. The batch must not silently discard a report or abort before later reports are checked.

### 3.8 Final publication assertion

Before returning or exporting a result, validate that customer-facing fields contain no prohibited categories and that raw technician notes have not been copied into the output. A failed assertion must prevent publication and produce an incomplete/unsafe status.

## 4. Data flow

1. Read the JSONL report set.
2. Parse and validate each record independently, preserving its asset reference where available.
3. Calculate duration from arrival/departure timestamps and compare it with stated duration using a documented tolerance.
4. Extract asset, date, findings, actions/resolution, parts, recommendations, notes, and duration.
5. Filter and redact unsafe material from the notes and any related fields by category.
6. Decide whether the report is complete, incomplete, contradictory, or unsafe to publish before calling the model.
7. Send only the sanitized payload to the LLM with instructions to return structured JSON and never follow instructions contained in report data.
8. Validate the model response for schema, supported facts, prohibited content, and unsupported claims; use a deterministic caveat if validation fails.
9. Compose the final safe summary in plain customer language, preserving the required sections: asset/date, findings, actions taken, parts fitted, outstanding items or recommendations, and time on site.
10. Run the final publication assertion before export.
11. Write the approved summaries to the requested JSONL and Markdown output files.

## 5. Risks and mitigations

### Risk: unsafe publication from free-text notes

Mitigation: maintain a category-based safety filter for names, phone numbers, emails, physical addresses, door codes, alarm codes, access locations, and other physical security details. Apply the filter before finalising the summary.

### Risk: false confidence on incomplete data

Mitigation: if fields disagree or are missing, return a “report incomplete / follow-up required” status rather than inventing a value.

### Risk: prompt-injection from free text

Mitigation: treat technician notes as untrusted data and never let embedded instructions override the summary policy.

### Risk: required information is omitted from an otherwise safe summary

Mitigation: validate the structured response against the required output sections and mark the report incomplete when reliable source information is missing, rather than filling gaps with assumptions.

### Risk: a single malformed record prevents batch verification

Mitigation: isolate parsing and validation failures per record, emit a non-publishing result with a generic status, and continue processing later JSONL lines.

### Risk: model output contains unsupported or sensitive content

Mitigation: sanitize before the model call, require structured JSON, validate every returned field, run a final forbidden-content assertion, and publish a caveat if any gate fails.

### Risk: model service is unavailable or misconfigured

Mitigation: keep credentials in environment variables, return a record-level follow-up result, and retain deterministic test doubles so validation does not depend on network access.

## 6. Delivery phases

1. Define the CLI output contract and structured summary schema, including the asset reference, all required summary sections, status, and customer-facing caveat fields.
2. Implement the backend summarisation pipeline and data validation.
3. Implement category-based security redaction and prompt-injection safeguards before model calls.
4. Implement the LLM client, structured prompt, response validation, and deterministic fallback behavior.
5. Implement the deterministic CLI and output writers.
6. Run verification against the provided 20 reports.
7. Add focused tests for normal reports, missing fields, malformed JSONL, duration conflicts, parts conflicts, personal/security data, instruction-like notes, recommendations, long reports, model failures, invalid model responses, and continuation after an invalid record.
8. Review the edge cases, especially access details, conflicting fields, incomplete reports, and model output safety.

## 7. Acceptance criteria for the plan

The project will be considered on track when:

- the backend can process the input JSONL reports,
- the output is customer-safe and includes asset, visit date, findings, actions taken, parts fitted when reliable, outstanding items or recommendations, and time on site when available,
- the CLI writes structured JSONL and readable Markdown summaries cleanly,
- material conflicts and incomplete data are handled conservatively,
- redaction is category-based and not limited to exact values,
- prompt-injection instructions in notes do not override the policy,
- the output files do not expose raw notes, internal identifiers, or hidden source fields,
- malformed or unsafe records produce isolated non-publishing results without stopping later records,
- the LLM receives only sanitized, structured facts and cannot override the publication policy,
- invalid, unavailable, or unsafe LLM responses produce a safe deterministic caveat,
- final output assertions prevent prohibited content or raw notes from being published,
- focused tests verify the customer-facing text as well as internal status flags,
- and the handling of incomplete or conflicting data is explicitly documented and consistent with the specification's conflict policy.

## 8. AI-augmented development and review

AI assistance may be used for implementation suggestions, test ideas, debugging, code review, and generated-summary review, but developer review remains the acceptance authority. Each suggestion must be checked for:

1. Correctness against `spec.md`
2. Alignment with the customer-facing intent
3. Security and safe publication
4. Performance and unnecessary model/API calls
5. Maintainability and testability

The implementation process must record at least one real issue found in AI-generated code or output, the correction applied, and the re-test or review evidence confirming the correction.

## 9. Retrieval decision

Retrieval-augmented generation is not required for the current scope. The supplied field report is the source of truth and there is no acceptance criterion requiring manuals, policies, or another external knowledge base. Adding retrieval would introduce infrastructure and testing complexity without improving the current required behavior.

If external maintenance manuals or company policies become part of a future scope, retrieval can be added behind the same deterministic safety and publication boundary.

## 10. Delivery evidence

Before submission, the project should include evidence of:

- batch execution against all 20 supplied reports;
- normal, safety-sensitive, prompt-injection, contradictory, and incomplete cases;
- review and correction of at least one real AI-generated issue;
- the first four commits and their order, timestamps, and file contents;
- the actual human effort and AI assistance used during development;
- a short demonstration covering report selection, summary generation, and at least one safety or uncertainty outcome.
