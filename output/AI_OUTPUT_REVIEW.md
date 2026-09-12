# AI output review

## Intent

The customer-facing result contains the required asset, visit date, findings,
actions, parts, outstanding/recommended work, time on site, and status. The
the CLI writes only approved customer-facing fields.

## Security

The model is optional and receives trusted facts rather than unrestricted
technician notes. Its asset, date, and parts claims are checked against those
facts. Final output validation covers contact details, names, addresses,
technician identifiers, and physical-security language. Operator reasons remain
separate from customer-facing caveats.

Evidence cases:

- FSR-3003 and FSR-3014 retain safe service outcomes while withholding
  personal/contact and access-related note content.
- FSR-3009 cannot use an embedded note instruction to change the published
  resolution.
- FSR-3011 retains recommendations at the end of a long multi-asset report.

## Tests and performance

`pytest -q` passes 12 focused summarizer tests. The CLI processes the 20-record JSONL input
in one streaming pass and produces exactly 20 output lines. The deterministic
fallback is used when no model credentials are configured.

## Real issues found and corrected

1. The first implementation copied technician notes into trusted facts. This
   created a potential path for personal and access information. The fix keeps
   only filtered recommendation-bearing sentences.
2. A broad security expression classified ordinary text such as `alarm
   cleared` as access information. The final check requires access context such
   as a code, pin, location, or key.
3. Deterministic caveats initially exposed operator wording such as internal
   identifier warnings. The final publication text now uses a generic
   customer-safe notice while detailed reasons remain internal.

Each correction was followed by focused tests and a full batch run.

## Limitations

The repository's existing git history does not contain the original required
four-commit sequence. This evidence set improves implementation and review
quality but does not recreate that historical process evidence.
