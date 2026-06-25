# ICA Advanced Figure Gallery

This default module keeps the component-review figure families visible and
aligned to the official ICA and time-frequency tutorials.

## Default Status

- Default enabled: yes
- Python module: `scripts/advanced_figures/ica_gallery.py`
- Markdown guide: `scripts/advanced_figures/ica.md`
- Default MCP route: `eeglab_plot_components / eeglab_plot_timefreq`

## Figure Families

| Figure family | Status | Official anchor | Official URL | MCP tool | Official scope |
| --- | --- | --- | --- | --- | --- |
| Component spectra | required | `EEGLAB-ICA-001` | `https://eeglab.org/tutorials/08_Plot_data/Plotting_ICA_components.html` | `eeglab_plot_components` | Component spectral contribution. |
| Component head plots | required | `EEGLAB-ICA-001` | `https://eeglab.org/tutorials/08_Plot_data/Plotting_ICA_components.html` | `eeglab_plot_components` | Component scalp projection review. |
| Component ERP envelopes | conditional | `EEGLAB-ICA-001` | `https://eeglab.org/tutorials/08_Plot_data/Plotting_ICA_components.html` | `eeglab_plot_components` | Component contribution to ERP morphology. |
| Component ERP-image | conditional | `EEGLAB-ICA-001` | `https://eeglab.org/tutorials/08_Plot_data/Plotting_ICA_components.html` | `eeglab_plot_components` | Single-component trial sorting. |
| Component time-frequency | conditional | `EEGLAB-TF-001` | `https://eeglab.org/tutorials/08_Plot_data/Time-Frequency_decomposition.html` | `eeglab_plot_timefreq` | Component ERSP / ITC dynamics. |
