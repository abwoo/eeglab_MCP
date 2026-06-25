"""Verify official EEGLAB/SCCN alignment artifacts."""

from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from eeglab_mcp_server.official_alignment import (  # noqa: E402
    HIGH_RISK_TOOL_NAMES,
    METHOD_PROFILES,
    OFFICIAL_CLAIMS,
    OFFICIAL_PLUGIN_MATRIX,
    OFFICIAL_SOURCE_SNAPSHOT,
    OFFICIAL_TOPIC_INDEX,
    REPORT_FIELD_MATRIX,
    evaluate_method_preflight,
)
from eeglab_mcp_server.mcp_surfaces import RESOURCE_FILES  # noqa: E402
from eeglab_mcp_server.schemas import workflow_tools  # noqa: E402
from eeglab_mcp_server.tool_definitions import build_tool_definitions  # noqa: E402
from eeglab_mcp_server.tool_registry import (  # noqa: E402
    TOOL_REGISTRY,
    validate_registry,
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def check_claim_map() -> None:
    registry_errors = validate_registry()
    _require(not registry_errors, f"registry errors: {registry_errors}")
    _require(len(OFFICIAL_CLAIMS) >= 10, "expected at least 10 official claims")
    for claim_id, claim in OFFICIAL_CLAIMS.items():
        _require(claim_id.startswith(("EEGLAB-", "BIDS-")), f"bad claim id: {claim_id}")
        for field in ("title", "url", "applies_to", "requirement", "cited_on"):
            _require(field in claim and claim[field], f"{claim_id} missing {field}")
        _require(
            (
                "eeglab.org" in claim["url"]
                or "github.com/sccn" in claim["url"]
                or "bids-specification.readthedocs.io" in claim["url"]
            ),
            f"non-official URL: {claim['url']}",
        )

    for profile_id, profile in METHOD_PROFILES.items():
        _require(profile.get("source_claim_ids"), f"{profile_id} missing source_claim_ids")
        for claim_id in profile["source_claim_ids"]:
            _require(
                claim_id in OFFICIAL_CLAIMS,
                f"{profile_id} references unknown claim {claim_id}",
            )
        _require(profile.get("requirements"), f"{profile_id} missing requirements")
        for tool_name in profile.get("tool_names", []):
            _require(
                tool_name in TOOL_REGISTRY,
                f"{profile_id} references unregistered tool {tool_name}",
            )
    for profile_id in (
        "bids_import",
        "bids_export",
        "study_create",
        "study_design",
        "study_precompute",
        "study_statistics",
        "ica_clustering",
        "import_plugins",
        "data_export",
        "hed_event_annotation",
        "history_scripting",
        "event_script_modification",
        "amica_ica",
        "nsg_remote",
        "plugin_development",
        "relica_reliability",
        "viewprops_review",
        "get_chanlocs_digitization",
        "roiconnect_source_connectivity",
        "eegstats_metrics",
    ):
        _require(profile_id in METHOD_PROFILES, f"missing staged STUDY profile: {profile_id}")

    for tool_name in HIGH_RISK_TOOL_NAMES:
        spec = TOOL_REGISTRY.get(tool_name)
        _require(spec is not None, f"high-risk tool missing registry entry: {tool_name}")
        _require(spec.risk_level == "high", f"{tool_name} registry risk_level must be high")
        _require(spec.method_profile, f"{tool_name} registry missing method_profile")


def check_official_matrices() -> None:
    support_levels = set(OFFICIAL_SOURCE_SNAPSHOT.get("support_level_values", []))
    _require(
        support_levels == {"executable", "gated_guidance", "indexed_only", "out_of_scope"},
        f"unexpected support levels: {support_levels}",
    )
    _require(
        OFFICIAL_SOURCE_SNAPSHOT.get("retrieved_on"),
        "official source snapshot missing retrieved_on",
    )
    for mirror_id, mirror in OFFICIAL_SOURCE_SNAPSHOT.get("mirrors", {}).items():
        _require(mirror.get("commit"), f"{mirror_id} missing commit")
        _require(mirror.get("url"), f"{mirror_id} missing url")

    _require(len(OFFICIAL_TOPIC_INDEX) >= 15, "official topic index too small")
    for topic_id, topic in OFFICIAL_TOPIC_INDEX.items():
        _require(topic.get("title"), f"{topic_id} missing title")
        support_level = topic.get("support_level")
        _require(
            support_level in support_levels,
            f"{topic_id} invalid support_level {support_level}",
        )
        resource_uri = topic.get("resource_uri")
        _require(resource_uri in RESOURCE_FILES, f"{topic_id} bad resource_uri")
        for claim_id in topic.get("claim_ids", []):
            _require(
                claim_id in OFFICIAL_CLAIMS,
                f"{topic_id} references unknown claim {claim_id}",
            )
        for tool_name in topic.get("tool_names", []):
            _require(
                tool_name in TOOL_REGISTRY,
                f"{topic_id} references unknown tool {tool_name}",
            )
        if support_level in {"executable", "gated_guidance"}:
            _require(
                topic.get("claim_ids"),
                f"{topic_id} missing claim_ids for supported topic",
            )
            if topic_id not in {"function_model"}:
                _require(
                    topic.get("tool_names"),
                    f"{topic_id} missing tool route for supported topic",
                )

    for plugin_name, plugin in OFFICIAL_PLUGIN_MATRIX.items():
        _require(
            plugin.get("support_level") in support_levels,
            f"{plugin_name} invalid support_level",
        )
        _require(plugin.get("functions"), f"{plugin_name} missing function probes")
        _require(
            plugin.get("dependent_profiles"),
            f"{plugin_name} missing dependent profiles",
        )
        _require(
            plugin.get("next_step_if_missing"),
            f"{plugin_name} missing next step",
        )
        for claim_id in plugin.get("claim_ids", []):
            _require(
                claim_id in OFFICIAL_CLAIMS,
                f"{plugin_name} references unknown claim {claim_id}",
            )
        for profile_id in plugin.get("dependent_profiles", []):
            _require(
                profile_id in METHOD_PROFILES or profile_id == "advanced_project",
                f"{plugin_name} references unknown profile {profile_id}",
            )

    required_report_groups = {
        "recording_and_acquisition",
        "events_and_design",
        "preprocessing_parameters",
        "analysis_parameters",
        "outputs_and_limits",
    }
    _require(
        required_report_groups.issubset(REPORT_FIELD_MATRIX),
        "report field matrix missing required groups",
    )
    for group, fields in REPORT_FIELD_MATRIX.items():
        _require(fields, f"report field matrix group empty: {group}")


def check_docs_and_skill() -> None:
    combined = "\n".join(
        [
            _read("docs/research-standard.md"),
            _read("docs/official-topic-index.md"),
            _read("docs/official-support-matrix.md"),
            _read("docs/official-tool-support-matrix.md"),
            _read("docs/official-method-map.md"),
            _read("docs/official-gate-policy.md"),
            _read("docs/official-plugin-map.md"),
            _read("docs/official-risk-matrix.md"),
            _read("docs/official-report-field-matrix.md"),
            _read("skills/eeglab-analysis/SKILL.md"),
            _read("skills/eeglab-analysis/references/official-gates.md"),
            _read("skills/eeglab-analysis/references/official-method-map.md"),
            _read("skills/eeglab-analysis/references/gate-policy.md"),
            _read("skills/eeglab-analysis/references/event-semantics.md"),
            _read("skills/eeglab-analysis/references/preprocessing-decision-tree.md"),
            _read("skills/eeglab-analysis/references/ica-iclabel-policy.md"),
            _read("skills/eeglab-analysis/references/bids-study-policy.md"),
            _read("skills/eeglab-analysis/references/source-policy.md"),
        _read("skills/eeglab-analysis/references/report-protocol-templates.md"),
        _read("skills/eeglab-analysis/references/branch-workflow-matrix.md"),
        _read("skills/eeglab-analysis/references/tools.md"),
            _read("skills/eeglab-analysis/references/workflows.md"),
            _read("eeglab_mcp_server/evals.xml"),
        ]
    )
    required_terms = [
        "eeglab_method_preflight",
        "official_gate_blocked",
        "override_gate",
        "override_reason",
        "source_claim_ids",
        "EEGLAB-EVENT-001",
        "EEGLAB-ASR-001",
        "EEGLAB-ICA-001",
        "EEGLAB-DIPFIT-001",
        "EEGLAB-BIDS-001",
        "BIDS-EEG-001",
        "BIDS-EVENTS-001",
        "support_level",
        "indexed_only",
        "gated_guidance",
        "topic index",
        "plugin matrix",
        "report field matrix",
        "branch workflow matrix",
        "branch-workflow-matrix.md",
        "tool support matrix",
        "eeglab://official/tool-support-matrix.md",
        "HED",
        "LIMO",
        "SIFT",
        "bids_export",
        "study_precompute",
        "ica_clustering",
        "amica_ica",
        "nsg_remote",
        "import_plugins",
        "data_export",
        "hed_event_annotation",
        "history_scripting",
        "event_script_modification",
        "EEGLAB-BIDSEXPORT-001",
        "EEGLAB-IMPORT-PLUGINS-001",
        "EEGLAB-EXPORT-001",
        "EEGLAB-HED-001",
        "EEGLAB-HISTORY-001",
        "EEGLAB-EVENTSCRIPT-001",
        "EEGLAB-MFF-001",
        "EEGLAB-NWB-001",
        "EEGLAB-BVA-001",
        "EEGLAB-STUDY-PRECOMP-001",
        "EEGLAB-ICCLUSTER-001",
        "EEGLAB-PLUGIN-DEV-001",
        "EEGLAB-RELICA-001",
        "EEGLAB-VIEWPROPS-001",
        "EEGLAB-GETCHANLOCS-001",
        "EEGLAB-ROICONNECT-001",
        "EEGLAB-EEGSTATS-001",
        "relica_reliability",
        "viewprops_review",
        "get_chanlocs_digitization",
        "roiconnect_source_connectivity",
        "eegstats_metrics",
        "plugin_development",
        "RELICA",
        "Viewprops",
        "get_chanlocs",
        "ROIconnect",
        "EEGstats",
        "EEGLAB-AMICA-001",
        "EEGLAB-NSG-001",
    ]
    for term in required_terms:
        _require(term.lower() in combined.lower(), f"missing official alignment term: {term}")

    official_method_doc = _read("docs/official-method-map.md").lower()
    skill_method_doc = _read("skills/eeglab-analysis/references/official-method-map.md").lower()
    for profile_id in METHOD_PROFILES:
        profile_term = f"`{profile_id}`".lower()
        _require(profile_term in official_method_doc, f"official method map missing profile: {profile_id}")
        _require(profile_term in skill_method_doc, f"skill official method map missing profile: {profile_id}")

    protocol_docs = "\n".join(
        [
            _read("skills/eeglab-analysis/references/report-protocol-templates.md"),
            _read("skills/eeglab-analysis/references/branch-workflow-matrix.md"),
            _read("skills/eeglab-analysis/references/tools.md"),
            _read("skills/eeglab-analysis/references/workflows.md"),
        ]
    )
    schema_text = _read("eeglab_mcp_server/schemas.py")
    for term in (
        "gate_results",
        "source_claim_ids",
        "report_fields",
        "branch_workflow",
        "branch_completeness",
        "override_used",
        "override_reason",
        "blocked_requirements_acknowledged",
        "missing_requirements",
    ):
        _require(term in protocol_docs, f"protocol docs missing term: {term}")
        _require(term in schema_text, f"schema missing protocol term: {term}")
    for term in (
        "report field matrix coverage",
        "recording/acquisition",
        "events/design",
        "outputs/limits",
    ):
        _require(
            term.lower() in protocol_docs.lower(),
            f"protocol docs missing report-field term: {term}",
        )


def check_tool_contract_text() -> None:
    tools = {tool.name: tool for tool in build_tool_definitions()}
    _require("eeglab_method_preflight" in tools, "missing eeglab_method_preflight tool")

    workflow_tool_names = {tool.name for tool in workflow_tools()}
    _require(
        "eeglab_method_preflight" in workflow_tool_names,
        "preflight missing from workflow tool set",
    )

    preflight_description = tools["eeglab_method_preflight"].description or ""
    for term in ("official", "gate_status", "source claim", "high-risk"):
        _require(
            term.lower() in preflight_description.lower(),
            f"preflight description missing term: {term}",
        )

    for tool_name in HIGH_RISK_TOOL_NAMES:
        tool = tools.get(tool_name)
        _require(tool is not None, f"high-risk tool not exposed: {tool_name}")
        properties = tool.inputSchema.get("properties", {})
        for field in ("override_gate", "override_reason", "method_context"):
            _require(field in properties, f"{tool_name} missing high-risk field {field}")
        description = (tool.description or "").lower()
        _require(
            "preflight" in description or "official" in description,
            f"{tool_name} description missing official/preflight guidance",
        )


def check_preflight_behavior() -> None:
    epoch = evaluate_method_preflight({"method": "epoch", "context": {"event_roles": ["boundary"]}})
    _require(epoch["gate_status"] == "blocked", "boundary-only epoch should be blocked")

    source = evaluate_method_preflight(
        {
            "method": "source",
            "context": {"has_ica": False, "has_channel_locations": False},
        }
    )
    _require(
        source["gate_status"] == "blocked",
        "source without ICA/channel locations should be blocked",
    )

    clean = evaluate_method_preflight({"method": "clean_rawdata", "context": {"data_shape": "epoched"}})
    _require(
        clean["gate_status"] == "blocked",
        "clean_rawdata on epoched-only data should be blocked",
    )

    acquisition = evaluate_method_preflight(
        {
            "method": "acquisition_metadata",
            "context": {
                "raw_input_preserved": False,
                "derivative_output_planned": False,
                "documented_missing_fields": ["impedance"],
            },
        }
    )
    _require(
        acquisition["gate_status"] == "blocked",
        "acquisition metadata gaps should block analysis-ready provenance",
    )
    acquisition_missing_ids = {item["id"] for item in acquisition["critical_missing_requirements"]}
    _require(
        {
            "raw_input_preserved",
            "derivative_output_planned",
            "reference_or_montage_recorded",
            "power_line_frequency_recorded",
            "acquisition_filters_recorded",
        }.issubset(acquisition_missing_ids),
        "acquisition gate missing expected critical requirement IDs",
    )
    acquisition_pass = evaluate_method_preflight(
        {
            "method": "acquisition_metadata",
            "context": {
                "raw_input_preserved": True,
                "output_path": "derivatives/sub-01_clean.set",
                "reference": "Cz",
                "line_freq": 60,
                "hardware_filters": "0.01-250 Hz",
                "task_name": "auditory oddball",
                "impedance_notes": "recorded in lab notebook",
            },
        }
    )
    _require(
        acquisition_pass["gate_status"] in {"pass", "advisory"},
        "complete acquisition provenance context should not be blocked",
    )

    bids = evaluate_method_preflight(
        {
            "method": "bids_metadata",
            "context": {
                "bids_path": "sub-01",
                "events_tsv_columns": ["onset", "duration", "trial_type"],
                "event_metadata_described": False,
            },
        }
    )
    _require(
        bids["gate_status"] == "blocked",
        "BIDS metadata without sidecar descriptions should be blocked",
    )
    bids_missing_ids = {item["id"] for item in bids["critical_missing_requirements"]}
    _require(
        {
            "bids_eeg_sidecar_complete",
            "event_metadata_described",
            "bids_event_columns_described",
        }.issubset(bids_missing_ids),
        "BIDS gate missing expected critical requirement IDs",
    )
    bids_pass = evaluate_method_preflight(
        {
            "method": "bids_metadata",
            "context": {
                "bids_path": "C:/data/bids",
                "sidecar_paths": [
                    "sub-01_task-test_eeg.json",
                    "sub-01_task-test_channels.tsv",
                    "sub-01_task-test_electrodes.tsv",
                    "sub-01_task-test_coordsystem.json",
                ],
                "events_tsv_columns": ["onset", "duration", "trial_type"],
                "events_json": "sub-01_task-test_events.json",
            },
        }
    )
    _require(
        bids_pass["gate_status"] == "pass",
        "complete BIDS metadata context should pass",
    )

    bids_import = evaluate_method_preflight(
        {
            "method": "bids_import",
            "context": {
                "bids_path": "C:/data/bids",
                "plugins_available": ["EEG-BIDS"],
                "events_tsv_columns": ["onset", "duration", "trial_type"],
            },
        }
    )
    _require(
        bids_import["gate_status"] in {"pass", "advisory"},
        "BIDS import with path/plugin/event timing should not be hard blocked",
    )

    study_create = evaluate_method_preflight({"method": "study_create", "context": {"project_scale": "bids_study"}})
    _require(
        study_create["gate_status"] == "advisory",
        "STUDY creation should not require design/statistics fields",
    )

    study_design = evaluate_method_preflight(
        {
            "method": "study_design",
            "context": {
                "project_scale": "bids_study",
                "design_variables": ["condition"],
            },
        }
    )
    _require(
        study_design["gate_status"] == "advisory",
        "STUDY design should pass critical gates but keep protocol lock advisory",
    )

    study_stats = evaluate_method_preflight(
        {
            "method": "study_statistics",
            "context": {
                "project_scale": "bids_study",
                "design_variables": ["condition"],
                "measure": "erp",
                "alpha": 0.05,
            },
        }
    )
    study_stats_missing_ids = {item["id"] for item in study_stats["critical_missing_requirements"]}
    _require(
        "single_subject_protocol_locked" in study_stats_missing_ids,
        "STUDY statistics should still require locked single-subject protocol",
    )

    study_ready = evaluate_method_preflight({"method": "study", "context": {"project_scale": "single_subject"}})
    study_ready_missing_ids = {item["id"] for item in study_ready["critical_missing_requirements"]}
    _require(
        {"multi_subject_or_bids", "single_subject_protocol_locked", "design_variables_defined"}.issubset(
            study_ready_missing_ids
        ),
        "STUDY ready-check should require multi-subject/BIDS organization, protocol lock, and design variables",
    )

    override = evaluate_method_preflight(
        {
            "method": "source",
            "context": {"has_ica": False, "has_channel_locations": False},
            "override_reason": "Exploratory dry-run approved by user; no scientific source claims will be made.",
        }
    )
    _require(
        override["gate_status"] == "override_accepted",
        "override should be accepted when reason is supplied",
    )
    _require(override["override_used"] is True, "override_used must be true")

    _require(
        "eeglab_source_localization" in HIGH_RISK_TOOL_NAMES,
        "source tool not marked high-risk",
    )

    chan_repair = evaluate_method_preflight(
        {
            "method": "channel_locations",
            "context": {"channel_location_repair_planned": True, "loc_file": "cap.ced"},
        }
    )
    _require(
        chan_repair["gate_status"] in {"pass", "advisory"},
        "channel location repair plan should not be hard blocked",
    )

    topography = evaluate_method_preflight({"method": "topography", "context": {"parameters_recorded": True}})
    _require(
        topography["gate_status"] == "blocked",
        "topography without channel locations should be blocked",
    )

    spectral = evaluate_method_preflight(
        {
            "method": "spectral",
            "context": {
                "freq_range": [0.5, 45],
                "artifact_policy": "manual QC plus rejected bad segments",
                "channels": ["Pz"],
            },
        }
    )
    _require(
        spectral["gate_status"] == "pass",
        "spectral with frequency/artifact/channel context should pass",
    )

    limo = evaluate_method_preflight(
        {
            "method": "limo_statistics",
            "context": {"plugins_available": ["LIMO"]},
        }
    )
    _require(
        limo["gate_status"] == "blocked",
        "LIMO without design/correction policy should be blocked",
    )

    bids_export = evaluate_method_preflight(
        {
            "method": "bids_export",
            "context": {
                "plugins_available": ["EEG-BIDS"],
                "output_dir": "derivatives/bids-export",
                "events_tsv_columns": ["onset", "duration", "trial_type"],
            },
        }
    )
    bids_export_missing_ids = {item["id"] for item in bids_export["critical_missing_requirements"]}
    _require(
        {"bids_eeg_sidecar_complete", "event_metadata_described"}.issubset(bids_export_missing_ids),
        "BIDS export should require sidecars and event metadata",
    )

    study_precompute = evaluate_method_preflight(
        {
            "method": "study_precompute",
            "context": {
                "project_scale": "bids_study",
                "design_variables": ["condition"],
                "output_dir": "derivatives/study",
            },
        }
    )
    study_precompute_missing_ids = {item["id"] for item in study_precompute["critical_missing_requirements"]}
    _require(
        {"single_subject_protocol_locked", "study_measure_recorded"}.issubset(study_precompute_missing_ids),
        "STUDY precompute should require protocol lock and measure records",
    )

    clustering = evaluate_method_preflight(
        {
            "method": "ica_clustering",
            "context": {
                "project_scale": "multi_subject",
                "has_ica": True,
                "measure": "dipoles+spectra",
            },
        }
    )
    clustering_missing_ids = {item["id"] for item in clustering["critical_missing_requirements"]}
    _require(
        "clustering_policy_recorded" in clustering_missing_ids,
        "ICA clustering should require clustering policy",
    )

    amica = evaluate_method_preflight(
        {
            "method": "amica_ica",
            "context": {
                "data_shape": "continuous",
                "rank_reference_reviewed": True,
            },
        }
    )
    amica_missing_ids = {item["id"] for item in amica["critical_missing_requirements"]}
    _require(
        {"plugin_amica_available", "compute_strategy_recorded"}.issubset(amica_missing_ids),
        "AMICA should require plugin availability and compute strategy",
    )

    nsg = evaluate_method_preflight(
        {
            "method": "nsg_remote",
            "context": {"plugins_available": ["NSGportal"]},
        }
    )
    nsg_missing_ids = {item["id"] for item in nsg["critical_missing_requirements"]}
    _require(
        {"remote_compute_approved", "job_provenance_recorded"}.issubset(nsg_missing_ids),
        "NSG remote planning should require approval and job provenance",
    )

    import_plugins = evaluate_method_preflight(
        {
            "method": "import_plugins",
            "context": {
                "source_format": "MFF",
                "raw_input_preserved": True,
            },
        }
    )
    import_plugins_missing_ids = {item["id"] for item in import_plugins["critical_missing_requirements"]}
    _require(
        {"plugin_import_available", "import_event_channel_mapping_recorded"}.issubset(import_plugins_missing_ids),
        "plugin import should require importer availability and event/channel mapping",
    )
    import_plugins_pass = evaluate_method_preflight(
        {
            "method": "import_plugins",
            "context": {
                "source_format": "BrainVision",
                "plugins_available": ["BVA-io"],
                "event_mapping": "markers reviewed against codebook",
                "channel_mapping": "header labels preserved",
                "raw_input_preserved": True,
            },
        }
    )
    _require(import_plugins_pass["gate_status"] == "pass", "complete import plugin context should pass")

    data_export = evaluate_method_preflight(
        {
            "method": "data_export",
            "context": {"export_format": "NWB", "plugins_available": ["NWB-io"]},
        }
    )
    data_export_missing_ids = {item["id"] for item in data_export["critical_missing_requirements"]}
    _require(
        {"derivative_output_planned", "export_metadata_complete"}.issubset(data_export_missing_ids),
        "data export should require derivative output and metadata completeness",
    )

    hed = evaluate_method_preflight(
        {
            "method": "hed_event_annotation",
            "context": {"hed_tags": ["Sensory-event"]},
        }
    )
    hed_missing_ids = {item["id"] for item in hed["critical_missing_requirements"]}
    _require(
        "hed_schema_recorded" in hed_missing_ids,
        "HED event annotation should require schema/version provenance",
    )

    history = evaluate_method_preflight(
        {
            "method": "history_scripting",
            "context": {"processing_history": "EEG = pop_eegfiltnew(...);"},
        }
    )
    history_missing_ids = {item["id"] for item in history["critical_missing_requirements"]}
    _require(
        "script_from_history_reviewed" in history_missing_ids,
        "history scripting should require reviewed scripts",
    )

    event_script = evaluate_method_preflight(
        {
            "method": "event_script_modification",
            "context": {"event_recode_table": {"S 1": "target"}, "srate": 500},
        }
    )
    event_script_missing_ids = {item["id"] for item in event_script["critical_missing_requirements"]}
    _require(
        "urevent_preserved_or_relinked" in event_script_missing_ids,
        "event script modification should require urevent preservation or relinking",
    )

    plugin_dev = evaluate_method_preflight(
        {
            "method": "plugin_development",
            "context": {"plugin_goal": "custom ERP import helper"},
        }
    )
    plugin_dev_missing_ids = {item["id"] for item in plugin_dev["critical_missing_requirements"]}
    _require(
        "eeglab_function_family_recorded" in plugin_dev_missing_ids,
        "plugin development should require function-family/interface boundary",
    )

    relica = evaluate_method_preflight(
        {
            "method": "relica_reliability",
            "context": {"plugins_available": ["RELICA"], "has_ica": True},
        }
    )
    relica_missing_ids = {item["id"] for item in relica["critical_missing_requirements"]}
    _require(
        "bootstrap_settings_recorded" in relica_missing_ids,
        "RELICA should require bootstrap/settings provenance",
    )

    viewprops = evaluate_method_preflight(
        {
            "method": "viewprops_review",
            "context": {"plugins_available": ["Viewprops"]},
        }
    )
    viewprops_missing_ids = {item["id"] for item in viewprops["critical_missing_requirements"]}
    _require("has_ica" in viewprops_missing_ids, "Viewprops review should require ICA")

    get_chanlocs = evaluate_method_preflight(
        {
            "method": "get_chanlocs_digitization",
            "context": {"plugins_available": ["get_chanlocs"], "head_image": "sub-01-head.obj"},
        }
    )
    get_chanlocs_missing_ids = {item["id"] for item in get_chanlocs["critical_missing_requirements"]}
    _require("fiducials_recorded" in get_chanlocs_missing_ids, "get_chanlocs should require fiducials")

    roiconnect = evaluate_method_preflight(
        {
            "method": "roiconnect_source_connectivity",
            "context": {"plugins_available": ["ROIconnect"], "source_model": "dipfit"},
        }
    )
    roiconnect_missing_ids = {item["id"] for item in roiconnect["critical_missing_requirements"]}
    _require(
        {"roi_atlas_recorded", "connectivity_metric_recorded"}.issubset(roiconnect_missing_ids),
        "ROIconnect should require ROI atlas and connectivity metric",
    )

    eegstats = evaluate_method_preflight(
        {
            "method": "eegstats_metrics",
            "context": {"plugins_available": ["EEGstats"], "freq_range": [1, 40]},
        }
    )
    eegstats_missing_ids = {item["id"] for item in eegstats["critical_missing_requirements"]}
    _require("channels_recorded" in eegstats_missing_ids, "EEGstats should require channels/ROIs")


def check_online_sources() -> None:
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", "eeglab-mcp-official-alignment-verifier")]
    for claim_id, claim in OFFICIAL_CLAIMS.items():
        with opener.open(claim["url"], timeout=15) as response:
            _require(
                200 <= response.status < 400,
                f"{claim_id} URL not reachable: {claim['url']}",
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--online", action="store_true", help="Also check official URLs are reachable.")
    args = parser.parse_args()

    check_claim_map()
    check_official_matrices()
    check_docs_and_skill()
    check_tool_contract_text()
    check_preflight_behavior()
    if args.online:
        check_online_sources()

    print("official_alignment_ok=True")
    print(f"claim_count={len(OFFICIAL_CLAIMS)}")
    print(f"method_profile_count={len(METHOD_PROFILES)}")
    print(f"high_risk_tool_count={len(HIGH_RISK_TOOL_NAMES)}")


if __name__ == "__main__":
    main()
