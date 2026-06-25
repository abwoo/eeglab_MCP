"""Default advanced source / connectivity figure gallery."""

from __future__ import annotations

try:
    from .catalog import render_module_doc
except ImportError:  # pragma: no cover - direct script execution support
    from catalog import render_module_doc

MODULE = {
    "title": "Source and Connectivity Advanced Figure Gallery",
    "summary": "Source-space and connectivity visuals stay guidance-heavy.",
    "python_module": "scripts/advanced_figures/source_gallery.py",
    "markdown_path": "scripts/advanced_figures/source.md",
    "mcp_route": "eeglab_source_localization / eeglab_plot_connectivity",
    "branch": "Source localization / connectivity",
}

FIGURE_FAMILIES = [
    {
        "figure_family": "Source / dipole review",
        "status": "required",
        "official_anchor": "EEGLAB-DIPFIT-001",
        "official_url": "https://eeglab.org/plugins/dipfit/",
        "mcp_tool": "eeglab_source_localization",
        "official_scope": "Model fit quality and residual variance review.",
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
        "figure_family": "ROI 2-D / 3-D review",
        "status": "guidance_only",
        "official_anchor": "EEGLAB-ROICONNECT-001",
        "official_url": "https://eeglab.org/plugins/roiconnect/",
        "mcp_tool": "ROIconnect",
        "official_scope": "Source-space review aid only.",
    },
    {
        "figure_family": "SIFT time-frequency grids",
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
