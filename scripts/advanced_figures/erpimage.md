# ERP-Image Advanced Figure Gallery

This default module keeps ERP-image figures visible as a browsable companion to the official ERP figure atlas.

## Default Status

- Default enabled: yes
- Python module: `scripts/advanced_figures/erpimage_gallery.py`
- Markdown guide: `scripts/advanced_figures/erpimage.md`
- Default MCP route: `eeglab_plot_erp / erpimage`

## Figure Families

| Figure family | Status | Official anchor | Official URL | MCP tool | Official scope |
| --- | --- | --- | --- | --- | --- |
| ERP-image heatmap | required | `EEGLAB-ERP-001` | `https://eeglab.org/tutorials/08_Plot_data/Plotting_ERP_images.html` | `eeglab_plot_erp` | Single-trial sorting, RT/phase review, and variance diagnostics. |
| ERP waveform | conditional | `EEGLAB-ERP-001` | `https://eeglab.org/tutorials/08_Plot_data/Data_Averaging.html` | `eeglab_plot_erp` | Condition-average comparison context for the image heatmap. |
| Latency-specific scalp maps | conditional | `EEGLAB-TOPO-001` | `https://eeglab.org/tutorials/08_Plot_data/Data_Averaging.html` | `eeglab_topoplot` | Spatial review of the same latency window used in ERP-image inspection. |
