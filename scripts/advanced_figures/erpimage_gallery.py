"""Default advanced ERP-image figure gallery."""

from __future__ import annotations

try:
    from .catalog import render_module_doc
except ImportError:  # pragma: no cover - direct script execution support
    from catalog import render_module_doc

MODULE = {
    "title": "ERP-Image Advanced Figure Gallery",
    "summary": "Official ERP-image figures remain visible as a default companion to the ERP branch, with single-trial dynamics separated from waveform averages.",
    "python_module": "scripts/advanced_figures/erpimage_gallery.py",
    "markdown_path": "scripts/advanced_figures/erpimage.md",
    "mcp_route": "eeglab_plot_erp / erpimage",
    "branch": "ERP",
}

FIGURE_FAMILIES = [
    {
        "figure_family": "ERP-image heatmap",
        "status": "required",
        "official_anchor": "EEGLAB-ERP-001",
        "official_url": "https://eeglab.org/tutorials/08_Plot_data/Plotting_ERP_images.html",
        "mcp_tool": "eeglab_plot_erp",
        "official_scope": "Single-trial sorting, RT/phase review, and variance diagnostics.",
    },
    {
        "figure_family": "ERP waveform",
        "status": "conditional",
        "official_anchor": "EEGLAB-ERP-001",
        "official_url": "https://eeglab.org/tutorials/08_Plot_data/Data_Averaging.html",
        "mcp_tool": "eeglab_plot_erp",
        "official_scope": "Condition-average comparison context for the image heatmap.",
    },
    {
        "figure_family": "Latency-specific scalp maps",
        "status": "conditional",
        "official_anchor": "EEGLAB-TOPO-001",
        "official_url": "https://eeglab.org/tutorials/08_Plot_data/Data_Averaging.html",
        "mcp_tool": "eeglab_topoplot",
        "official_scope": "Spatial review of the same latency window used in ERP-image inspection.",
    },
]


def render_markdown() -> str:
    return render_module_doc(MODULE, FIGURE_FAMILIES)


if __name__ == "__main__":
    print(render_markdown())
