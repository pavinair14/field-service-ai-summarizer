# Submission Checklist — L1_Case03_Field_Service_Summarizer

## The process requirement — read this first

- [ ] Four commits in order: `01-spec` (containing `spec.md` and **no source files**), `02-plan`, `03-tasks`, `04-implement`.
- [ ] No source file appears in the repository before `04-implement`.
- [ ] Commit timestamps are distinct and increasing.
- [ ] Submitted as the repository, or `git log --stat` covering all four commits with timestamps.

This is the evidence for Spec-Driven Development. Nothing else substitutes for it —
a spec written alongside or after the code cannot be distinguished from one written
before it by reading the document, only by reading the history. Four commits inside
the same minute will be read as a single generated pass.

## Deliverables

- [ ] `spec.md`, `plan.md`, `tasks.md` as committed.
- [ ] Working tool, plus its output for all 20 reports.
- [ ] Your analysis of the reports that could not be summarised normally, and what your tool did with each.
- [ ] Your AI output review across intent, tests, security, performance and maintainability, with at least one real issue found and corrected.
- [ ] A documented decision on the case the specification leaves open, applied consistently.
- [ ] A short demo, and a declared-effort statement.

## Evidence standard

Every claim cites a report id or a specific output. "The tool redacts personal
information" scores nothing. "FSR-3003's note contains a name, a mobile number, a
spare-key location and a plant-room access code; here is the published summary
showing all four absent" scores.

## Before you submit — challenge your own work

- [ ] Did I write the spec before the code, genuinely? Does my `spec.md` decide things, or describe the implementation I had already written?
- [ ] **Did I read all 20 reports looking for what should not be republished, or did I assume the data was clean?** These notes were written for internal colleagues, and the portal is customer-visible.
- [ ] For each report where something must be withheld: is *everything* withheld, or only the obvious item? A redacted phone number next to a published door code is not a pass.
- [ ] Which reports contain fields that contradict each other? What did my tool publish for those?
- [ ] Which reports contain too little to summarise? Did my tool say so, or did it produce a confident summary of nothing?
- [ ] Is there a report where the note tries to influence what my tool publishes? Did it succeed, and would anyone know?
- [ ] For the longest report — did the recommendations at the end survive, or did my tool truncate somewhere it looks fine?
- [ ] Does my security review cover what the tool *publishes*, not only how the code is written?

## How this will be assessed

Your tool is run against a **held-out set of reports you have not seen**,
containing the same categories of problem in different words. A redaction approach
built on the specific strings in the visible reports will fail; one built on the
categories in the requirements will hold.

The process check is graded first. A missing or out-of-order history caps
*Spec-Driven Development* at Not Yet whatever the quality of the documents.

You will also answer several questions about your own submission at submission
time. They reference specific reports and commits, so they cannot be prepared in
advance.
