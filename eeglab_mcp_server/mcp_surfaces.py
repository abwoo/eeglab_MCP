"""Read-only MCP prompt and resource surface definitions."""

from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT_DIR / "skills" / "eeglab-analysis"
DOCS_DIR = ROOT_DIR / "docs"

PROMPT_DEFINITIONS: dict[str, dict[str, str]] = {
    "eeglab_project_intake": {
        "title": "EEGLAB Project Intake",
        "description": "Start a strict EEG research project by gathering goal, scale, data shape, events, montage, outputs, and constraints.",
        "text": (
            "Use this intake before running EEG processing. Ask for or infer: research goal/hypothesis, "
            "project scale, subject/session structure, EEG file format, sampling rate, event labels, "
            "montage/reference/channel-location status, required outputs, and whether group/STUDY analysis is needed. "
            "Then call eeglab_project_plan or eeglab_workflow_recommend with all known facts and use its qc_gates, "
            "gate_results, and source_claim_ids before destructive steps."
        ),
    },
    "eeglab_strict_qc_protocol": {
        "title": "EEGLAB Strict QC Protocol",
        "description": "Inspect recording/provenance metadata before preprocessing or analysis.",
        "text": (
            "Run eeglab_init, eeglab_load_data, eeglab_qc_report, eeglab_info, eeglab_get_events, and eeglab_history. "
            "Report source path, sampling rate, duration, data shape, channel count, channel-location coverage, reference/montage, "
            "event labels/counts/latencies, processing-history availability, plugin limitations, and raw-preservation strategy. "
            "Do not make clinical claims."
        ),
    },
    "eeglab_dual_mcp_routing": {
        "title": "EEGLAB + MATLAB MCP Routing",
        "description": "Route work when both eeglab and general matlab MCP servers are available.",
        "text": (
            "Use eeglab first for EEG/EEGLAB data loading, QC, event audit, preprocessing, ICA, ERP, spectral/time-frequency, "
            "source, STUDY, and EEGLAB figures. Use matlab MCP for generic MATLAB scripts, custom matrix/statistical code, "
            "or non-EEGLAB toolboxes. Treat the servers as workspace-isolated sessions; use file handoff via .set/.fdt, "
            ".mat, .csv, .png, or reports. Never assume EEG variables are shared across MCP servers."
        ),
    },
    "eeglab_report_template": {
        "title": "EEGLAB Research Report Template",
        "description": "Structure a concise reproducible EEG processing report.",
        "text": (
            "Report in this order: recording/provenance facts, user goal and assumptions, QC gates, processing steps, "
            "exact parameters, outputs/files, failures/recovery, limitations, and next recommended analysis. Include filter cutoffs, "
            "line-noise handling, rereference, bad-channel handling, ICA/ICLabel decisions, epoch/baseline windows, frequency ranges, "
            "rejected data/components, and software/plugin limitations."
        ),
    },
    "eeglab_erp_research_entry": {
        "title": "ERP Research Entry",
        "description": "Start ERP work with event semantics, epoch/baseline, and reporting gates.",
        "text": (
            "For ERP work, first confirm the research question, condition labels, event-code semantics, epoch window, "
            "baseline window, channels/ROIs, reference, and output tables/figures. Call eeglab_project_plan or "
            "eeglab_workflow_recommend, then eeglab_event_semantics_audit and eeglab_method_preflight before epoching. "
            "Do not epoch around boundaries, impedance, excluded markers, or segment-only start/end markers."
        ),
    },
    "eeglab_resting_research_entry": {
        "title": "Resting Research Entry",
        "description": "Start resting-state spectral/connectivity work with continuous-data and artifact gates.",
        "text": (
            "For resting-state work, confirm continuous raw availability, eyes-open/eyes-closed/task-block context, "
            "reference/montage, line-noise frequency, artifact policy, and spectral/connectivity outputs. Prefer quick_qc "
            "and official preflight for derivative processing before filtering. Do not treat epoched-only data as "
            "resting-state data unless the design explicitly supports it."
        ),
    },
    "eeglab_time_frequency_entry": {
        "title": "Time-Frequency Research Entry",
        "description": "Start ERSP/ITC work with event, cycles, baseline, and frequency-range gates.",
        "text": (
            "For ERSP/ITC work, confirm condition triggers, epoch length, baseline interval, channels/ROIs, frequency range, "
            "cycles/wavelet settings, and multiple-comparison/reporting plan. Call eeglab_event_semantics_audit and "
            "eeglab_method_preflight before epoching/time-frequency analysis, then report ERSP/ITC parameters and limitations."
        ),
    },
    "eeglab_ica_cleanup_entry": {
        "title": "ICA Cleanup Entry",
        "description": "Start ICA/ICLabel cleanup with rank, plugin, and review gates.",
        "text": (
            "For ICA cleanup, confirm continuous-data suitability, filtering/rank/reference choices, bad-channel handling, "
            "ICA algorithm, ICLabel availability, component review policy, and save-as-new-output path. Run eeglab_plugin_check "
            "and eeglab_method_preflight for ICA/ICLabel-dependent work. Do not auto-remove components without reporting "
            "thresholds and rationale."
        ),
    },
    "eeglab_bids_study_entry": {
        "title": "BIDS/STUDY Research Entry",
        "description": "Start multi-subject BIDS/STUDY work with metadata, design, and group-statistics gates.",
        "text": (
            "For BIDS/STUDY work, confirm subject/session layout, task/event metadata, design variables, single-subject "
            "preprocessing protocol, output measures, alpha, correction method, and BIDS plugin availability. Use eeglab first "
            "for STUDY creation/design/statistics after eeglab_method_preflight; use matlab MCP only for custom computations "
            "via file handoff."
        ),
    },
    "eeglab_source_connectivity_entry": {
        "title": "Source/Connectivity Entry",
        "description": "Start source or connectivity work with montage, ICA, DIPFIT, and interpretation gates.",
        "text": (
            "For source/connectivity work, confirm channel-location coverage, reference, ICA/source model availability, DIPFIT "
            "resources, selected components/channels, frequency range, and interpretation limits. Run eeglab_method_preflight "
            "before source tools. Do not claim anatomical certainty or source-level results from missing montage, missing ICA, "
            "or unreported model assumptions."
        ),
    },
}

RESOURCE_FILES: dict[str, tuple[str, Path, str]] = {
    "eeglab://skill/SKILL.md": (
        "EEGLAB Analysis Skill",
        SKILL_DIR / "SKILL.md",
        "Primary EEG research workflow skill used by clients that support skills.",
    ),
    "eeglab://references/workflows.md": (
        "EEGLAB Workflow Reference",
        SKILL_DIR / "references" / "workflows.md",
        "Workflow recipes for inspection, preprocessing, ERP, time-frequency, ICA, STUDY, and source workflows.",
    ),
    "eeglab://references/branch-workflow-matrix.md": (
        "EEGLAB Branch Workflow Matrix",
        SKILL_DIR / "references" / "branch-workflow-matrix.md",
        "Canonical branch workflow matrix defining required, conditional, and forbidden steps for ERP, resting-state, time-frequency, source, and STUDY analysis.",
    ),
    "eeglab://references/figure-atlas.md": (
        "EEGLAB Figure Atlas",
        SKILL_DIR / "references" / "figure-atlas.md",
        "Canonical required, conditional, and guidance-only figure families for each analysis branch.",
    ),
    "eeglab://references/tools.md": (
        "EEGLAB Tool Reference",
        SKILL_DIR / "references" / "tools.md",
        "Tool groups, routing rules, common parameters, and project-scale guardrails.",
    ),
    "eeglab://references/setup.md": (
        "EEGLAB Setup Reference",
        SKILL_DIR / "references" / "setup.md",
        "MCP and skill setup guidance, including MATLAB MCP pairing and verification.",
    ),
    "eeglab://references/official-method-map.md": (
        "EEGLAB Skill Official Method Map",
        SKILL_DIR / "references" / "official-method-map.md",
        "Skill-side router map for official method profiles and gated MCP tools.",
    ),
    "eeglab://references/gate-policy.md": (
        "EEGLAB Skill Gate Policy",
        SKILL_DIR / "references" / "gate-policy.md",
        "Skill-side hard-gate and override handling policy.",
    ),
    "eeglab://references/method-gates.md": (
        "EEGLAB Method Gates Reference",
        SKILL_DIR / "references" / "method-gates.md",
        "Method-family preflight inputs, high-risk gates, and override requirements.",
    ),
    "eeglab://references/acquisition-to-derivatives.md": (
        "EEGLAB Acquisition To Derivatives Reference",
        SKILL_DIR / "references" / "acquisition-to-derivatives.md",
        "Raw preservation, acquisition metadata, BIDS-style sidecars, and derivative output policy.",
    ),
    "eeglab://references/event-semantics.md": (
        "EEGLAB Event Semantics Reference",
        SKILL_DIR / "references" / "event-semantics.md",
        "Marker classification rules before epoching or event-locked claims.",
    ),
    "eeglab://references/preprocessing-decision-tree.md": (
        "EEGLAB Preprocessing Decision Tree",
        SKILL_DIR / "references" / "preprocessing-decision-tree.md",
        "Preprocessing order, gate context, and parameter record expectations.",
    ),
    "eeglab://references/ica-iclabel-policy.md": (
        "EEGLAB ICA And ICLabel Policy",
        SKILL_DIR / "references" / "ica-iclabel-policy.md",
        "ICA, ICLabel, and component-removal preflight and reporting rules.",
    ),
    "eeglab://references/bids-study-policy.md": (
        "EEGLAB BIDS And STUDY Policy",
        SKILL_DIR / "references" / "bids-study-policy.md",
        "BIDS/STUDY/group-statistics gate and routing rules.",
    ),
    "eeglab://references/source-policy.md": (
        "EEGLAB Source Localization Policy",
        SKILL_DIR / "references" / "source-policy.md",
        "DIPFIT/source-localization prerequisites and report limits.",
    ),
    "eeglab://references/report-protocol-templates.md": (
        "EEGLAB Report And Protocol Templates",
        SKILL_DIR / "references" / "report-protocol-templates.md",
        "Reusable recording, parameter, official-gate, and limitation report sections.",
    ),
    "eeglab://references/statistics-reporting.md": (
        "EEGLAB Statistics And Reporting Reference",
        SKILL_DIR / "references" / "statistics-reporting.md",
        "STUDY/LIMO/SIFT statistics gates and minimum report fields.",
    ),
    "eeglab://official/references.md": (
        "EEGLAB Official Research References",
        DOCS_DIR / "research-standard.md",
        "Official EEGLAB, SCCN, and plugin references that anchor research-level workflow policy.",
    ),
    "eeglab://official/topic-index.md": (
        "EEGLAB Official Topic Index",
        DOCS_DIR / "official-topic-index.md",
        "Official EEGLAB/SCCN topic coverage index with support_level, claim IDs, and MCP routes.",
    ),
    "eeglab://official/support-matrix.md": (
        "EEGLAB Official Support Matrix",
        DOCS_DIR / "official-support-matrix.md",
        "Support-level taxonomy for executable, gated_guidance, indexed_only, and out_of_scope topics.",
    ),
    "eeglab://official/tool-support-matrix.md": (
        "EEGLAB Official Tool Support Matrix",
        DOCS_DIR / "official-tool-support-matrix.md",
        "Tool-level support labels, official method gates, read/write effects, and report requirements.",
    ),
    "eeglab://official/method-map.md": (
        "EEGLAB Official Method Map",
        DOCS_DIR / "official-method-map.md",
        "Mapping from MCP tools to official EEGLAB method profiles and claim IDs.",
    ),
    "eeglab://official/gate-policy.md": (
        "EEGLAB Official Gate Policy",
        DOCS_DIR / "official-gate-policy.md",
        "Hard-gate and explicit-override policy for high-risk EEG processing.",
    ),
    "eeglab://official/plugin-map.md": (
        "EEGLAB Official Plugin Map",
        DOCS_DIR / "official-plugin-map.md",
        "Official plugin dependency map for clean_rawdata, ICLabel, DIPFIT, BIDS/STUDY, LIMO, and SIFT.",
    ),
    "eeglab://official/plugin-matrix.md": (
        "EEGLAB Official Plugin Matrix",
        DOCS_DIR / "official-plugin-map.md",
        "Plugin support matrix with support levels, function probes, claim IDs, dependent profiles, and next steps.",
    ),
    "eeglab://official/plugin-family-catalog.md": (
        "EEGLAB Official Plugin Family Catalog",
        DOCS_DIR / "official-plugin-family-catalog.md",
        "Discovery-only catalog for the broader official EEGLAB plugin families surfaced on the plugins page.",
    ),
    "eeglab://official/risk-matrix.md": (
        "EEGLAB Official Risk Matrix",
        DOCS_DIR / "official-risk-matrix.md",
        "Method-risk gates for preprocessing, ICA, ERP, spectral/connectivity, STUDY, source, LIMO, and SIFT.",
    ),
    "eeglab://official/report-field-matrix.md": (
        "EEGLAB Official Report Field Matrix",
        DOCS_DIR / "official-report-field-matrix.md",
        "Minimum reproducible report fields for recording, events, preprocessing, analysis, figure atlas, outputs, gates, and limitations.",
    ),
    "eeglab://official/figure-atlas.md": (
        "EEGLAB Official Figure Atlas",
        DOCS_DIR / "figure-atlas.md",
        "Canonical static figure families, metadata, and interpretation scope by analysis branch.",
    ),
    "eeglab://scripts/advanced_figures/README.md": (
        "EEGLAB Advanced Figure Gallery",
        ROOT_DIR / "scripts" / "advanced_figures" / "README.md",
        "Default browsable companion to the official figure atlas, with module-level Markdown and Python gallery entry points.",
    ),
}
