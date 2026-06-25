"""Default advanced time-frequency figure gallery."""

from __future__ import annotations

try:
    from .catalog import render_module_doc
except ImportError:  # pragma: no cover - direct script execution support
    from catalog import render_module_doc

MODULE = {
    "title": "Time-Frequency Advanced Figure Gallery",
    "summary": "The time-frequency branch is built around ERSP/ITC.",
    "python_module": "scripts/advanced_figures/timefreq_gallery.py",
    "markdown_path": "scripts/advanced_figures/timefreq.md",
    "mcp_route": "eeglab_plot_timefreq",
    "branch": "Time-frequency",
}

FIGURE_FAMILIES = [
    {
        "figure_family": "ERSP / ITC heatmap",
        "status": "required",
        "official_anchor": "EEGLAB-TF-001",
        "official_url": "https://eeglab.org/tutorials/08_Plot_data/Time-Frequency_decomposition.html",
        "mcp_tool": "eeglab_plot_timefreq",
        "official_scope": "Event-locked power and phase dynamics.",
    },
    {
        "figure_family": "Time-frequency curves",
        "status": "conditional",
        "official_anchor": "EEGLAB-TF-001",
        "official_url": "https://eeglab.org/tutorials/08_Plot_data/Time-Frequency_decomposition.html",
        "mcp_tool": "eeglab_plot_timefreq",
        "official_scope": "Frequency-specific time courses.",
    },
    {
        "figure_family": "tftopo summary",
        "status": "guidance_only",
        "official_anchor": "EEGLAB-TF-001",
        "official_url": "https://eeglab.org/tutorials/08_Plot_data/EEG_scalp_measures.html",
        "mcp_tool": "tftopo",
        "official_scope": "Multi-electrode summary, static only.",
    },
    {
        "figure_family": "metaplottopo summary",
        "status": "guidance_only",
        "official_anchor": "EEGLAB-TF-001",
        "official_url": "https://eeglab.org/tutorials/08_Plot_data/EEG_scalp_measures.html",
        "mcp_tool": "metaplottopo",
        "official_scope": "Channel-grid summary, static only.",
    },
]


def render_markdown() -> str:
    return render_module_doc(MODULE, FIGURE_FAMILIES)


if __name__ == "__main__":
    print(render_markdown())
