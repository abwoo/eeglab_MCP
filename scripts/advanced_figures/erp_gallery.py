"""Default advanced ERP figure gallery."""

from __future__ import annotations

try:
    from .catalog import render_module_doc
except ImportError:  # pragma: no cover - direct script execution support
    from catalog import render_module_doc

MODULE = {
    "title": "ERP Advanced Figure Gallery",
    "summary": "Event-locked ERP figures stay aligned to the official ERP, event, and topography tutorials.",
    "python_module": "scripts/advanced_figures/erp_gallery.py",
    "markdown_path": "scripts/advanced_figures/erp.md",
    "mcp_route": "eeglab_plot_erp / eeglab_topoplot / eeglab_plot_psd",
    "branch": "ERP",
}

FIGURE_FAMILIES = [
    {
        "figure_family": "ERP waveform",
        "status": "required",
        "official_anchor": "EEGLAB-ERP-001",
        "official_url": "https://eeglab.org/tutorials/08_Plot_data/Data_Averaging.html",
        "mcp_tool": "eeglab_plot_erp",
        "official_scope": "Mean amplitude and latency comparison across conditions.",
    },
    {
        "figure_family": "ERP-image heatmap",
        "status": "conditional",
        "official_anchor": "EEGLAB-ERP-001",
        "official_url": "https://eeglab.org/tutorials/08_Plot_data/Plotting_ERP_images.html",
        "mcp_tool": "eeglab_plot_erp",
        "official_scope": "Single-trial sorting, RT/phase review, variance diagnostics.",
    },
    {
        "figure_family": "Scalp map series",
        "status": "required",
        "official_anchor": "EEGLAB-TOPO-001",
        "official_url": "https://eeglab.org/tutorials/08_Plot_data/Data_Averaging.html",
        "mcp_tool": "eeglab_topoplot",
        "official_scope": "Latency-specific scalp distribution.",
    },
    {
        "figure_family": "Difference-wave review",
        "status": "conditional",
        "official_anchor": "EEGLAB-ERP-001",
        "official_url": "https://eeglab.org/tutorials/08_Plot_data/Data_Averaging.html",
        "mcp_tool": "eeglab_plot_erp",
        "official_scope": "Polarity and latency sanity check.",
    },
    {
        "figure_family": "PSD review",
        "status": "required",
        "official_anchor": "EEGLAB-SPECTRAL-001",
        "official_url": "https://eeglab.org/tutorials/08_Plot_data/Plotting_Channel_Spectra_and_Maps.html",
        "mcp_tool": "eeglab_plot_psd",
        "official_scope": "Broad spectral sanity check.",
    },
]


def render_markdown() -> str:
    return render_module_doc(MODULE, FIGURE_FAMILIES)


if __name__ == "__main__":
    print(render_markdown())
