"""Default advanced connectivity figure gallery."""

from __future__ import annotations

try:
    from .catalog import render_module_doc
except ImportError:  # pragma: no cover - direct script execution support
    from catalog import render_module_doc

MODULE = {
    "title": "Connectivity Advanced Figure Gallery",
    "summary": "Connectivity visuals stay sensor- or ROI-level unless a source model is explicitly justified.",
    "python_module": "scripts/advanced_figures/connectivity_gallery.py",
    "markdown_path": "scripts/advanced_figures/connectivity.md",
    "mcp_route": "eeglab_plot_connectivity / eeglab_plot_psd / eeglab_topoplot",
    "branch": "Spectral / connectivity",
}

FIGURE_FAMILIES = [
    {
        "figure_family": "Connectivity matrix / network",
        "status": "required",
        "official_anchor": "EEGLAB-SPECTRAL-001",
        "official_url": "https://eeglab.org/tutorials/08_Plot_data/Plotting_Channel_Spectra_and_Maps.html",
        "mcp_tool": "eeglab_plot_connectivity",
        "official_scope": "Sensor-level connectivity summary, not anatomical connectivity.",
    },
    {
        "figure_family": "Band-power topomaps",
        "status": "conditional",
        "official_anchor": "EEGLAB-TOPO-001",
        "official_url": "https://eeglab.org/tutorials/08_Plot_data/Plotting_Channel_Spectra_and_Maps.html",
        "mcp_tool": "eeglab_topoplot",
        "official_scope": "Frequency-band scalp distribution.",
    },
    {
        "figure_family": "Channel spectra + maps",
        "status": "required",
        "official_anchor": "EEGLAB-SPECTRAL-001",
        "official_url": "https://eeglab.org/tutorials/08_Plot_data/Plotting_Channel_Spectra_and_Maps.html",
        "mcp_tool": "eeglab_plot_psd",
        "official_scope": "Channel and ROI power profile used to contextualize connectivity.",
    },
    {
        "figure_family": "ROI connectivity matrix",
        "status": "conditional",
        "official_anchor": "EEGLAB-ROICONNECT-001",
        "official_url": "https://eeglab.org/plugins/roiconnect/",
        "mcp_tool": "eeglab_plot_connectivity",
        "official_scope": "ROI-level functional connectivity summary.",
    },
    {
        "figure_family": "SIFT connectivity summary",
        "status": "guidance_only",
        "official_anchor": "EEGLAB-SIFT-001",
        "official_url": "https://eeglab.org/plugins/SIFT/",
        "mcp_tool": "SIFT",
        "official_scope": "Model-based connectivity summary only.",
    },
]


def render_markdown() -> str:
    return render_module_doc(MODULE, FIGURE_FAMILIES)


if __name__ == "__main__":
    print(render_markdown())
