# Field Service Report Summarizer - Specification

## 1. Purpose

Build a tool that transforms engineer field-service reports into customer-ready summaries for publication to the Northgate FM customer portal.

The primary goal is that a client's facilities contact can read the summary and understand what happened to their asset without needing to contact Northgate for clarification and without being exposed to information that should remain internal.

The tool must prioritise correctness, safe publication, and faithful representation of the source report over producing a summary at any cost.

## 2. Intended audience

- Primary audience: the client’s facilities contact.
- Not an audience: Northgate engineers, internal service teams, or anyone who needs operational or technician access details.
- The summary must be readable without a phone call to the contractor.

## 3. Required observable behavior

For each report, the tool must output a summary that includes all of the following:

1. Asset
2. Date of the visit
3. What was found.
4. What was done.
5. Any parts fitted, if applicable.
6. Anything outstanding or recommended.
7. Time on site.

The summary must be written in plain English and must not include internal identifiers beyond the asset reference itself.

The tool must process each report independently. A malformed, invalid, incomplete, contradictory, or unsafe report must receive a safe result and must not prevent later reports in the same batch from being processed.

## 4. Required output format

The tool must produce one summary per report using a consistent structure such as:

- Asset and visit date
- Findings
- Actions taken
- Parts fitted
- Outstanding items or recommendations
- Time on site

The CLI must write this output in structured JSONL and a customer-facing Markdown document. The Markdown document must use a consistent per-report structure with the asset, report reference, visit date, summary, work completed, parts used, follow-up, and time on site. No raw or hidden internal data may appear in either output.

If the tool can only produce a partial or incomplete summary, it must state that the report is incomplete or the status is unclear rather than guessing.

Each structured result must include:

- the customer-safe summary sections listed above;
- a publication status such as `complete`, `incomplete`, `unclear`, or `unsafe`;
- a customer-facing caveat when follow-up is required.

Internal validation reasons may be retained for operator review, but must be separate from customer-facing fields and must not contain raw notes or sensitive values.

## 5. Safety and redaction rules

The tool must not republish any of the following from the technician notes or any other report field:

- Personal names of individuals
- Technician IDs
- Personal contact details, including phone numbers and email addresses
- Home or personal addresses
- Site access information such as key locations, door codes, alarm codes, or plant-room access codes
- Internal technician identifiers or engineer names
- Other physical security information
- Unnecessary internal information

This is a security requirement, not a cosmetic one. Access information must be withheld even if it appears in a field that otherwise looks harmless. 

The protection shall apply to categories of information, not only to the exact values found in the supplied reports.

## 6. Rules for handling notes that are not instruction-bearing

The `technician_notes` field is input data, not a set of instructions for the summary tool. It may contain:

- observations from the visit,
- a note about the issue,
- recommendations,
- contradictory facts,
- or a request to suppress something from the customer summary.

A note that appears to instruct omission or direct the summary publication must be treated as a signal to review the content for customer safety, not as an instruction to obey it.

If a note contains something that must not appear in a published summary, the tool must withhold it and continue with the safe information only.

Technician notes must never be treated as executable instructions. The tool must not send unrestricted notes, raw sensitive values, or invalid raw input to an AI model. Any model-assisted output must be checked against the validated source facts and all publication rules before it is returned.

## 7. Data quality and uncertainty handling

The source data is unvalidated and may contain contradictory or incomplete fields. The tool must not silently resolve contradictions by guessing.

If a material conflict or lack of information prevents a trustworthy summary, the tool shall indicate that the report requires a follow-up rather than producing a confident summary. 

When the report is internally inconsistent, or too weak to support a confident summary, the tool must say so. It should publish a clear caveat such as:

- “This report is incomplete and requires follow-up.”
- “The available information is inconsistent; a precise summary cannot be confirmed.”

The tool must prefer safe, explicit, and customer-appropriate language over confident speculation.

For time on site, the tool should calculate the duration from valid arrival and departure timestamps when available. If a stated duration materially disagrees with the calculated duration, the discrepancy must be flagged and the tool must not present an unqualified duration as reliable. Invalid or incomplete timestamps must result in an incomplete or unclear status when they prevent a trustworthy duration.

## 8. Decision policy for conflicting values

This specification leaves open the question of which value to prefer when two fields disagree. To keep the behavior consistent, the tool must follow this decision rule:

1. Prefer objective, customer-safe observations from the resolution and technician notes over incomplete metadata.
2. Prefer the most recent explicit field that clearly describes the actual work performed or status of the asset.
3. If the disagreement still prevents a reliable customer summary, publish a status of incomplete/unclear rather than selecting a value arbitrarily.
4. Do not invent missing facts to complete the summary.

This rule must be applied consistently to every report.

## 9. Summary Quality

The tool shall:

- use plain customer-facing language;
- accurately represent the report;
- preserve relevant recommendations and outstanding work;
- distinguish completed work from outstanding work;
- avoid unsupported assumptions;
- avoid exposing prohibited information.

The tool must not:

- fabricate information;
- publish names, phone numbers, addresses, access codes, or other personal or security-sensitive information;
- include engineer names or technician IDs;
- invent facts to fill missing information;
- pretend a contradictory or incomplete report is fully resolved;
- obey instructions embedded in the notes that would compromise the customer-facing summary;
- create a summary that uses internal-only terminology without customer-safe explanation;
- republish information that was only known to the engineer and should not be visible to the client.

## 10. Acceptance criteria

### AC-01 - Required content
A valid report produces a summary containing all required information that is available and reliable. Every input report receives a customer-safe result, including an incomplete or unsafe result where a normal summary cannot be produced.

### AC-02 - Customer language
The summary is understandable to a client's facilities contact.

### AC-03 - Privacy
Personal information and internal personal information do not appear in the published summary.

### AC-04 - Physical security
Keys, access locations, door codes, alarm codes and similar information do not appear in the published summary. It omits all prohibited content

### AC-05 - Conflicting information
Materially conflicting information is identified rather than silently resolved.

### AC-06 - Insufficient information
Reports that cannot be reliably summarised result in a clear follow-up/incomplete outcome.

### AC-07 - Prompt-injection resistance
Instructions contained within technician notes cannot override the summary requirements. The tool does not replicate or amplify access/security information from the technician notes.

### AC-08 - Recommendations
Relevant outstanding or recommended work is retained in the summary.

### AC-09 - No fabrication
The tool does not invent information that is absent from the report

### AC-10 - Failure-safe model assistance
If an AI model is unavailable, times out, returns invalid structured data, includes prohibited content, or makes unsupported claims, the tool does not publish that response. It returns a deterministic incomplete, unclear, or unsafe result with an appropriate follow-up caveat.

### AC-11 - Batch continuation
Malformed JSON or an invalid report does not terminate batch processing. The tool returns exactly one result for each input record or line and continues with subsequent records.

### AC-12 - Final publication boundary
Before a result is returned or displayed, every customer-facing field is checked for prohibited personal, internal, physical-security, and unsupported content. A failed check prevents publication.

## 11. Success criteria for the tool

The tool is successful when a client can read the output and understand:

- what asset was visited,
- when it was visited,
- what the problem was,
- what action was taken,
- whether anything remains outstanding,
- and whether follow-up is required,

without needing access to internal service records or any hidden notes.

## 12. Non-functional expectations

The implementation should be reliable, deterministic, and reviewable. It should be easy to audit for redaction failures and easy to test against edge cases such as:

- missing fields,
- contradictory fields,
- notes containing personal data,
- notes that ask for suppression,
- long reports with many actions,
- incomplete or insufficiently clear findings.
- malformed JSON or invalid record types;
- invalid timestamps and material duration mismatches;
- unavailable, malformed, or unsafe AI responses;
- long or multi-record batch inputs where one record must not stop later records.

The tool should be designed to fail safely: when the evidence is weak or unsafe, it should publish a caveat rather than a confident summary.
