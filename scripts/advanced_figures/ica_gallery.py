"""Default advanced ICA figure gallery."""

from __future__ import annotations

try:
    from .catalog import render_module_doc
except ImportError:  # pragma: no cover - direct script execution support
    from catalog import render_module_doc

MODULE = {
    "title": "ICA Advanced Figure Gallery",
    "summary": "ICA figures are the bridge between decomposition and interpretation.",
    "python_module": "scripts/advanced_figures/ica_gallery.py",
    "markdown_path": "scripts/advanced_figures/ica.md",
    "mcp_route": "eeglab_plot_components / eeglab_plot_timefreq",
    "branch": "ICA and artifact handling",
}

FIGURE_FAMILIES = [
    {
        "figure_family": "Component spectra",
        "status": "required",
        "official_anchor": "EEGLAB-ICA-001",
        "official_url": "https://eeglab.org/tutorials/08_Plot_data/Plotting_ICA_components.html",
        "mcp_tool": "eeglab_plot_components",
        "official_scope": "Component spectral contribution.",
    },
    {
        "figure_family": "Component head plots",
        "status": "required",
        "official_anchor": "EEGLAB-ICA-001",
        "official_url": "https://eeglab.org/tutorials/08_Plot_data/Plotting_ICA_components.html",
        "mcp_tool": "eeglab_plot_components",
        "official_scope": "Component scalp projection review.",
    },
    {
        "figure_family": "Component ERP envelopes",
        "status": "conditional",
        "official_anchor": "EEGLAB-ICA-001",
        "official_url": "https://eeglab.org/tutorials/08_Plot_data/Plotting_ICA_components.html",
        "mcp_tool": "eeglab_plot_components",
        "official_scope": "Component contribution to ERP morphology.",
    },
    {
        "figure_family": "Component ERP-image",
        "status": "conditional",
        "official_anchor": "EEGLAB-ICA-001",
        "official_url": "https://eeglab.org/tutorials/08_Plot_data/Plotting_ICA_components.html",
        "mcp_tool": "eeglab_plot_components",
        "official_scope": "Single-component trial sorting.",
    },
    {
        "figure_family": "Component time-frequency",
        "status": "conditional",
        "official_anchor": "EEGLAB-TF-001",
        "official_url": "https://eeglab.org/tutorials/08_Plot_data/Time-Frequency_decomposition.html",
        "mcp_tool": "eeglab_plot_timefreq",
        "official_scope": "Component ERSP / ITC dynamics.",
    },
]


def render_markdown() -> str:
    return render_module_doc(MODULE, FIGURE_FAMILIES)


if __name__ == "__main__":
    print(render_markdown())
