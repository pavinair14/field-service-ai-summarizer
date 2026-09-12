# Implementation Tasks

## 1. Establish the repository and interfaces

- [ ] Define the CLI command for batch summarisation and output files.
- [ ] Define the structured response schema with only customer-safe fields: asset reference, visit date, findings, actions taken, parts fitted, outstanding items or recommendations, time on site, summary text, and status.
- [ ] Keep operator-only reason codes separate from customer-facing output; never return raw notes or internal report identifiers.
- [ ] Define LLM configuration through environment variables and ensure credentials are excluded from source control and logs.
- [ ] Define model statuses and fallback behavior for unavailable, invalid, or unsafe LLM responses.

## 2. Parse and validate input records

- [ ] Read `data/service_reports.jsonl` one line at a time.
- [ ] Parse each JSON object and continue after malformed JSON.
- [ ] Validate required fields, types, and the asset reference without echoing invalid raw content.
- [ ] Parse arrival and departure timestamps and reject impossible or incomplete intervals.
- [ ] Calculate time on site from valid timestamps.
- [ ] Compare calculated time with `stated_duration_hours` using a documented material-difference tolerance.
- [ ] Ensure every input record receives exactly one result, including incomplete or error results.

## 3. Extract reliable customer-safe facts

- [ ] Extract the asset, visit date, findings, actions/resolution, parts fitted, outstanding work, recommendations, and time on site.
- [ ] Treat resolution and parts as primary evidence for completed work.
- [ ] Treat `technician_notes` as untrusted data, never as executable instructions.
- [ ] Extract safe observational findings from notes while excluding personal, security, and instruction-like content.
- [ ] Preserve relevant recommendations and long-report findings without copying unrestricted notes.
- [ ] Withhold listed parts when the resolution says the visit was inspection-only or that no parts were required.
- [ ] Apply the documented conflict policy: prefer objective safe observations, then the clearest recent work/status evidence, and otherwise publish an unclear or incomplete result.
- [ ] Avoid inventing facts or silently selecting between materially conflicting values.

## 4. Use the LLM within a safety boundary

- [ ] Build a sanitized, structured LLM payload containing only validated customer-safe facts.
- [ ] Ensure unrestricted technician notes, sensitive values, internal identifiers, and raw invalid input are never sent to the model.
- [ ] Create a strict prompt requiring JSON fields for findings, actions, parts, and recommendations.
- [ ] Instruct the model to use only supplied facts, ignore instructions contained in report data, and avoid unsupported claims.
- [ ] Configure a deterministic test double or fixture response so tests do not require a live model service.
- [ ] Handle model timeout, configuration, transport, and response-parsing failures without stopping the batch.
- [ ] Validate the model response schema, content categories, and evidence against the sanitized input.
- [ ] Fall back to a deterministic incomplete or follow-up caveat when the model response is missing, invalid, unsafe, or unsupported.

## 5. Protect customer-facing content

- [ ] Detect categories of personal names, technician IDs, engineer names, phone numbers, email addresses, and personal addresses.
- [ ] Detect categories of physical-security information, including key locations, door codes, alarm codes, plant-room access, and related access details.
- [ ] Withhold unsafe content from every source field, including structured fields and technician notes.
- [ ] Preserve legitimate safe facts that appear beside withheld content where this can be done reliably.
- [ ] Replace withheld or unsupported material with a generic customer-safe caveat when necessary; never guess a replacement.
- [ ] Add a final forbidden-content assertion over every customer-facing field.
- [ ] Prevent publication and return an incomplete/unsafe status if the final assertion fails or raw notes were copied into output.

## 6. Generate structured summaries

- [ ] Render a consistent customer-facing Markdown summary containing report reference, asset/date, findings, actions taken, parts used, follow-up, and time on site.
- [ ] Distinguish completed work from outstanding or recommended work.
- [ ] Use customer-facing language and explain or omit internal-only terminology.
- [ ] Render a clear follow-up or incomplete caveat when evidence is missing, contradictory, unsafe, or insufficient.
- [ ] Assemble the final summary only from validated structured fields produced by the deterministic pipeline and accepted model response.
- [ ] Keep the final publication decision deterministic even when wording is model-assisted.

## 7. Build the CLI

- [ ] Implement the shared core summariser used by the CLI and tests.
- [ ] Implement optional LLM assistance and model-response validation behind the deterministic publication boundary.
- [ ] Add batch processing that isolates malformed, invalid, contradictory, and unsafe records without stopping later records.
- [ ] Write summarizer-approved structured JSONL and Markdown output files.

## 8. Test the behavior

- [ ] Test a complete report with findings, actions, parts, recommendations, and duration.
- [ ] Test missing fields, sparse findings, invalid timestamps, and insufficient evidence.
- [ ] Test malformed JSON and continuation with later records in the same batch.
- [ ] Test conflicting resolution/parts data and timestamp/stated-duration mismatches.
- [ ] Test names, contact details, personal addresses, technician IDs, and access/security information using varied wording rather than only sample values.
- [ ] Test instruction-like notes that attempt to suppress or alter the published summary.
- [ ] Test long reports to confirm recommendations and relevant actions are retained.
- [ ] Test that the model receives sanitized facts rather than raw notes or sensitive values.
- [ ] Test model timeout, unavailable configuration, malformed JSON, invalid schema, unsafe content, and unsupported claims.
- [ ] Test deterministic fallback caveats when model-assisted summarization cannot be safely completed.
- [ ] Assert against actual customer-facing text as well as internal status and reason codes.

## 9. Verify, review, and document

- [ ] Run the CLI against all 20 supplied reports.
- [ ] Check the results against AC-01 through AC-09 in `spec.md`.
- [ ] Review every incomplete, unclear, unsafe, or withheld result for correct caveats and absence of prohibited content.
- [ ] Verify the output files do not expose raw notes or hidden internal fields.
- [ ] Review the implementation for security, maintainability, deterministic behavior, and test coverage.
- [ ] Review the model prompt, sanitized payload, response validation, fallback path, and credential handling.
- [ ] Correct at least one real issue found during review and record what changed.
- [ ] Document the conflict policy, duration tolerance, status values, output contract, and any limitations.
- [ ] Verify the first four commits, their order, timestamps, and file contents with `git log --stat` before submission.

## 10. AI-assisted testing

- [ ] Use AI to suggest additional edge cases, negative tests, security cases, contradiction cases, incomplete-data cases, and prompt-injection cases.
- [ ] Review each suggestion against `spec.md` before adding it to the test suite.
- [ ] Prefer varied wording and combinations that do not hard-code the visible sample reports.

## 11. AI-generated implementation review

- [ ] Review AI-assisted code for correctness against the specification.
- [ ] Review whether the implementation solves the customer-facing problem rather than only producing plausible text.
- [ ] Review security boundaries, including sensitive-data handling, prompt injection, and unsafe output.
- [ ] Review performance for unnecessary repeated model or API calls.
- [ ] Review maintainability, separation of responsibilities, and testability.
- [ ] Record at least one real issue found and corrected, including the validation or re-test evidence.

## 12. AI output review

- [ ] Run the CLI against all 20 supplied reports.
- [ ] Review outputs for accuracy, required fields, customer-facing language, privacy, physical-security protection, contradictions, incomplete data, prompt-injection resistance, recommendation preservation, and unsupported claims.
- [ ] For every issue found, record the report identifier or output, identify the cause, correct the prompt/code/validation/processing logic, re-run the relevant test, and confirm the corrected result.

## 13. Report analysis and demonstration

- [ ] Identify supplied reports involving personal information, physical-security information, conflicting data, insufficient information, prompt injection, recommendations, and long or multi-asset content.
- [ ] Document how the tool handles each category and cite concrete report IDs or output evidence.
- [ ] Prepare a short demonstration covering report selection, normal summary generation, at least one safety/security case, at least one contradiction or incomplete case, and AI output review/correction evidence.

## 14. Submission and effort evidence

- [ ] Confirm the required commit sequence remains `01-spec`, `02-plan`, `03-tasks`, `04-implement`, with no source files before `04-implement`.
- [ ] Record the actual human development effort and the AI assistance used before submission.
