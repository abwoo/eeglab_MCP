#!/usr/bin/env python3
"""
EEG Analysis Report Generator

Generates a standardized research-grade EEG analysis report from
EEGLAB processing results. Follows official EEGLAB/SCCN reporting
guidelines and COBIDAS-style metadata expectations.

Usage:
    python generate_eeg_report.py --input results.json --output report.md
    python generate_eeg_report.py --input results.json --output report.html --format html
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class EEGReportGenerator:
    """Generate standardized EEG analysis reports."""

    def __init__(self, results: Dict[str, Any]):
        self.results = results
        self.report_sections = []

    def generate_markdown(self) -> str:
        """Generate a complete Markdown report."""
        sections = [
            self._title_section(),
            self._abstract_section(),
            self._recording_section(),
            self._preprocessing_section(),
            self._analysis_section(),
            self._branch_workflow_section(),
            self._figure_atlas_section(),
            self._figures_section(),
            self._compliance_section(),
            self._results_section(),
            self._discussion_section(),
            self._limitations_section(),
            self._appendix_section(),
        ]
        return "\n\n".join(sections)

    def _title_section(self) -> str:
        """Generate title and metadata."""
        title = self.results.get("title", "EEG Analysis Report")
        date = self.results.get("date", datetime.now().strftime("%Y-%m-%d"))
        author = self.results.get("author", "EEGLAB MCP Agent")

        return f"""# {title}

**Date:** {date}
**Author:** {author}
**Software:** EEGLAB MCP Agent"""

    def _abstract_section(self) -> str:
        """Generate abstract section."""
        abstract = self.results.get("abstract", "No abstract provided.")
        return f"""## Abstract

{abstract}"""

    def _recording_section(self) -> str:
        """Generate recording and acquisition section."""
        recording = self.results.get("recording", {})

        lines = ["## Recording And Acquisition"]
        lines.append("")
        lines.append("| Parameter | Value |")
        lines.append("|-----------|-------|")

        fields = [
            ("Input Path", "input_path"),
            ("Output Path", "output_path"),
            ("Set Name", "set_name"),
            ("File Name", "file_name"),
            ("Sampling Rate", "sampling_rate"),
            ("Duration", "duration"),
            ("Data Points", "data_points"),
            ("Channels", "channels"),
            ("Channel Locations", "channel_locations"),
            ("Reference", "reference"),
            ("Montage", "montage"),
            ("Event Count", "event_count"),
            ("Event Labels", "event_labels"),
            ("Event Latency Range", "event_latency_range"),
            ("History Available", "history_available"),
            ("ICA Status", "ica_status"),
            ("Power Line Frequency", "power_line_frequency"),
            ("Acquisition Filters", "acquisition_filters"),
            ("Raw Files Preserved", "raw_files_preserved"),
        ]

        for label, key in fields:
            value = recording.get(key, "N/A")
            lines.append(f"| {label} | {value} |")

        return "\n".join(lines)

    def _compliance_section(self) -> str:
        """Generate workflow compliance and provenance coverage section."""
        tool_coverage = self.results.get("tool_coverage", {})
        reference_coverage = self.results.get("reference_coverage", {})
        official_doc_coverage = self.results.get("official_document_coverage", {})
        method_preflights = self.results.get("method_preflights", [])
        report_field_coverage = self.results.get("report_field_coverage", {})
        source_claim_ids = self.results.get("source_claim_ids", [])
        branch = self.results.get("branch_workflow", {})

        lines = ["## Workflow Compliance And Provenance"]
        lines.append("")

        if tool_coverage:
            lines.append("### Tool Coverage")
            lines.append("")
            lines.append("| Field | Value |")
            lines.append("|-------|-------|")
            for key, value in tool_coverage.items():
                lines.append(f"| {key} | {self._format_value(value)} |")
            lines.append("")

        if reference_coverage or official_doc_coverage:
            lines.append("### Reference Coverage")
            lines.append("")
            lines.append("| Source Set | Coverage | Missing |")
            lines.append("|------------|----------|---------|")
            if reference_coverage:
                lines.append(
                    "| Skill References | "
                    f"{self._format_value(reference_coverage.get('read', 'N/A'))}/"
                    f"{self._format_value(reference_coverage.get('expected', 'N/A'))} | "
                    f"{self._format_value(reference_coverage.get('missing', []))} |"
                )
            if official_doc_coverage:
                lines.append(
                    "| Official Docs | "
                    f"{self._format_value(official_doc_coverage.get('read', 'N/A'))}/"
                    f"{self._format_value(official_doc_coverage.get('expected', 'N/A'))} | "
                    f"{self._format_value(official_doc_coverage.get('missing', []))} |"
                )
            lines.append("")

        if method_preflights:
            lines.append("### Method Preflights")
            lines.append("")
            lines.append("| Method | Gate Status | Missing Requirements | Source Claims |")
            lines.append("|--------|-------------|----------------------|---------------|")
            for item in method_preflights:
                lines.append(
                    "| "
                    f"{self._format_value(item.get('method', 'N/A'))} | "
                    f"{self._format_value(item.get('gate_status', 'N/A'))} | "
                    f"{self._format_value(item.get('missing_requirements', []))} | "
                    f"{self._format_value(item.get('source_claim_ids', []))} |"
                )
            lines.append("")

        if report_field_coverage:
            lines.append("### Report Field Coverage")
            lines.append("")
            lines.append("| Field Group | Status | Notes |")
            lines.append("|-------------|--------|-------|")
            for key, value in report_field_coverage.items():
                if isinstance(value, dict):
                    status = value.get("status", "N/A")
                    notes = value.get("notes", "")
                else:
                    status = value
                    notes = ""
                lines.append(f"| {key} | {self._format_value(status)} | {self._format_value(notes)} |")
            lines.append("")

        required_families = self.results.get("required_figure_families", [])
        conditional_families = self.results.get("conditional_figure_families", [])
        guidance_families = self.results.get("guidance_only_figure_families", [])
        figure_atlas = self.results.get("figure_atlas", [])
        figure_descriptions = self.results.get("figure_descriptions", [])
        figure_generation_notes = self.results.get("figure_generation_notes", [])
        if required_families or conditional_families or guidance_families or figure_atlas or figure_descriptions or figure_generation_notes:
            lines.append("### Figure Coverage")
            lines.append("")
            lines.append("| Family Type | Families |")
            lines.append("|-------------|----------|")
            lines.append(f"| required | {self._format_value(required_families)} |")
            lines.append(f"| conditional | {self._format_value(conditional_families)} |")
            lines.append(f"| guidance_only | {self._format_value(guidance_families)} |")
            lines.append(f"| atlas_entries | {len(figure_atlas)} |")
            lines.append("")
            if figure_atlas:
                lines.append("### Figure Atlas")
                lines.append("")
                lines.append("| Figure Type | Status | Branch | Channel/ROI | Latency | Frequency | Tool Source | Interpretation Scope |")
                lines.append("|-------------|--------|--------|-------------|---------|-----------|-------------|----------------------|")
                for item in figure_atlas:
                    if isinstance(item, dict):
                        lines.append(
                            "| "
                            f"{self._format_value(item.get('figure_type', 'N/A'))} | "
                            f"{self._format_value(item.get('figure_status', 'N/A'))} | "
                            f"{self._format_value(item.get('branch_id', 'N/A'))} | "
                            f"{self._format_value(item.get('channel_or_roi', 'N/A'))} | "
                            f"{self._format_value(item.get('latency_window', 'N/A'))} | "
                            f"{self._format_value(item.get('frequency_window', 'N/A'))} | "
                            f"{self._format_value(item.get('tool_source', 'N/A'))} | "
                            f"{self._format_value(item.get('interpretation_scope', 'N/A'))} |"
                        )
                lines.append("")
            if figure_descriptions:
                lines.append("### Figure Descriptions")
                lines.append("")
                for item in self._text_items(figure_descriptions):
                    lines.append(f"- {item}")
                lines.append("")
            if figure_generation_notes:
                lines.append("### Figure Generation Notes")
                lines.append("")
                for note in self._text_items(figure_generation_notes):
                    lines.append(f"- {note}")
                lines.append("")

        if source_claim_ids:
            lines.append("### Source Claim IDs")
            lines.append("")
            for claim_id in source_claim_ids:
                lines.append(f"- {claim_id}")
            lines.append("")

        if branch:
            lines.append("### Branch Workflow Coverage")
            lines.append("")
            completeness = branch.get("branch_completeness", {})
            for key in ("branch_id", "branch_label", "branch_mode", "analysis_type", "branch_variant"):
                lines.append(f"- {key}: {self._format_value(branch.get(key, 'N/A'))}")
            lines.append(f"- completeness_status: {self._format_value(completeness.get('status', 'N/A'))}")
            lines.append(f"- universal_preamble_steps: {self._format_value(branch.get('universal_preamble_steps', []))}")
            lines.append(f"- ordered_branch_steps: {self._format_value(branch.get('ordered_branch_steps', []))}")
            lines.append(f"- missing_required_steps: {self._format_value(completeness.get('missing_required_steps', []))}")
            lines.append(f"- blocked_steps: {self._format_value(completeness.get('blocked_steps', []))}")
            lines.append(f"- required_figures: {self._format_value(completeness.get('required_figures', []))}")
            lines.append(
                f"- required_figure_families: {self._format_value(completeness.get('required_figure_families', []))}"
            )
            lines.append(
                f"- conditional_figure_families: {self._format_value(completeness.get('conditional_figure_families', []))}"
            )
            lines.append(
                f"- guidance_only_figure_families: {self._format_value(completeness.get('guidance_only_figure_families', []))}"
            )
            lines.append(f"- figure_atlas: {self._format_value(completeness.get('figure_atlas', []))}")
            lines.append(f"- figure_paths: {self._format_value(completeness.get('figure_paths', []))}")
            lines.append(f"- required_outputs: {self._format_value(completeness.get('required_outputs', []))}")
            lines.append(f"- output_paths: {self._format_value(completeness.get('output_paths', []))}")
            lines.append("")

        if not any(
            [
                tool_coverage,
                reference_coverage,
                official_doc_coverage,
                method_preflights,
                report_field_coverage,
                source_claim_ids,
                branch,
            ]
        ):
            lines.append("Workflow compliance metadata was not provided.")

        return "\n".join(lines)

    def _figure_atlas_section(self) -> str:
        """Generate the canonical figure atlas section."""
        atlas = self.results.get("figure_atlas", [])
        if not atlas:
            return "## Figure Atlas\n\nNo figure atlas metadata was provided."

        lines = ["## Figure Atlas", ""]
        lines.append("| Figure Type | Status | Branch | Channel/ROI | Latency Window | Frequency Window | Tool Source | Official Anchor | Scope | Path |")
        lines.append("|-------------|--------|--------|-------------|-----------------|-------------------|-------------|-----------------|-------|------|")
        for item in atlas:
            if not isinstance(item, dict):
                continue
            lines.append(
                "| "
                f"{self._format_value(item.get('figure_type', 'N/A'))} | "
                f"{self._format_value(item.get('figure_status', 'N/A'))} | "
                f"{self._format_value(item.get('branch_id', 'N/A'))} | "
                f"{self._format_value(item.get('channel_or_roi', 'N/A'))} | "
                f"{self._format_value(item.get('latency_window', 'N/A'))} | "
                f"{self._format_value(item.get('frequency_window', 'N/A'))} | "
                f"{self._format_value(item.get('tool_source', 'N/A'))} | "
                f"{self._format_value(item.get('official_anchor', 'N/A'))} | "
                f"{self._format_value(item.get('interpretation_scope', 'N/A'))} | "
                f"{self._format_value(item.get('figure_path', item.get('path', 'N/A')))} |"
            )
        return "\n".join(lines)

    def _preprocessing_section(self) -> str:
        """Generate preprocessing parameters section."""
        preprocessing = self.results.get("preprocessing", {})

        lines = ["## Preprocessing Parameters"]
        lines.append("")
        lines.append("| Step | Parameters |")
        lines.append("|------|------------|")

        steps = [
            ("Filter", "filter"),
            ("Line Noise", "line_noise"),
            ("Resampling", "resampling"),
            ("Re-reference", "rereference"),
            ("Bad Channel Handling", "bad_channels"),
            ("ASR", "asr"),
            ("ICA Algorithm", "ica_algorithm"),
            ("ICLabel Thresholds", "iclabel_thresholds"),
            ("Components Removed", "components_removed"),
            ("Epoch Window", "epoch_window"),
            ("Baseline Window", "baseline_window"),
            ("Rejection Criteria", "rejection_criteria"),
        ]

        for label, key in steps:
            value = preprocessing.get(key, "N/A")
            if isinstance(value, dict):
                value = ", ".join(f"{k}: {v}" for k, v in value.items())
            lines.append(f"| {label} | {value} |")

        return "\n".join(lines)

    @staticmethod
    def _format_value(value: Any) -> str:
        """Format nested values for compact Markdown table cells."""
        if value is None:
            return "N/A"
        if isinstance(value, (list, tuple, set)):
            return ", ".join(str(item) for item in value) if value else "None"
        if isinstance(value, dict):
            return ", ".join(f"{k}: {v}" for k, v in value.items()) if value else "None"
        return str(value)

    @staticmethod
    def _text_items(value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, (list, tuple, set)):
            return [str(item) for item in value if str(item)]
        return [str(value)]

    def _analysis_section(self) -> str:
        """Generate analysis parameters section."""
        analysis = self.results.get("analysis", {})

        lines = ["## Analysis Parameters"]
        lines.append("")

        # ERP Analysis
        erp = analysis.get("erp", {})
        if erp:
            lines.append("### ERP Analysis")
            lines.append("")
            lines.append("| Parameter | Value |")
            lines.append("|-----------|-------|")
            for key, value in erp.items():
                lines.append(f"| {key} | {value} |")
            lines.append("")

        # Spectral Analysis
        spectral = analysis.get("spectral", {})
        if spectral:
            lines.append("### Spectral Analysis")
            lines.append("")
            lines.append("| Parameter | Value |")
            lines.append("|-----------|-------|")
            for key, value in spectral.items():
                lines.append(f"| {key} | {value} |")
            lines.append("")

        # Time-Frequency Analysis
        timefreq = analysis.get("timefreq", {})
        if timefreq:
            lines.append("### Time-Frequency Analysis")
            lines.append("")
            lines.append("| Parameter | Value |")
            lines.append("|-----------|-------|")
            for key, value in timefreq.items():
                lines.append(f"| {key} | {value} |")
            lines.append("")

        # Connectivity Analysis
        connectivity = analysis.get("connectivity", {})
        if connectivity:
            lines.append("### Connectivity Analysis")
            lines.append("")
            lines.append("| Parameter | Value |")
            lines.append("|-----------|-------|")
            for key, value in connectivity.items():
                lines.append(f"| {key} | {value} |")
            lines.append("")

        # Source Localization
        source = analysis.get("source", {})
        if source:
            lines.append("### Source Localization")
            lines.append("")
            lines.append("| Parameter | Value |")
            lines.append("|-----------|-------|")
            for key, value in source.items():
                lines.append(f"| {key} | {value} |")
            lines.append("")

        return "\n".join(lines)

    def _branch_workflow_section(self) -> str:
        """Generate branch workflow section."""
        branch = self.results.get("branch_workflow", {})
        if not branch:
            return "## Branch Workflow\n\nBranch coverage metadata was not provided."

        completeness = branch.get("branch_completeness", {})
        lines = ["## Branch Workflow", ""]
        lines.append("| Field | Value |")
        lines.append("|------|-------|")
        for key in ("branch_id", "branch_label", "branch_mode", "analysis_type", "branch_variant"):
            lines.append(f"| {key} | {self._format_value(branch.get(key, 'N/A'))} |")
        lines.append(f"| completeness_status | {self._format_value(completeness.get('status', 'N/A'))} |")
        lines.append("")
        lines.append("### Universal Preamble")
        for step in branch.get("universal_preamble_steps", []):
            lines.append(f"- {step}")
        lines.append("")
        lines.append("### Ordered Branch Steps")
        for step in branch.get("ordered_branch_steps", []):
            lines.append(f"- {step}")
        lines.append("")
        lines.append("### Branch Completeness")
        lines.append("")
        lines.append("| Field | Value |")
        lines.append("|------|-------|")
        lines.append(f"| branch_completeness_status | {self._format_value(completeness.get('status', 'N/A'))} |")
        for key in (
            "coverage_notes",
            "blocker_messages",
            "missing_required_steps",
            "blocked_steps",
            "missing_required_figures",
            "missing_required_outputs",
            "required_figures",
            "conditional_figures",
            "required_outputs",
            "completed_steps",
            "figure_paths",
            "output_paths",
        ):
            lines.append(f"| {key} | {self._format_value(completeness.get(key, []))} |")
        return "\n".join(lines)

    def _figures_section(self) -> str:
        """Generate figures section with images."""
        figures = self.results.get("figures", [])

        lines = ["## Figures"]
        lines.append("")

        if not figures:
            lines.append("No figures generated.")
            return "\n".join(lines)

        for i, fig in enumerate(figures, 1):
            fig_path = fig.get("path", "")
            fig_caption = fig.get("caption", f"Figure {i}")
            fig_description = fig.get("description", "")

            lines.append(f"### Figure {i}: {fig_caption}")
            lines.append("")
            if fig_description:
                lines.append(fig_description)
                lines.append("")
            if fig_path:
                lines.append(f"![{fig_caption}]({fig_path})")
                lines.append("")

        return "\n".join(lines)

    def _results_section(self) -> str:
        """Generate results section."""
        results = self.results.get("results", {})

        lines = ["## Results"]
        lines.append("")

        if not results:
            lines.append("No results to report.")
            return "\n".join(lines)

        for key, value in results.items():
            lines.append(f"### {key.replace('_', ' ').title()}")
            lines.append("")
            if isinstance(value, dict):
                lines.append("| Metric | Value |")
                lines.append("|--------|-------|")
                for k, v in value.items():
                    lines.append(f"| {k} | {v} |")
            else:
                lines.append(str(value))
            lines.append("")

        return "\n".join(lines)

    def _discussion_section(self) -> str:
        """Generate discussion section."""
        discussion = self.results.get("discussion", "No discussion provided.")

        return f"""## Discussion

{discussion}"""

    def _limitations_section(self) -> str:
        """Generate limitations section."""
        limitations = self.results.get("limitations", [])
        gate_results = self.results.get("gate_results", {})
        override_used = self.results.get("override_used", False)

        lines = ["## Limitations"]
        lines.append("")

        if limitations:
            for lim in limitations:
                lines.append(f"- {lim}")
        else:
            lines.append("- No specific limitations noted.")

        lines.append("")
        lines.append("**Official Gate Status:**")
        lines.append("")

        if gate_results:
            for claim_id, status in gate_results.items():
                lines.append(f"- {claim_id}: {status}")
        else:
            lines.append("- Gate coverage not provided.")

        if override_used:
            lines.append("")
            lines.append("**Override Applied:**")
            lines.append("")
            override_reason = self.results.get("override_reason", "No reason provided.")
            lines.append(f"- Reason: {override_reason}")

        lines.append("")
        lines.append("**Disclaimer:** These are EEG signal-processing results, not clinical conclusions. No anatomical certainty is claimed from missing montage/model data.")

        return "\n".join(lines)

    def _appendix_section(self) -> str:
        """Generate appendix with additional information."""
        appendix = self.results.get("appendix", {})

        lines = ["## Appendix"]
        lines.append("")

        # Software versions
        software = appendix.get("software", {})
        if software:
            lines.append("### Software And Versions")
            lines.append("")
            for key, value in software.items():
                lines.append(f"- **{key}:** {value}")
            lines.append("")

        # Plugin status
        plugins = appendix.get("plugins", {})
        if plugins:
            lines.append("### Plugin Status")
            lines.append("")
            for plugin, status in plugins.items():
                lines.append(f"- **{plugin}:** {status}")
            lines.append("")

        # Generated files
        files = appendix.get("generated_files", [])
        if files:
            lines.append("### Generated Files")
            lines.append("")
            for file_info in files:
                if isinstance(file_info, dict):
                    lines.append(f"- `{file_info.get('path', 'N/A')}`: {file_info.get('description', '')}")
                else:
                    lines.append(f"- `{file_info}`")
            lines.append("")

        return "\n".join(lines)

    def generate_html(self) -> str:
        """Generate a complete HTML report with proper formatting."""
        title = self.results.get("title", "EEG Analysis Report")
        date = self.results.get("date", datetime.now().strftime("%Y-%m-%d"))
        author = self.results.get("author", "EEGLAB MCP Agent")

        # Build HTML sections
        sections = []

        # Title
        sections.append(f"""<h1>{title}</h1>
<p><strong>Date:</strong> {date}<br>
<strong>Author:</strong> {author}<br>
<strong>Software:</strong> EEGLAB MCP Agent</p>""")

        # Abstract
        abstract = self.results.get("abstract", "No abstract provided.")
        sections.append(f"<h2>Abstract</h2><p>{abstract}</p>")

        # Recording
        recording = self.results.get("recording", {})
        if recording:
            sections.append("<h2>Recording And Acquisition</h2>")
            sections.append("<table><tr><th>Parameter</th><th>Value</th></tr>")
            for key, value in recording.items():
                label = key.replace("_", " ").title()
                sections.append(f"<tr><td>{label}</td><td>{value}</td></tr>")
            sections.append("</table>")

        # Preprocessing
        preprocessing = self.results.get("preprocessing", {})
        if preprocessing:
            sections.append("<h2>Preprocessing Parameters</h2>")
            sections.append("<table><tr><th>Step</th><th>Parameters</th></tr>")
            for key, value in preprocessing.items():
                label = key.replace("_", " ").title()
                if isinstance(value, dict):
                    value = ", ".join(f"{k}: {v}" for k, v in value.items())
                sections.append(f"<tr><td>{label}</td><td>{value}</td></tr>")
            sections.append("</table>")

        # Analysis
        analysis = self.results.get("analysis", {})
        if any(analysis.values()):
            sections.append("<h2>Analysis Parameters</h2>")
            for analysis_type, params in analysis.items():
                if params:
                    sections.append(f"<h3>{analysis_type.replace('_', ' ').title()}</h3>")
                    sections.append("<table><tr><th>Parameter</th><th>Value</th></tr>")
                    for key, value in params.items():
                        sections.append(f"<tr><td>{key}</td><td>{value}</td></tr>")
                    sections.append("</table>")

        branch = self.results.get("branch_workflow", {})
        if branch:
            sections.append("<h2>Branch Workflow</h2>")
            sections.append("<table><tr><th>Field</th><th>Value</th></tr>")
            for key in ("branch_id", "branch_label", "branch_mode", "analysis_type", "branch_variant"):
                sections.append(f"<tr><td>{key}</td><td>{branch.get(key, 'N/A')}</td></tr>")
            completeness = branch.get("branch_completeness", {})
            sections.append(f"<tr><td>completeness_status</td><td>{completeness.get('status', 'N/A')}</td></tr>")
            sections.append("</table>")
            sections.append("<h3>Universal Preamble</h3><ul>")
            for step in branch.get("universal_preamble_steps", []):
                sections.append(f"<li>{step}</li>")
            sections.append("</ul>")
            sections.append("<h3>Ordered Branch Steps</h3><ul>")
            for step in branch.get("ordered_branch_steps", []):
                sections.append(f"<li>{step}</li>")
            sections.append("</ul>")
            sections.append("<h3>Branch Completeness</h3>")
            sections.append("<table><tr><th>Field</th><th>Value</th></tr>")
            sections.append(f"<tr><td>branch_completeness_status</td><td>{self._format_value(completeness.get('status', 'N/A'))}</td></tr>")
            for key in (
                "coverage_notes",
                "blocker_messages",
                "missing_required_steps",
                "blocked_steps",
                "missing_required_figures",
                "missing_required_outputs",
                "required_figures",
                "conditional_figures",
                "required_figure_families",
                "conditional_figure_families",
                "guidance_only_figure_families",
                "required_outputs",
                "completed_steps",
                "figure_paths",
                "output_paths",
            ):
                sections.append(f"<tr><td>{key}</td><td>{self._format_value(completeness.get(key, []))}</td></tr>")
            sections.append("</table>")
            figure_families = {
                "required": branch.get("required_figure_families", []),
                "conditional": branch.get("conditional_figure_families", []),
                "guidance_only": branch.get("guidance_only_figure_families", []),
            }
            if any(figure_families.values()):
                sections.append("<h3>Figure Coverage</h3>")
                sections.append("<table><tr><th>Family Type</th><th>Families</th></tr>")
                for label, families in figure_families.items():
                    sections.append(f"<tr><td>{label}</td><td>{self._format_value(families)}</td></tr>")
                sections.append("</table>")
            atlas = branch.get("figure_atlas", [])
            if atlas:
                sections.append("<h3>Figure Atlas</h3>")
                sections.append("<table><tr><th>Figure Type</th><th>Status</th><th>Channel/ROI</th><th>Latency Window</th><th>Frequency Window</th><th>Tool Source</th><th>Official Anchor</th><th>Scope</th><th>Path</th></tr>")
                for item in atlas:
                    if isinstance(item, dict):
                        sections.append(
                            "<tr>"
                            f"<td>{item.get('figure_type', 'N/A')}</td>"
                            f"<td>{item.get('figure_status', 'N/A')}</td>"
                            f"<td>{item.get('channel_or_roi', 'N/A')}</td>"
                            f"<td>{item.get('latency_window', 'N/A')}</td>"
                            f"<td>{item.get('frequency_window', 'N/A')}</td>"
                            f"<td>{item.get('tool_source', 'N/A')}</td>"
                            f"<td>{item.get('official_anchor', 'N/A')}</td>"
                            f"<td>{item.get('interpretation_scope', 'N/A')}</td>"
                            f"<td>{item.get('figure_path', item.get('path', 'N/A'))}</td>"
                            "</tr>"
                        )
                sections.append("</table>")

        # Figures
        figures = self.results.get("figures", [])
        if figures:
            sections.append("<h2>Figures</h2>")
            for i, fig in enumerate(figures, 1):
                fig_path = fig.get("path", "")
                fig_caption = fig.get("caption", f"Figure {i}")
                fig_description = fig.get("description", "")
                sections.append(f"<h3>Figure {i}: {fig_caption}</h3>")
                if fig_description:
                    sections.append(f"<p>{fig_description}</p>")
                if fig_path:
                    sections.append(f'<img src="{fig_path}" alt="{fig_caption}" style="max-width: 100%;">')

        # Results
        results = self.results.get("results", {})
        if results:
            sections.append("<h2>Results</h2>")
            for key, value in results.items():
                sections.append(f"<h3>{key.replace('_', ' ').title()}</h3>")
                if isinstance(value, dict):
                    sections.append("<table><tr><th>Metric</th><th>Value</th></tr>")
                    for k, v in value.items():
                        sections.append(f"<tr><td>{k}</td><td>{v}</td></tr>")
                    sections.append("</table>")
                else:
                    sections.append(f"<p>{value}</p>")

        # Discussion
        discussion = self.results.get("discussion", "No discussion provided.")
        sections.append(f"<h2>Discussion</h2><p>{discussion}</p>")

        # Limitations
        limitations = self.results.get("limitations", [])
        gate_results = self.results.get("gate_results", {})
        override_used = self.results.get("override_used", False)

        sections.append("<h2>Limitations</h2>")
        sections.append("<ul>")
        if limitations:
            for lim in limitations:
                sections.append(f"<li>{lim}</li>")
        else:
            sections.append("<li>No specific limitations noted.</li>")
        sections.append("</ul>")

        sections.append("<p><strong>Official Gate Status:</strong></p><ul>")
        if gate_results:
            for claim_id, status in gate_results.items():
                sections.append(f"<li>{claim_id}: {status}</li>")
        else:
            sections.append("<li>Gate coverage not provided.</li>")
        sections.append("</ul>")

        if override_used:
            override_reason = self.results.get("override_reason", "No reason provided.")
            sections.append(f"<p><strong>Override Applied:</strong></p><p>Reason: {override_reason}</p>")

        sections.append('<p><strong>Disclaimer:</strong> These are EEG signal-processing results, not clinical conclusions. No anatomical certainty is claimed from missing montage/model data.</p>')

        # Compliance
        compliance_keys = [
            "tool_coverage",
            "reference_coverage",
            "official_document_coverage",
            "method_preflights",
            "report_field_coverage",
            "source_claim_ids",
        ]
        if any(self.results.get(key) for key in compliance_keys):
            sections.append("<h2>Workflow Compliance And Provenance</h2>")
            for key in compliance_keys:
                value = self.results.get(key)
                if value:
                    sections.append(f"<h3>{key.replace('_', ' ').title()}</h3>")
                    sections.append(f"<pre>{self._format_value(value)}</pre>")

        # Appendix
        appendix = self.results.get("appendix", {})
        if appendix:
            sections.append("<h2>Appendix</h2>")

            software = appendix.get("software", {})
            if software:
                sections.append("<h3>Software And Versions</h3><ul>")
                for key, value in software.items():
                    sections.append(f"<li><strong>{key}:</strong> {value}</li>")
                sections.append("</ul>")

            plugins = appendix.get("plugins", {})
            if plugins:
                sections.append("<h3>Plugin Status</h3><ul>")
                for plugin, status in plugins.items():
                    sections.append(f"<li><strong>{plugin}:</strong> {status}</li>")
                sections.append("</ul>")

            files = appendix.get("generated_files", [])
            if files:
                sections.append("<h3>Generated Files</h3><ul>")
                for file_info in files:
                    if isinstance(file_info, dict):
                        sections.append(f"<li><code>{file_info.get('path', 'N/A')}</code>: {file_info.get('description', '')}</li>")
                    else:
                        sections.append(f"<li><code>{file_info}</code></li>")
                sections.append("</ul>")

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        img {{
            max-width: 100%;
            height: auto;
            margin: 20px 0;
            display: block;
        }}
        h1, h2, h3 {{
            color: #333;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
        }}
        ul {{
            margin: 10px 0;
        }}
        li {{
            margin: 5px 0;
        }}
    </style>
</head>
<body>
{"".join(sections)}
</body>
</html>"""
        return html


def load_results(input_path: str) -> Dict[str, Any]:
    """Load results from JSON file."""
    with open(input_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Generate EEG analysis report")
    parser.add_argument("--input", required=True, help="Input JSON results file")
    parser.add_argument("--output", required=True, help="Output report file")
    parser.add_argument(
        "--format",
        choices=["markdown", "html"],
        default="markdown",
        help="Output format (default: markdown)",
    )

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    results = load_results(args.input)
    generator = EEGReportGenerator(results)

    if args.format == "html":
        report = generator.generate_html()
    else:
        report = generator.generate_markdown()

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Report generated: {args.output}")


if __name__ == "__main__":
    main()
