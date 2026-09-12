# Report-by-report review

Generated from the deterministic batch output. The review records observable
outcomes without repeating raw technician notes or sensitive values.

| Report | Asset | Status | Review outcome |
|---|---|---|---|
| FSR-3001 | Chiller CH-04 | complete | Filter-drier work, part, visit date, and 2 hours 30 minutes are retained. |
| FSR-3002 | AHU-11 | complete | Belt adjustment is published and the next-maintenance recommendation is retained. |
| FSR-3003 | Boiler BLR-02 | complete | Safe ignition-electrode outcome is retained; personal and physical-security note content is withheld. |
| FSR-3004 | Pump P-07 | complete | Reset outcome is published without claiming the underlying recurring cause was resolved. |
| FSR-3005 | Chiller CH-01 | unclear | Timestamp duration conflicts with stated duration; no unqualified time is published. |
| FSR-3006 | Cooling tower CT-02 | unclear | Parts list conflicts with inspection-only resolution; contradiction is surfaced. |
| FSR-3007 | AHU-04 | incomplete | Evidence is too sparse to establish findings or completed work; follow-up is required. |
| FSR-3008 | VAV-22 | incomplete | Evidence is too sparse to establish a trustworthy customer summary. |
| FSR-3009 | Boiler BLR-05 | complete | Instruction-like note cannot override the structured service outcome. |
| FSR-3010 | Chiller CH-07 | complete | Expansion-valve work and dated follow-up recommendation are retained. |
| FSR-3011 | Central plant - multiple | complete | All seven listed parts, multi-asset work, elapsed time, and both recommendations are retained. |
| FSR-3012 | Pump P-12 | complete | Mechanical-seal replacement and outcome are published. |
| FSR-3013 | AHU-09 | complete | Differential-pressure switch replacement and alarm outcome are published. |
| FSR-3014 | Boiler BLR-08 | complete | Thermocouple outcome is retained; personal contact content is withheld. |
| FSR-3015 | Chiller CH-03 | complete | Coil-cleaning outcome and quarterly recommendation are retained. |
| FSR-3016 | Fan FCU-31 | complete | Capacitor replacement and normal operation are published. |
| FSR-3017 | Cooling tower CT-01 | complete | Fill-pack and drift-eliminator work is published; water-treatment review is retained. |
| FSR-3018 | AHU-15 | complete | Sensor recalibration outcome is published. |
| FSR-3019 | Boiler BLR-03 | complete | Gas-valve replacement and passed combustion test are published. |
| FSR-3020 | Pump P-03 | complete | Resolved weep and monitor-at-next-visit recommendation are retained. |

## Totals

- 20 of 20 records processed.
- 16 complete.
- 2 unclear: FSR-3005 and FSR-3006.
- 2 incomplete: FSR-3007 and FSR-3008.
- 0 unsafe results in the supplied dataset.

## Safety cases

- FSR-3003 and FSR-3014 demonstrate withholding of sensitive note content while
  preserving safe neighboring service facts.
- FSR-3009 demonstrates resistance to an instruction embedded in a note.
- FSR-3011 demonstrates retention of long, multi-asset recommendations rather
  than truncating at the first completed action.
