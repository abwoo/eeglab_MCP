"""High-level research workflow helpers for EEGLAB MCP tools."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from mcp.types import TextContent

try:
    from .official_alignment import (
        branch_workflow_details,
        OFFICIAL_CLAIMS,
        REPORT_FIELD_MATRIX,
        evaluate_method_preflight,
    )
except ImportError:  # pragma: no cover - direct script execution support
    from official_alignment import (
        branch_workflow_details,
        OFFICIAL_CLAIMS,
        REPORT_FIELD_MATRIX,
        evaluate_method_preflight,
    )


LIMITATIONS = [
    "This workflow reports EEG signal-processing outputs, not clinical or diagnostic conclusions.",
    "Results depend on local EEGLAB plugins, channel metadata, event coding, and acquisition quality.",
    "Recording/acquisition metadata may be incomplete unless it was preserved in the imported EEG file or BIDS sidecars.",
    "Light workflows are smoke-tested entry points and do not replace study-specific preprocessing decisions.",
]

OFFICIAL_REFERENCES = [
    {
        "name": "EEGLAB GitHub",
        "url": "https://github.com/sccn/eeglab",
        "use": "Open-source EEGLAB MATLAB/Octave signal-processing environment.",
    },
    {
        "name": "EEGLAB functions guide",
        "url": "https://eeglab.org/tutorials/ConceptsGuide/EEGLAB_functions.html",
        "use": "Official pop_/eeg_ function model used by MCP tool descriptions.",
    },
    {
        "name": "EEGLAB tutorials",
        "url": "https://eeglab.org/tutorials/",
        "use": "Official workflow tutorials for scripting, preprocessing, ICA, ERP, time-frequency, STUDY, and source work.",
    },
    {
        "name": "clean_rawdata",
        "url": "https://eeglab.org/plugins/clean_rawdata/",
        "use": "ASR, bad-channel, and bad-segment cleaning prerequisites.",
    },
    {
        "name": "ICLabel",
        "url": "https://github.com/sccn/ICLabel",
        "use": "ICA component classification prerequisite and interpretation limits.",
    },
    {
        "name": "DIPFIT",
        "url": "https://eeglab.org/plugins/dipfit/",
        "use": "Source-localization prerequisites and template model assumptions.",
    },
    {
        "name": "EEG-BIDS in EEGLAB",
        "url": "https://eeglab.org/tutorials/11_Scripting/Analyzing_EEG_BIDS_data_in_EEGLAB.html",
        "use": "BIDS import and STUDY/group-analysis path.",
    },
    {
        "name": "EEGLAB Course",
        "url": "https://github.com/sccn/EEGLAB_course",
        "use": "Official course coverage for BIDS, preprocessing, ERP/time-frequency, source/connectivity, ICA clustering, and statistics.",
    },
]

DEFAULT_QC_GATES = [
    "raw_input_preserved",
    "recording_metadata_reported",
    "channel_location_coverage_checked",
    "event_labels_and_latencies_checked",
    "processing_history_or_session_steps_recorded",
    "analysis_branch_matches_study_design",
    "destructive_steps_write_new_outputs",
    "artifact_rejection_thresholds_reported",
    "outputs_and_limitations_reported",
]

NON_ANALYSIS_EVENT_ROLES = {
    "boundary",
    "impedance",
    "segment_marker",
    "excluded",
    "qc_annotation",
}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _as_string_list(value: Any) -> list[str]:
    return [str(item).strip() for item in _as_list(value) if str(item).strip()]


def _norm_label(value: Any) -> str:
    return str(value).strip().lower()


def _event_role_from_semantics(label: str, semantics: dict[str, Any]) -> str | None:
    """Return a normalized role supplied by user/lab semantics, when available."""
    if not isinstance(semantics, dict):
        return None
    raw = semantics.get(label)
    if raw is None:
        raw = semantics.get(_norm_label(label))
    if isinstance(raw, dict):
        raw = raw.get("role") or raw.get("type") or raw.get("meaning")
    if raw is None:
        return None
    text = str(raw).strip().lower()
    if any(
        term in text
        for term in (
            "condition",
            "target",
            "standard",
            "stimulus",
            "trigger",
            "response",
        )
    ):
        return "condition"
    if any(term in text for term in ("boundary", "start", "end", "segment", "block", "run")):
        return "segment_marker" if "segment" in text or "start" in text or "end" in text else "boundary"
    if "impedance" in text:
        return "impedance"
    if any(term in text for term in ("exclude", "delete", "ignore", "qc", "metadata")):
        return "excluded"
    return text or None


def _analysis_event_types(
    event_types: list[str],
    event_semantics: dict[str, Any] | None = None,
    condition_markers: list[str] | None = None,
    exclude_markers: list[str] | None = None,
    boundary_markers: list[str] | None = None,
    segment_markers: list[str] | None = None,
) -> list[str]:
    """Return markers that are eligible for condition/event-locked analysis."""
    condition_set = {_norm_label(item) for item in _as_string_list(condition_markers)}
    exclude_set = {_norm_label(item) for item in _as_string_list(exclude_markers)}
    boundary_set = {_norm_label(item) for item in _as_string_list(boundary_markers)}
    segment_set = {_norm_label(item) for item in _as_string_list(segment_markers)}
    eligible: list[str] = []
    for event in event_types:
        key = _norm_label(event)
        role = _event_role_from_semantics(event, event_semantics or {})
        if key in condition_set or role == "condition":
            eligible.append(event)
        elif key in exclude_set or key in boundary_set or key in segment_set:
            continue
        elif role in NON_ANALYSIS_EVENT_ROLES:
            continue
        elif "impedance" in key or "boundary" in key or key in {"s1000", "new segment", "start", "end"}:
            continue
        else:
            eligible.append(event)
    return eligible


def _research_blockers(
    *,
    analysis_type: str,
    event_types: list[str],
    analysis_events: list[str],
    data_shape: str | None,
    has_channel_locations: bool | None,
    has_ica: bool | None,
    has_continuous_raw: bool | None,
    has_behavioral_log: bool | None,
    project_scale: str,
) -> tuple[list[str], list[str]]:
    """Return blocking conditions and explicit not-recommended actions."""
    blockers: list[str] = []
    not_recommended: list[str] = [
        "Do not overwrite raw EEG files; write derivatives to a separate output path.",
        "Do not make clinical or diagnostic claims from signal-processing outputs.",
    ]

    if analysis_type in {"erp", "timefreq"}:
        not_recommended.append("Do not epoch around boundary, impedance, excluded, or segment-only markers.")
        if event_types and not analysis_events:
            blockers.append("No confirmed condition/trigger event remains after excluding boundary/QC/segment markers.")
        elif not event_types:
            blockers.append(
                "Event-locked ERP/time-frequency analysis needs validated event labels and condition semantics."
            )
        if has_behavioral_log is False:
            not_recommended.append(
                "Do not claim condition-level behavioral interpretation without a behavioral log or validated event-code map."
            )

    if analysis_type in {"source", "connectivity"}:
        if has_channel_locations is False:
            blockers.append(
                "Channel locations are missing; source/topography/connectivity interpretation is blocked until montage metadata is repaired."
            )
        not_recommended.append(
            "Do not infer anatomical sources from sensor data without correct montage, ICA/source prerequisites, and reported model assumptions."
        )

    if analysis_type == "source" and has_ica is False:
        blockers.append(
            "Source localization through DIPFIT needs ICA components or another explicitly justified source model."
        )

    if analysis_type in {"ica", "resting"} and data_shape == "epoched" and has_continuous_raw is False:
        blockers.append(
            "ICA/resting analysis from epoched-only data is blocked unless the design explicitly supports that use."
        )

    if analysis_type == "study":
        if project_scale not in {"multi_subject", "bids_study"}:
            blockers.append("STUDY/group analysis needs a multi-subject or BIDS/STUDY project structure.")
        not_recommended.append(
            "Do not run group statistics before the single-subject preprocessing protocol is locked and documented."
        )

    if has_channel_locations is False:
        not_recommended.append(
            "Do not produce topography or source claims until channel-location coverage is repaired."
        )

    return blockers, not_recommended


def text_payload(payload: dict[str, Any]) -> list[TextContent]:
    """Return a JSON text MCP payload."""
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))]


def structured_payload(
    payload: dict[str, Any],
) -> tuple[list[TextContent], dict[str, Any]]:
    """Return text JSON plus structuredContent for MCP clients that support it."""
    return text_payload(payload), payload


def parse_tool_result(result: Any) -> dict[str, Any]:
    """Parse the first TextContent JSON item returned by a tool call."""
    if isinstance(result, tuple):
        result = result[0]
    if not result:
        return {
            "status": "error",
            "code": "empty_tool_result",
            "error": "tool returned no content",
        }
    text = result[0].text if hasattr(result[0], "text") else ""
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "code": "non_json_tool_result",
            "error": f"tool returned non-JSON text: {exc}",
            "details": {"text_preview": text[:1200]},
        }


def workflow_error(
    workflow: str,
    step: str,
    payload: dict[str, Any],
    *,
    parameters: dict[str, Any],
    steps: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a workflow-shaped error response."""
    return {
        "status": "error",
        "code": payload.get("code", "workflow_step_failed"),
        "error": payload.get("error", f"{step} failed"),
        "next_step": payload.get(
            "next_step",
            "Inspect the failed step details and rerun with corrected inputs.",
        ),
        "workflow": workflow,
        "steps": steps,
        "parameters": parameters,
        "outputs": {},
        "summary": {"failed_step": step},
        "limitations": LIMITATIONS,
        "details": {"step": step, "result": payload},
    }


def safe_output_filename(name: Any, *, default: str) -> str:
    """Return a safe leaf filename for a workflow output."""
    filename = str(name or default).strip()
    if not filename:
        filename = default
    if not filename.lower().endswith(".set"):
        filename += ".set"
    if Path(filename).name != filename or filename in {".", ".."} or any(sep in filename for sep in ("/", "\\")):
        raise ValueError("output_filename must be a filename inside output_dir, not a path")
    if os.path.splitdrive(filename)[0]:
        raise ValueError("output_filename must not include a drive prefix")
    return filename


def workflow_success(
    workflow: str,
    *,
    steps: list[dict[str, Any]],
    parameters: dict[str, Any],
    outputs: dict[str, Any],
    summary: dict[str, Any],
) -> dict[str, Any]:
    """Build a workflow-shaped success response."""
    return {
        "status": "success",
        "workflow": workflow,
        "steps": steps,
        "parameters": parameters,
        "outputs": outputs,
        "summary": summary,
        "limitations": LIMITATIONS,
    }


ANALYSIS_TO_METHOD_PROFILE = {
    "erp": "epoch",
    "timefreq": "timefreq",
    "ica": "run_ica",
    "source": "source",
    "study": "study",
    "connectivity": "connectivity",
    "segment_qc": "epoch",
    "resting": "derivative_processing",
}

STUDY_STAGE_METHODS = (
    "bids_metadata",
    "bids_import",
    "study_create",
    "study_design",
    "study_statistics",
)


def _method_context_from_workflow(parameters: dict[str, Any]) -> dict[str, Any]:
    """Translate workflow-level facts into official preflight context keys."""
    context = dict(parameters)
    if parameters.get("analysis_event_types"):
        context.setdefault("condition_markers", parameters.get("analysis_event_types"))
        context.setdefault("event_roles", ["condition"])
    event_semantics = parameters.get("event_semantics")
    if isinstance(event_semantics, dict):
        context.setdefault("event_roles", list(event_semantics.values()))
    if parameters.get("has_channel_locations") is True:
        context.setdefault("has_channel_locations", True)
    if parameters.get("has_ica") is True:
        context.setdefault("has_ica", True)
    if parameters.get("has_continuous_raw") is True and not context.get("data_shape"):
        context.setdefault("data_shape", "continuous")
    return context


def official_alignment_summary(
    method: str = "", tool_name: str = "", context: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Return a compact official-alignment summary for workflow outputs."""
    method_key = ANALYSIS_TO_METHOD_PROFILE.get(str(method).lower(), method)
    payload = evaluate_method_preflight(
        {
            "method": method_key,
            "tool_name": tool_name,
            "context": _method_context_from_workflow(context or {}),
            "strictness": "hard",
        }
    )
    return {
        "method_profile_id": payload.get("method_profile_id", ""),
        "gate_status": payload.get("gate_status", ""),
        "source_claim_ids": payload.get("source_claim_ids", []),
        "missing_requirement_ids": [item.get("id") for item in payload.get("missing_requirements", [])],
    }


def official_gate_summaries(method: str, context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Return one or more compact gate summaries for a workflow branch."""
    if str(method).lower() != "study":
        return [official_alignment_summary(method, context=context)]
    return [official_alignment_summary(stage_method, context=context) for stage_method in STUDY_STAGE_METHODS]


def _unique_strings(values: list[Any]) -> list[str]:
    """Return non-empty strings in first-seen order."""
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _gate_results_from_args(args: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize caller-supplied compact gate summaries."""
    raw = args.get("gate_results")
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict)]


def _source_claim_ids_from_protocol_args(args: dict[str, Any], gate_results: list[dict[str, Any]]) -> list[str]:
    """Prefer explicit source claims; otherwise derive them from gate summaries."""
    explicit = _as_string_list(args.get("source_claim_ids"))
    if explicit:
        return _unique_strings(explicit)
    derived: list[Any] = []
    for gate in gate_results:
        derived.extend(_as_list(gate.get("source_claim_ids")))
    return _unique_strings(derived)


def _report_field_coverage(args: dict[str, Any]) -> dict[str, Any]:
    """Return report-field coverage without claiming unchecked fields are complete."""
    supplied = args.get("report_fields") if isinstance(args.get("report_fields"), dict) else {}
    coverage: dict[str, Any] = {}
    for group, fields in REPORT_FIELD_MATRIX.items():
        group_value = supplied.get(group) if isinstance(supplied, dict) else None
        if group_value is None:
            provided: list[str] = []
        elif isinstance(group_value, list):
            provided = _unique_strings(group_value)
        elif isinstance(group_value, dict):
            provided = _unique_strings([key for key, value in group_value.items() if value])
        else:
            provided = [str(group_value)]
        coverage[group] = {
            "expected_fields": fields,
            "provided_fields": provided,
            "coverage_status": "provided" if provided else "not_provided",
        }
    return coverage


def _branch_payload_from_args(args: dict[str, Any]) -> dict[str, Any]:
    """Normalize branch completeness inputs into a canonical payload."""
    branch_args = args if isinstance(args, dict) else {}
    return branch_workflow_details(
        branch_args.get("analysis_type", ""),
        completed_steps=_as_string_list(branch_args.get("completed_steps")),
        figure_paths=_as_string_list(branch_args.get("figure_paths")),
        output_paths=_as_string_list(branch_args.get("output_paths")),
        blocker_messages=_as_string_list(branch_args.get("blocked_steps")),
        required_outputs=_as_string_list(branch_args.get("required_outputs")),
        branch_variant=str(branch_args.get("branch_variant", "") or "").strip() or None,
    )


def _gate_result_line(gate: dict[str, Any]) -> str:
    """Render one compact gate result for Markdown protocol text."""
    profile = gate.get("method_profile_id", "unknown")
    status = gate.get("gate_status", "unknown")
    missing = gate.get("missing_requirement_ids") or [
        item.get("id") for item in _as_list(gate.get("missing_requirements")) if isinstance(item, dict)
    ]
    claims = _as_string_list(gate.get("source_claim_ids"))
    return f"- `{profile}`: `{status}`; missing={_unique_strings(missing) or []}; " f"source_claim_ids={claims or []}"


def qc_report_from_payloads(info: dict[str, Any], events: dict[str, Any], history: dict[str, Any]) -> dict[str, Any]:
    """Build a QC report from existing low-level tool payloads."""
    recording = info.get("recording") or {}
    missing_locations = []
    channel_labels = info.get("channel_labels") or []
    if info.get("has_channel_locations") is False:
        missing_locations = channel_labels

    risks: list[str] = []
    provenance_hints: list[str] = []
    if not info.get("num_events"):
        risks.append("No events were reported; event-locked analyses may not be possible.")
    elif not info.get("has_urevent_links", False):
        provenance_hints.append(
            "Event urevent links are absent; preserve event latencies/counts when transforming epochs."
        )
    if info.get("has_channel_locations") is False:
        risks.append("Channel locations appear missing; topography/source workflows need channel locations.")
    elif info.get("channel_location_coverage", 1) < 1:
        risks.append("Some channel locations are missing; topography/source workflows may be incomplete.")
    if not info.get("ica_computed", False):
        risks.append("ICA weights are absent; component-level artifact review is not available yet.")
    if info.get("srate") and info["srate"] < 128:
        risks.append("Sampling rate is low for high-frequency analyses.")
    if not info.get("processing_history_available", False):
        provenance_hints.append(
            "EEGLAB processing history is empty; report all steps applied in this session explicitly."
        )
    if not recording.get("has_comments", False):
        provenance_hints.append(
            "Dataset comments/recording notes are absent; record acquisition context outside the .set file if needed."
        )
    if not recording.get("filename") and not info.get("filename"):
        provenance_hints.append(
            "Source filename is missing from EEG metadata; keep the absolute input path in reports."
        )

    return workflow_success(
        "eeglab_qc_report",
        steps=[
            {"name": "eeglab_info", "status": info.get("status", "success")},
            {"name": "eeglab_get_events", "status": events.get("status", "success")},
            {"name": "eeglab_history", "status": history.get("status", "success")},
        ],
        parameters={},
        outputs={},
        summary={
            "recording": {
                "data_shape": recording.get("data_shape"),
                "sampling_rate_hz": recording.get("sampling_rate_hz", info.get("srate")),
                "channel_count": recording.get("channel_count", info.get("nbchan")),
                "trials": recording.get("trials", info.get("trials")),
                "points_per_epoch": recording.get("points_per_epoch", info.get("pnts")),
                "epoch_duration_sec": recording.get("epoch_duration_sec", info.get("duration_sec")),
                "total_data_duration_sec": recording.get("total_data_duration_sec"),
                "setname": recording.get("setname", info.get("setname")),
                "filename": recording.get("filename", info.get("filename")),
                "filepath": recording.get("filepath", info.get("filepath")),
                "saved_state": recording.get("saved_state", info.get("saved")),
                "has_comments": recording.get("has_comments", False),
                "has_etc_metadata": recording.get("has_etc_metadata", False),
            },
            "nbchan": info.get("nbchan"),
            "srate": info.get("srate"),
            "pnts": info.get("pnts"),
            "trials": info.get("trials"),
            "duration_sec": info.get("duration_sec"),
            "event_types": events.get("event_types", info.get("event_types", [])),
            "event_counts": events.get("event_counts", info.get("event_counts", {})),
            "event_latency_range_sec": info.get("event_latency_range_sec"),
            "has_urevent_links": info.get("has_urevent_links", False),
            "num_urevents": info.get("num_urevents", 0),
            "channel_location_coverage": info.get("channel_location_coverage"),
            "channels_with_locations": info.get("channels_with_locations"),
            "channels_missing_locations": info.get("channels_missing_locations"),
            "ica_computed": info.get("ica_computed", False),
            "ica_classified": info.get("ica_classified", False),
            "missing_channel_locations": missing_locations,
            "risk_hints": risks,
            "provenance_hints": provenance_hints,
            "history_available": bool(history.get("history") and history.get("history") != "无操作历史记录"),
        },
    )


def recommend_workflow(args: dict[str, Any]) -> dict[str, Any]:
    """Recommend an adaptive, project-level, non-destructive EEG workflow plan."""
    requested_analysis_type = args.get("analysis_type", "auto")
    event_types = args.get("event_types", [])
    data_shape = args.get("data_shape")
    has_channel_locations = args.get("has_channel_locations")
    event_semantics = args.get("event_semantics") if isinstance(args.get("event_semantics"), dict) else {}
    analysis_events = _analysis_event_types(event_types, event_semantics)

    if requested_analysis_type != "auto":
        analysis_type = requested_analysis_type
    elif analysis_events:
        analysis_type = "erp"
    elif data_shape == "epoched":
        analysis_type = "erp"
    else:
        analysis_type = "resting"

    research_goal = args.get("research_goal", "")
    project_scale = args.get("project_scale", "unknown")
    stage = args.get("stage", "planning")
    event_types = args.get("event_types", [])
    srate = args.get("srate")
    has_ica = args.get("has_ica", False)
    has_continuous_raw = args.get("has_continuous_raw")
    has_behavioral_log = args.get("has_behavioral_log")
    blockers, not_recommended = _research_blockers(
        analysis_type=analysis_type,
        event_types=event_types,
        analysis_events=analysis_events,
        data_shape=data_shape,
        has_channel_locations=has_channel_locations,
        has_ica=has_ica,
        has_continuous_raw=has_continuous_raw,
        has_behavioral_log=has_behavioral_log,
        project_scale=project_scale,
    )

    common = [
        "eeglab_init",
        "eeglab_load_data",
        "eeglab_info recording/channel/event audit",
        "eeglab_qc_report",
    ]
    parameters: dict[str, Any] = {
        "analysis_type_requested": requested_analysis_type,
        "analysis_type_resolved": analysis_type,
        "research_goal": research_goal,
        "project_scale": project_scale,
        "stage": stage,
        "event_types": event_types,
        "srate": srate,
        "has_ica": has_ica,
        "data_shape": data_shape,
        "has_channel_locations": has_channel_locations,
        "analysis_event_types": analysis_events,
        "has_continuous_raw": has_continuous_raw,
        "has_behavioral_log": has_behavioral_log,
    }
    gate_results = official_gate_summaries(analysis_type, context=parameters)
    official_alignment = gate_results[0]
    base_hints = [
        "Preserve the raw dataset; write transformed outputs to a new path.",
        "Report acquisition/recording facts before analysis: sampling rate, duration, channel count, montage/channel-location coverage, reference, event labels/counts, and processing history.",
        "Audit event latencies and labels before event-locked analyses.",
    ]
    required_user_decisions: list[str] = []
    clarifying_questions: list[str] = []
    default_assumptions: list[str] = []

    if not research_goal:
        required_user_decisions.append("primary research goal or hypothesis")
        clarifying_questions.append(
            "What is the primary research goal: ERP, resting-state spectrum/connectivity, time-frequency, ICA cleanup, source localization, or group/STUDY analysis?"
        )
        default_assumptions.append(
            f"No research_goal was supplied; using analysis_type_resolved={analysis_type} from event/data-shape hints."
        )
    if project_scale == "unknown":
        required_user_decisions.append("project scale and grouping")
        clarifying_questions.append("Is this single-subject, multi-subject, BIDS/STUDY, or exploratory QC work?")
        default_assumptions.append(
            "Project scale is unknown; start with single-subject provenance/QC before group-level assumptions."
        )
    if analysis_type in {"erp", "timefreq"} and not analysis_events:
        required_user_decisions.append("event labels and task conditions")
        clarifying_questions.append(
            "Which event labels define the conditions/epochs, and what epoch/baseline windows match the study design?"
        )
        default_assumptions.append(
            "No confirmed analysis event labels were supplied; inspect event semantics and avoid event-locked analysis until labels are confirmed."
        )
    if has_channel_locations is False:
        required_user_decisions.append("montage/channel-location repair")
        clarifying_questions.append(
            "Can you provide the cap montage/channel-location file, or should analysis avoid topography/source outputs?"
        )
    if srate is None:
        required_user_decisions.append("sampling rate and acquisition details")
        clarifying_questions.append(
            "What sampling rate, reference, amplifier/cap montage, and acquisition filters were used if not preserved in the file?"
        )

    if analysis_type == "erp":
        steps = common + [
            "eeglab_filter bandpass 0.1-40 Hz or study-specific cutoffs",
            "optional eeglab_clean_line_noise",
            ("optional ICA review" if has_ica else "optional eeglab_run_ica + eeglab_classify_ica"),
            "eeglab_epoch with explicit event_types",
            "eeglab_erp_analysis",
            "eeglab_save_data to a new output path",
        ]
        hints = base_hints + [
            "Use event audit first; ERP is not meaningful without validated condition/trigger labels."
        ]
        if not analysis_events:
            hints.append("No analysis_event_types were resolved; run eeglab_event_semantics_audit before epoching.")
    elif analysis_type == "resting":
        steps = common + [
            "eeglab_filter highpass 0.5/1 Hz and lowpass 45/80 Hz as appropriate",
            "eeglab_clean_line_noise",
            "optional conservative eeglab_clean_rawdata",
            "eeglab_reref",
            "eeglab_spectral",
        ]
        hints = base_hints + ["Avoid event-locked interpretations for resting-state outputs."]
    elif analysis_type == "timefreq":
        steps = common + [
            "inspect events and epoch windows",
            "eeglab_filter with study-specific high-frequency ceiling",
            "eeglab_epoch",
            "eeglab_timefreq with explicit cycles/freq_range/baseline",
        ]
        hints = base_hints + ["Time-frequency settings should be justified by the frequencies of interest."]
    elif analysis_type == "ica":
        steps = common + [
            "filter for ICA, commonly highpass 1 Hz",
            "remove/interpolate clearly bad channels when justified",
            "eeglab_run_ica",
            "eeglab_classify_ica",
            "review before eeglab_remove_components",
        ]
        hints = base_hints + ["Do not automatically remove components without reporting thresholds and classes."]
    elif analysis_type == "study":
        steps = common + [
            "organize BIDS/datasets",
            "eeglab_method_preflight bids_import or study_create",
            "eeglab_study_create",
            "eeglab_method_preflight study_design",
            "eeglab_study_design",
            "eeglab_method_preflight study_statistics",
            "eeglab_study_statistics",
        ]
        hints = base_hints + [
            "Run stable single-subject preprocessing before group-level STUDY statistics.",
            "Use staged BIDS/STUDY gates: bids_metadata, bids_import or study_create, study_design, then study_statistics.",
        ]
    else:
        steps = common + [
            "confirm ICA and channel locations",
            "eeglab_source_settings",
            "eeglab_source_localization",
        ]
        hints = base_hints + ["Source localization requires correct channel locations and DIPFIT resources."]

    if srate and srate > 500:
        hints.append("Consider resampling for computational efficiency after confirming analysis requirements.")
    if has_channel_locations is False:
        hints.append(
            "Channel locations are missing; load or repair montage metadata before topography/source workflows."
        )
    if data_shape == "epoched" and analysis_type in {"ica", "resting"}:
        hints.append(
            "The data appears epoched; confirm this is appropriate before ICA or resting-state spectral analysis."
        )

    branch_workflow = branch_workflow_details(
        analysis_type,
        completed_steps=steps,
        required_outputs=[
            "derivative_set",
            "protocol_export",
            "final_report",
        ],
        branch_variant=("connectivity" if analysis_type == "connectivity" else None),
    )

    project_phases = [
        "0_project_intake: define hypothesis, project scale, subject/session structure, data format, and required outputs",
        "1_recording_provenance_audit: preserve raw files; inspect sampling rate, data shape, duration, channel montage, reference, event markers, BIDS/comments, and history",
        "2_qc_gate_before_processing: verify loadability, event integrity, channel-location coverage, missing metadata, and plugin prerequisites",
        "3_single_subject_preprocessing: apply transparent filtering, line-noise cleanup, rereferencing, bad-channel handling, ICA/ICLabel when justified, and save named intermediates",
        "4_analysis_branch: run ERP, resting-state spectral/connectivity, time-frequency, source, or STUDY workflow according to validated design",
        "5_output_and_reporting: save processed datasets/figures/tables, report exact parameters and limitations, and avoid clinical claims",
        "6_project_evolution: turn repeated failures/decisions into updated protocol notes, eval prompts, and skill guidance after review",
    ]
    qc_gates = DEFAULT_QC_GATES
    adaptive_decision_rules = [
        "If research_goal is missing, ask for it; if unavailable, infer a conservative first-pass path from events and data_shape.",
        "If event_types are present, ERP/time-frequency branches are candidates; if events are absent, prefer resting-state QC/spectral analysis.",
        "If data_shape is epoched, avoid resting-state or ICA assumptions until the original continuous data or study design is confirmed.",
        "If channel locations are incomplete, avoid topography/source localization until montage metadata is repaired.",
        "If ICA is absent, run ICA only after continuous-data suitability, filtering, rank/reference, and plugin availability are checked.",
        "For multi-subject or BIDS projects, stabilize single-subject preprocessing before STUDY/group statistics.",
    ]
    self_evolution_hooks = [
        "Capture missing metadata, failed tools, plugin gaps, and parameter decisions in the session report.",
        "After a project pattern repeats, update workflow references/evals so future agents ask the right questions earlier.",
        "Do not silently change scientific defaults; record each default, rationale, and condition under which it should be revised.",
        "Prefer adding eval prompts for new research patterns before treating them as supported workflows.",
    ]

    return workflow_success(
        "eeglab_workflow_recommend",
        steps=[{"name": step, "status": "recommended"} for step in steps],
        parameters=parameters,
        outputs={},
        summary={
            "analysis_type_requested": requested_analysis_type,
            "analysis_type_resolved": analysis_type,
            "project_phases": project_phases,
            "recommended_steps": steps,
            "hints": hints,
            "required_user_decisions": required_user_decisions,
            "clarifying_questions": clarifying_questions,
            "default_assumptions": default_assumptions,
            "blocking_conditions": blockers,
            "not_recommended": not_recommended,
            "analysis_event_types": analysis_events,
            "research_grade_next_step": (
                "Resolve blocking_conditions before processing."
                if blockers
                else "Proceed through qc_gates before any destructive processing."
            ),
            "qc_gates": qc_gates,
            "adaptive_decision_rules": adaptive_decision_rules,
            "self_evolution_hooks": self_evolution_hooks,
            "minimum_report_fields": [
                "input_path",
                "output_path",
                "sampling_rate_hz",
                "duration_sec",
                "channel_count",
                "channel_location_coverage",
                "reference",
                "event_labels_and_counts",
                "filter_cutoffs",
                "rereference",
                "epoch_and_baseline_windows",
                "artifact_rejection_or_ica_decisions",
                "software_and_plugin_limitations",
            ],
            "official_alignment": official_alignment,
            "gate_results": gate_results,
            "branch_workflow": branch_workflow,
            "method_profile_id": official_alignment.get("method_profile_id", ""),
            "source_claim_ids": official_alignment.get("source_claim_ids", []),
        },
    )


def event_semantics_audit(args: dict[str, Any]) -> dict[str, Any]:
    """Classify event markers before deriving epochs or condition tables."""
    event_types = _as_string_list(args.get("event_types"))
    event_counts_raw = args.get("event_counts") if isinstance(args.get("event_counts"), dict) else {}
    event_counts = {str(key): value for key, value in event_counts_raw.items()}
    if not event_types:
        event_types = list(event_counts)

    event_descriptions = args.get("event_descriptions") if isinstance(args.get("event_descriptions"), dict) else {}
    boundary_markers = {_norm_label(item) for item in _as_string_list(args.get("boundary_markers"))}
    condition_markers = {_norm_label(item) for item in _as_string_list(args.get("condition_markers"))}
    segment_markers = {_norm_label(item) for item in _as_string_list(args.get("segment_markers"))}
    exclude_markers = {_norm_label(item) for item in _as_string_list(args.get("exclude_markers"))}

    classifications: list[dict[str, Any]] = []
    analysis_events: list[str] = []
    excluded_events: list[str] = []
    boundary_events: list[str] = []
    segment_events: list[str] = []
    impedance_events: list[str] = []
    candidate_events: list[str] = []

    for label in event_types:
        key = _norm_label(label)
        role = _event_role_from_semantics(label, event_descriptions)
        reason = "heuristic fallback"
        if key in condition_markers:
            role = "condition"
            reason = "listed in condition_markers"
        elif key in exclude_markers:
            role = "excluded"
            reason = "listed in exclude_markers"
        elif key in boundary_markers:
            role = "boundary"
            reason = "listed in boundary_markers"
        elif key in segment_markers:
            role = "segment_marker"
            reason = "listed in segment_markers"
        elif role:
            reason = "event_descriptions mapping"
        elif "impedance" in key:
            role = "impedance"
            reason = "label contains impedance"
        elif "boundary" in key or key in {"s1000", "start", "end", "new segment"}:
            role = "boundary"
            reason = "common boundary/start/end marker"
        elif key in {"sync", "pause", "resume", "calibration"}:
            role = "qc_annotation"
            reason = "common acquisition/QC annotation"
        else:
            role = "candidate_trigger"
            reason = "not identified as boundary/QC/excluded"

        count = event_counts.get(label, event_counts.get(key))
        row = {"label": label, "role": role, "count": count, "reason": reason}
        classifications.append(row)
        if role == "condition":
            analysis_events.append(label)
        elif role == "candidate_trigger":
            candidate_events.append(label)
        elif role == "boundary":
            boundary_events.append(label)
        elif role == "segment_marker":
            segment_events.append(label)
        elif role == "impedance":
            impedance_events.append(label)
        else:
            excluded_events.append(label)

    confirmed_analysis = analysis_events[:]
    candidate_analysis = candidate_events[:]
    blocker: list[str] = []
    if not confirmed_analysis and not candidate_analysis:
        blocker.append("No condition-level ERP/time-frequency trigger remains after event semantics classification.")

    segment_pair_count = None
    if segment_events:
        segment_total = sum(int(event_counts.get(label, 0) or 0) for label in segment_events)
        if segment_total:
            segment_pair_count = segment_total // 2 if segment_total % 2 == 0 else None

    return workflow_success(
        "eeglab_event_semantics_audit",
        steps=[{"name": "classify_event_semantics", "status": "success"}],
        parameters={
            "event_types": event_types,
            "event_counts": event_counts,
            "boundary_markers": sorted(boundary_markers),
            "condition_markers": sorted(condition_markers),
            "segment_markers": sorted(segment_markers),
            "exclude_markers": sorted(exclude_markers),
        },
        outputs={},
        summary={
            "classifications": classifications,
            "confirmed_analysis_events": confirmed_analysis,
            "candidate_analysis_events_need_confirmation": candidate_analysis,
            "excluded_events": excluded_events,
            "boundary_events": boundary_events,
            "segment_events": segment_events,
            "impedance_events": impedance_events,
            "segment_pair_count_if_sequential": segment_pair_count,
            "blocking_conditions": blocker,
            "recommended_next_step": (
                "Ask the user for condition codes or behavioral logs before ERP/time-frequency analysis."
                if blocker
                else "Use only confirmed_analysis_events for epoching; confirm candidate triggers before analysis claims."
            ),
            "not_recommended": [
                "Do not epoch around boundary, impedance, excluded, or segment-only markers.",
                "Do not treat experiment start/end markers as ERP triggers unless the user supplies a task-condition mapping.",
            ],
        },
    )


def project_plan(args: dict[str, Any]) -> dict[str, Any]:
    """Create a research-grade EEG project plan without running MATLAB."""
    event_types = _as_string_list(args.get("event_types"))
    event_semantics = args.get("event_semantics") if isinstance(args.get("event_semantics"), dict) else {}
    analysis_type = args.get("analysis_type", "auto")
    project_scale = args.get("project_scale", "unknown")
    data_shape = args.get("data_shape")
    if data_shape == "unknown":
        data_shape = None
    analysis_events = _analysis_event_types(event_types, event_semantics)
    if analysis_type == "auto":
        if analysis_events:
            resolved = "erp"
        elif project_scale == "bids_study":
            resolved = "study"
        elif data_shape == "epoched":
            resolved = "erp"
        else:
            resolved = "resting"
    else:
        resolved = analysis_type

    has_ica = args.get("has_ica")
    has_channel_locations = args.get("has_channel_locations")
    has_continuous_raw = args.get("has_continuous_raw")
    has_behavioral_log = args.get("has_behavioral_log")
    blockers, not_recommended = _research_blockers(
        analysis_type=resolved,
        event_types=event_types,
        analysis_events=analysis_events,
        data_shape=data_shape,
        has_channel_locations=has_channel_locations,
        has_ica=has_ica,
        has_continuous_raw=has_continuous_raw,
        has_behavioral_log=has_behavioral_log,
        project_scale=project_scale,
    )
    official_context = {
        "event_roles": (list(event_semantics.values()) if isinstance(event_semantics, dict) else []),
        "data_shape": data_shape,
        "has_ica": has_ica,
        "has_channel_locations": has_channel_locations,
        "has_continuous_raw": has_continuous_raw,
        "project_scale": project_scale,
        "condition_markers": analysis_events,
    }
    gate_results = official_gate_summaries(resolved, context=official_context)
    official_alignment = gate_results[0]

    steps = [
        "project_intake",
        "raw_preservation_and_output_dir_policy",
        "recording_provenance_audit",
        "event_semantics_audit",
        "plugin_doctor_if_needed",
        "qc_gate_before_processing",
        f"analysis_branch_{resolved}",
        "protocol_export",
        "report_outputs_and_limitations",
    ]
    if resolved in {"ica", "erp", "timefreq", "source", "study"}:
        steps.insert(6, "preprocessing_decision_tree")
    if resolved == "source":
        steps.insert(7, "source_prerequisite_gate")
    if resolved == "study":
        steps.insert(7, "staged_bids_study_gates")
        steps.insert(8, "single_subject_protocol_lock_before_group_statistics")

    required_user_decisions: list[str] = []
    if not args.get("research_goal"):
        required_user_decisions.append("primary research goal/hypothesis")
    if resolved in {"erp", "timefreq"} and not analysis_events:
        required_user_decisions.append("task-condition event codes or behavioral log")
    if has_channel_locations is False:
        required_user_decisions.append("montage/channel-location repair file or decision to avoid topography/source")
    if project_scale == "unknown":
        required_user_decisions.append("single-subject vs multi-subject/BIDS/STUDY scope")

    quick_modes = {
        "quick_qc": "Load/QC/events/history only; no data modification.",
        "safe_erp": "ERP branch only after event semantics identify condition triggers.",
        "segment_qc": "For start/end-only marker data; report segment durations and avoid ERP claims.",
        "study_ready_check": "Staged BIDS/STUDY gates: bids_metadata, bids_import or study_create, study_design, and study_statistics.",
        "plugin_doctor": "Check clean_rawdata, ICLabel, DIPFIT, BIDS, LIMO, and SIFT availability before dependent steps.",
    }

    branch_workflow = branch_workflow_details(
        resolved,
        completed_steps=steps,
        required_outputs=_as_string_list(args.get("required_outputs")),
        branch_variant=("connectivity" if resolved == "connectivity" else None),
    )

    return workflow_success(
        "eeglab_project_plan",
        steps=[{"name": step, "status": "planned"} for step in steps],
        parameters={
            "research_goal": args.get("research_goal", ""),
            "analysis_type_requested": analysis_type,
            "analysis_type_resolved": resolved,
            "project_scale": project_scale,
            "data_format": args.get("data_format", ""),
            "data_shape": data_shape,
            "event_types": event_types,
            "analysis_event_types": analysis_events,
            "srate": args.get("srate"),
            "subject_count": args.get("subject_count"),
            "session_count": args.get("session_count"),
            "has_channel_locations": has_channel_locations,
            "has_behavioral_log": has_behavioral_log,
            "has_continuous_raw": has_continuous_raw,
            "required_outputs": _as_string_list(args.get("required_outputs")),
        },
        outputs={},
        summary={
            "product_advantage": [
                "Uses eeglab_* tools for executable EEGLAB work instead of asking the user to write MATLAB scripts.",
                "Uses skill/MCP policy for reproducible parameters, QC gates, event semantics, provenance, and limitations.",
                "Keeps EEG data local and exchanges cross-MCP state only through explicit files.",
            ],
            "project_phases": steps,
            "qc_gates": DEFAULT_QC_GATES,
            "blocking_conditions": blockers,
            "not_recommended": not_recommended,
            "required_user_decisions": required_user_decisions,
            "quick_modes": quick_modes,
            "official_reference_anchors": OFFICIAL_REFERENCES,
            "official_claim_count": len(OFFICIAL_CLAIMS),
            "official_alignment": official_alignment,
            "gate_results": gate_results,
            "branch_workflow": branch_workflow,
            "staged_study_gate_methods": (list(STUDY_STAGE_METHODS) if resolved == "study" else []),
            "recommended_next_step": (
                "Resolve blocking_conditions and required_user_decisions before destructive preprocessing."
                if blockers or required_user_decisions
                else "Run quick_qc, then export a protocol before destructive preprocessing."
            ),
        },
    )


def protocol_export_payload(args: dict[str, Any]) -> dict[str, Any]:
    """Build and optionally write a Markdown or JSON research protocol."""
    format_name = args.get("format", "markdown")
    if format_name not in {"markdown", "json"}:
        raise ValueError("format must be markdown or json")
    parameters = args.get("parameters") if isinstance(args.get("parameters"), dict) else {}
    outputs = args.get("outputs") if isinstance(args.get("outputs"), dict) else {}
    qc_gates = _as_string_list(args.get("qc_gates")) or DEFAULT_QC_GATES
    steps = _as_string_list(args.get("steps")) or [
        "project_intake",
        "quick_qc",
        "workflow_recommend",
        "analysis_branch",
    ]
    limitations = _as_string_list(args.get("limitations")) or LIMITATIONS
    research_goal = str(args.get("research_goal", "")).strip()
    analysis_type = str(args.get("analysis_type", "")).strip()
    gate_results = _gate_results_from_args(args)
    source_claim_ids = _source_claim_ids_from_protocol_args(args, gate_results)
    missing_requirements = _as_string_list(args.get("missing_requirements"))
    for gate in gate_results:
        for item in _as_list(gate.get("missing_requirements")):
            if isinstance(item, dict) and item.get("id"):
                missing_requirements.append(str(item["id"]))
        missing_requirements.extend(_as_list(gate.get("missing_requirement_ids")))
    missing_requirements = _unique_strings(missing_requirements)
    override_used = bool(args.get("override_used"))
    if not override_used:
        override_used = any(bool(gate.get("override_used")) for gate in gate_results)
    override_reason = str(args.get("override_reason", "") or "").strip()
    if not override_reason:
        override_reason = next(
            (
                str(gate.get("override_reason", "")).strip()
                for gate in gate_results
                if str(gate.get("override_reason", "")).strip()
            ),
            "",
        )
    blocked_acknowledged = _unique_strings(
        _as_list(args.get("blocked_requirements_acknowledged"))
        + [item for gate in gate_results for item in _as_list(gate.get("blocked_requirements_acknowledged"))]
    )
    report_field_coverage = _report_field_coverage(args)
    gate_coverage_status = "provided" if gate_results else "not_provided"
    override_status = {
        "override_used": override_used,
        "override_reason": override_reason if override_used else "",
        "blocked_requirements_acknowledged": (blocked_acknowledged if override_used else []),
    }

    protocol = {
        "research_goal": research_goal,
        "analysis_type": analysis_type,
        "steps": steps,
        "parameters": parameters,
        "qc_gates": qc_gates,
        "outputs": outputs,
        "limitations": limitations,
        "official_gate_results": gate_results,
        "gate_coverage_status": gate_coverage_status,
        "source_claim_ids": source_claim_ids,
        "missing_requirements": missing_requirements,
        "override_status": override_status,
        "report_field_matrix_coverage": report_field_coverage,
        "branch_workflow": branch_workflow_details(
            analysis_type,
            completed_steps=_as_string_list(steps),
            figure_paths=_as_string_list(outputs.get("figure_paths")),
            output_paths=_as_string_list(outputs.get("output_paths")),
            blocker_messages=missing_requirements,
            required_outputs=_as_string_list(outputs.get("required_outputs")),
            branch_variant=("connectivity" if analysis_type == "connectivity" else None),
        ),
        "official_reference_anchors": OFFICIAL_REFERENCES,
    }

    if format_name == "json":
        rendered = json.dumps(protocol, ensure_ascii=False, indent=2)
    else:
        refs = "\n".join(f"- {ref['name']}: {ref['url']} ({ref['use']})" for ref in OFFICIAL_REFERENCES)
        gate_lines = (
            [_gate_result_line(gate) for gate in gate_results]
            if gate_results
            else ["- Gate coverage status: not_provided"]
        )
        field_lines = [
            (f"- `{group}`: {details['coverage_status']}; " f"provided={details['provided_fields']}")
            for group, details in report_field_coverage.items()
        ]
        rendered = "\n".join(
            [
                "# EEGLAB Research Protocol",
                "",
                f"- Research goal: {research_goal or 'not specified'}",
                f"- Analysis type: {analysis_type or 'not specified'}",
                f"- Source claim IDs: {source_claim_ids or []}",
                f"- Gate coverage status: {gate_coverage_status}",
                "",
                "## Workflow Steps",
                *[f"- {step}" for step in steps],
                "",
                "## QC Gates",
                *[f"- {gate}" for gate in qc_gates],
                "",
                "## Parameters",
                "```json",
                json.dumps(parameters, ensure_ascii=False, indent=2),
                "```",
                "",
                "## Outputs",
                "```json",
                json.dumps(outputs, ensure_ascii=False, indent=2),
                "```",
                "",
                "## Official Gate Results",
                *gate_lines,
                "",
                "## Override Status",
                f"- override_used: {override_used}",
                f"- override_reason: {override_reason if override_used else ''}",
                f"- blocked_requirements_acknowledged: {blocked_acknowledged if override_used else []}",
                "",
                "## Report Field Matrix Coverage",
                *field_lines,
                "",
                "## Limitations",
                *[f"- {item}" for item in limitations],
                "",
                "## Official Reference Anchors",
                refs,
                "",
            ]
        )

    written_path = ""
    output_path = str(args.get("output_path", "")).strip()
    if output_path:
        path = Path(output_path).expanduser().resolve()
        if path.suffix.lower() in {
            ".set",
            ".fdt",
            ".eeg",
            ".vhdr",
            ".vmrk",
            ".edf",
            ".bdf",
            ".cnt",
        }:
            raise ValueError("protocol output_path must not target EEG data or raw sidecar file extensions")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
        written_path = str(path)

    return workflow_success(
        "eeglab_protocol_export",
        steps=[{"name": "render_protocol", "status": "success"}]
        + ([{"name": "write_protocol_file", "status": "success"}] if written_path else []),
        parameters={
            "format": format_name,
            "output_path": output_path,
            "research_goal": research_goal,
            "analysis_type": analysis_type,
        },
        outputs={"protocol_text": rendered, "written_path": written_path},
        summary={
            "qc_gates": qc_gates,
            "step_count": len(steps),
            "official_reference_count": len(OFFICIAL_REFERENCES),
            "source_claim_ids": source_claim_ids,
            "gate_results": gate_results,
            "gate_coverage_status": gate_coverage_status,
            "missing_requirements": missing_requirements,
            "override_status": override_status,
            "report_field_matrix_coverage": report_field_coverage,
            "branch_workflow": protocol["branch_workflow"],
            "official_alignment": {
                "source": "local_official_claim_map",
                "claim_count": len(source_claim_ids),
            },
            "recommended_next_step": "Attach this protocol to the project report and keep exact tool parameters synchronized after each processing change.",
        },
    )


def method_preflight_workflow(args: dict[str, Any]) -> dict[str, Any]:
    """Return workflow-shaped official method gate evaluation."""
    result = evaluate_method_preflight(args)
    return workflow_success(
        "eeglab_method_preflight",
        steps=[{"name": "evaluate_official_method_gates", "status": result["gate_status"]}],
        parameters={
            "method": args.get("method", ""),
            "tool_name": args.get("tool_name", ""),
            "strictness": args.get("strictness", "hard"),
            "context": (args.get("context", {}) if isinstance(args.get("context"), dict) else {}),
            "override_reason": args.get("override_reason", ""),
        },
        outputs={},
        summary=result,
    )


def light_erp_parameters(args: dict[str, Any]) -> dict[str, Any]:
    """Normalize light ERP workflow parameters."""
    output_dir = str(Path(args["output_dir"]).resolve())
    output_filename = safe_output_filename(args.get("output_filename"), default="light_erp_processed.set")
    output_path = Path(output_dir) / output_filename
    return {
        "data_path": str(Path(args["data_path"]).resolve()),
        "output_dir": output_dir,
        "output_filename": output_filename,
        "output_path": str(output_path),
        "output_fdt_path": str(output_path.with_suffix(".fdt")),
        "low_cutoff": args.get("low_cutoff", 0.5),
        "high_cutoff": args.get("high_cutoff", 40.0),
        "event_types": args.get("event_types", ["target", "standard"]),
        "epoch_window": args.get("epoch_window", [-0.2, 0.8]),
        "baseline_window": args.get("baseline_window", [-200, 0]),
        "channels": args.get("channels", ["Cz"]),
        "time_window": args.get("time_window", [250, 450]),
    }
