# EEGLAB Statistics And Reporting

Use this reference when a workflow reaches STUDY, LIMO, SIFT/connectivity, or a
methods/reporting handoff.

## Group And Statistics Gates

- Single-subject preprocessing must be locked before STUDY/group statistics.
- Subject/session layout and design variables must be known before creating
  design contrasts or claiming group effects.
- Alpha, correction method, measure type, and contrast/condition definitions
  must be recorded before statistical output is interpreted.
- LIMO and SIFT workflows require explicit plugin availability and design
  suitability; otherwise keep the output to planning or QC.

## Minimum Report Fields

Every EEGLAB report should include:

- input and output paths
- sampling rate, duration, channel count, data shape, and reference/montage
- channel-location coverage and missing-location limitations
- event labels, counts, roles, and event-code source
- filter, line-noise, rereference, ASR, ICA, ICLabel, epoch, baseline,
  frequency, source, STUDY, alpha, and correction parameters when used
- generated files, failed steps, recovery choices, gate results, source claim
  IDs, override status, and limitations

Do not make clinical, diagnostic, anatomical-certainty, or group-statistical
claims when the relevant gate prerequisites are missing or overridden.
