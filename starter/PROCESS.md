# Required build process

This case grades **how** you built the tool as heavily as the tool itself. The
sequence below is not a suggestion, and it is checked against your git history.

## Four commits, in order

Work in a git repository. Produce exactly these four commits, in this order,
each one a separate commit with its own message:

| Commit message | Contains |
|---|---|
| `01-spec` | `spec.md` only. **No source files.** |
| `02-plan` | adds `plan.md` |
| `03-tasks` | adds `tasks.md` |
| `04-implement` | adds your implementation |

Further commits after `04-implement` are fine and expected - fixes, tests,
refactors. What is graded is that the first four exist, in that order, and that
**no source file appears in the repository before `04-implement`**.

Submit the repository, or `git log --stat` output covering all four commits with
their timestamps.

## Why it is done this way

The four-phase loop is the competency being assessed, and it is the one competency
that is trivial to claim and impossible to verify from a finished artifact. A spec
written after the code, or alongside it, produces a different and worse spec - it
documents what you built rather than deciding what to build. The history is the
only evidence that distinguishes the two.

A learner who generates spec, plan, tasks and implementation in a single pass
cannot produce this history. That is the intent.

## What each document is for

**`spec.md`** - what the tool must do and for whom, in terms of observable
behaviour. Written before you know how you will build it. Include what it must
*not* do; read the summary requirements carefully before writing this.

**`plan.md`** - how you intend to build it. Structure, approach, the decisions you
are taking and the alternatives you are rejecting.

**`tasks.md`** - the decomposition into individually completable pieces, in the
order you intend to do them.

**`04-implement`** - the code. If while implementing you discover the spec was
wrong, fix the spec in a later commit and say so in your write-up. That is the
loop working, not a failure of it, and it is worth reporting.
