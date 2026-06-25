# EEGLAB Figure Atlas

The canonical branch workflow matrix names the required, conditional, and guidance-only figure families. This file mirrors the official figure policy for the execution layer.

## Rule Set

- Use only real loaded EEG data and real project metadata.
- Keep static figures as the default executable baseline.
- Treat movie/animation figure outputs as guidance-only unless a dedicated workflow exists.
- Record `figure_type`, `branch_id`, `branch_mode`, `branch_variant`, `channel_or_roi`, `latency_window`, `frequency_window`, `tool_source`, `official_anchor`, `official_url`, `interpretation_scope`, and absolute `figure_path` for every figure.

## Branch Families

### ERP

- Required: ERP waveform, scalp map series, PSD review
- Conditional: ERP-image heatmap, difference-wave review, ICA component diagnostics

### Resting-State Spectral / Connectivity

- Required: channel spectra
- Conditional: band-power topomap, connectivity matrix

### Time-Frequency

- Required: ERSP / ITC heatmap
- Conditional: time-frequency curve
- Guidance-only: `tftopo`, `metaplottopo`

### ICA

- Required: component spectra, component head plots
- Conditional: component ERP, component ERP-image, component time-frequency

### Source / Connectivity

- Required: source / dipole review
- Conditional: ROI connectivity matrix, component head plot
- Guidance-only: SIFT time-frequency grids, ROIconnect review extras

### STUDY / Group Analysis

- Required: grand-average ERP
- Conditional: all-channel ERP, spectra and scalp maps, ERP-image review, ERSP / ITC summary, CI / contrast plots
- Guidance-only: cluster / edge visuals

## Cross-References

- `docs/figure-atlas.md`
- `scripts/advanced_figures/`
- `references/branch-workflow-matrix.md`
- `references/report-protocol-templates.md`
- `docs/official-report-field-matrix.md`
