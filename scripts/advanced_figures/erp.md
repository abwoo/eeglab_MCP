# ERP Advanced Figure Gallery

This default module keeps the ERP figure families visible and aligned to the
official ERP, event, and topography tutorials.

## Default Status

- Default enabled: yes
- Python module: `scripts/advanced_figures/erp_gallery.py`
- Markdown guide: `scripts/advanced_figures/erp.md`
- Default MCP route: `eeglab_plot_erp / eeglab_topoplot / eeglab_plot_psd`

## Figure Families

| Figure family | Status | Official anchor | Official URL | MCP tool | Official scope |
| --- | --- | --- | --- | --- | --- |
| ERP waveform | required | `EEGLAB-ERP-001` | `https://eeglab.org/tutorials/08_Plot_data/Data_Averaging.html` | `eeglab_plot_erp` | Mean amplitude and latency comparison across conditions. |
| ERP-image heatmap | conditional | `EEGLAB-ERP-001` | `https://eeglab.org/tutorials/08_Plot_data/Plotting_ERP_images.html` | `eeglab_plot_erp` | Single-trial sorting, RT/phase review, variance diagnostics. |
| Scalp map series | required | `EEGLAB-TOPO-001` | `https://eeglab.org/tutorials/08_Plot_data/Data_Averaging.html` | `eeglab_topoplot` | Latency-specific scalp distribution. |
| Difference-wave review | conditional | `EEGLAB-ERP-001` | `https://eeglab.org/tutorials/08_Plot_data/Data_Averaging.html` | `eeglab_plot_erp` | Polarity and latency sanity check. |
| PSD review | required | `EEGLAB-SPECTRAL-001` | `https://eeglab.org/tutorials/08_Plot_data/Plotting_Channel_Spectra_and_Maps.html` | `eeglab_plot_psd` | Broad spectral sanity check. |
