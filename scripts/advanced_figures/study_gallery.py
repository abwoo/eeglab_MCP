"""Default advanced STUDY / group figure gallery."""

from __future__ import annotations

try:
    from .catalog import render_module_doc
except ImportError:  # pragma: no cover - direct script execution support
    from catalog import render_module_doc

MODULE = {
    "title": "STUDY Advanced Figure Gallery",
    "summary": "Group-level figures are only meaningful after single-subject preprocessing is locked.",
    "python_module": "scripts/advanced_figures/study_gallery.py",
    "markdown_path": "scripts/advanced_figures/study.md",
    "mcp_route": "eeglab_plot_erp / eeglab_plot_psd / eeglab_plot_timefreq / eeglab_study_statistics",
    "branch": "STUDY / group analysis",
}

FIGURE_FAMILIES = [
    {
        "figure_family": "Grand-average ERP",
        "status": "required",
        "official_anchor": "EEGLAB-STUDY-001",
        "official_url": "https://eeglab.org/tutorials/10_Group_analysis/study_data_visualization_tools.html",
        "mcp_tool": "eeglab_plot_erp",
        "official_scope": "Group-level ERP summary.",
    },
    {
        "figure_family": "All-channel ERP",
        "status": "conditional",
        "official_anchor": "EEGLAB-STUDY-001",
        "official_url": "https://eeglab.org/tutorials/10_Group_analysis/study_data_visualization_tools.html",
        "mcp_tool": "eeglab_plot_erp",
        "official_scope": "Channel-wide ERP review.",
    },
    {
        "figure_family": "Spectra / scalp maps",
        "status": "conditional",
        "official_anchor": "EEGLAB-STUDY-PRECOMP-001",
        "official_url": "https://eeglab.org/tutorials/10_Group_analysis/study_data_visualization_tools.html",
        "mcp_tool": "eeglab_plot_psd",
        "official_scope": "Group spectral summary.",
    },
    {
        "figure_family": "ERP-image review",
        "status": "conditional",
        "official_anchor": "EEGLAB-STUDY-001",
        "official_url": "https://eeglab.org/tutorials/10_Group_analysis/study_data_visualization_tools.html",
        "mcp_tool": "eeglab_plot_erp",
        "official_scope": "Trial-level or subject-level sorting review.",
    },
    {
        "figure_family": "ERSP / ITC summary",
        "status": "conditional",
        "official_anchor": "EEGLAB-STUDY-PRECOMP-001",
        "official_url": "https://eeglab.org/tutorials/10_Group_analysis/study_data_visualization_tools.html",
        "mcp_tool": "eeglab_plot_timefreq",
        "official_scope": "Group time-frequency summary.",
    },
    {
        "figure_family": "CI / contrast plots",
        "status": "conditional",
        "official_anchor": "EEGLAB-STUDY-001",
        "official_url": "https://eeglab.org/tutorials/10_Group_analysis/study_statistics.html",
        "mcp_tool": "eeglab_study_statistics",
        "official_scope": "Statistical contrast review.",
    },
    {
        "figure_family": "Cluster / edge visuals",
        "status": "guidance_only",
        "official_anchor": "EEGLAB-ICCLUSTER-001",
        "official_url": "https://eeglab.org/tutorials/10_Group_analysis/component_clustering_tools.html",
        "mcp_tool": "eeglab_study_statistics",
        "official_scope": "Cluster review or edge visualization only.",
    },
]


def render_markdown() -> str:
    return render_module_doc(MODULE, FIGURE_FAMILIES)


if __name__ == "__main__":
    print(render_markdown())
