# Advanced Figure Gallery

This default gallery gives the richer EEG figure families a browsable home.
Use it as the visual companion to the official figure atlas, while keeping the
MCP tools as the execution path.

## Modules

| Module | Python file | Markdown guide | Primary branch |
| --- | --- | --- | --- |
| ERP advanced figures | `scripts/advanced_figures/erp_gallery.py` | `scripts/advanced_figures/erp.md` | ERP |
| ERP-image advanced figures | `scripts/advanced_figures/erpimage_gallery.py` | `scripts/advanced_figures/erpimage.md` | ERP |
| Resting-state advanced figures | `scripts/advanced_figures/resting_gallery.py` | `scripts/advanced_figures/resting.md` | Resting-state spectral / connectivity |
| Time-frequency advanced figures | `scripts/advanced_figures/timefreq_gallery.py` | `scripts/advanced_figures/timefreq.md` | Time-frequency |
| ICA advanced figures | `scripts/advanced_figures/ica_gallery.py` | `scripts/advanced_figures/ica.md` | ICA and artifact handling |
| Connectivity advanced figures | `scripts/advanced_figures/connectivity_gallery.py` | `scripts/advanced_figures/connectivity.md` | Spectral / connectivity |
| Source and connectivity advanced figures | `scripts/advanced_figures/source_gallery.py` | `scripts/advanced_figures/source.md` | Source localization / connectivity |
| STUDY advanced figures | `scripts/advanced_figures/study_gallery.py` | `scripts/advanced_figures/study.md` | STUDY / group analysis |

## Default Companion

Use the module that matches the branch you are about to execute. Each module
mirrors the official figure atlas and stays default-visible.

## Notes

- They do not replace the canonical MCP tools.
- They mirror the figure atlas so the figure families stay visible even when the
  user is browsing files instead of the MCP surface.
