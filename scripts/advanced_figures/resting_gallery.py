"""Default advanced resting-state figure gallery."""

from __future__ import annotations

try:
    from .catalog import render_module_doc
except ImportError:  # pragma: no cover - direct script execution support
    from catalog import render_module_doc

MODULE = {
    "title": "Resting-State Advanced Figure Gallery",
    "summary": "Resting-state visuals stay centered on continuous data: spectra first, then band-power maps, then connectivity.",
    "python_module": "scripts/advanced_figures/resting_gallery.py",
    "markdown_path": "scripts/advanced_figures/resting.md",
    "mcp_route": "eeglab_plot_psd / eeglab_topoplot / eeglab_plot_connectivity",
    "branch": "Resting-state spectral / connectivity",
}

FIGURE_FAMILIES = [
    {
        "figure_family": "Channel spectra + maps",
        "status": "required",
        "official_anchor": "EEGLAB-SPECTRAL-001",
        "official_url": "https://eeglab.org/tutorials/08_Plot_data/Plotting_Channel_Spectra_and_Maps.html",
        "mcp_tool": "eeglab_plot_psd",
        "official_scope": "Channel and ROI power profile.",
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
        "figure_family": "Connectivity matrix / network",
        "status": "conditional",
        "official_anchor": "EEGLAB-SPECTRAL-001",
        "official_url": "https://eeglab.org/tutorials/08_Plot_data/Plotting_Channel_Spectra_and_Maps.html",
        "mcp_tool": "eeglab_plot_connectivity",
        "official_scope": "Sensor-level summary, not anatomical connectivity.",
    },
]


def render_markdown() -> str:
    return render_module_doc(MODULE, FIGURE_FAMILIES)


if __name__ == "__main__":
    print(render_markdown())
