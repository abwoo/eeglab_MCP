"""Executable handler map for exposed EEGLAB MCP tools."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

try:
    from .handlers_data import (
        _eeglab_history,
        _eeglab_import_bids,
        _eeglab_info,
        _eeglab_init,
        _eeglab_load_data,
        _eeglab_save_data,
    )
    from .handlers_events_erp import (
        _eeglab_average_erp,
        _eeglab_epoch,
        _eeglab_erp_analysis,
        _eeglab_get_events,
        _eeglab_reject_epochs,
        _eeglab_sort_epochs,
    )
    from .handlers_frequency_timefreq import (
        _eeglab_connectivity,
        _eeglab_spectral,
        _eeglab_timefreq,
    )
    from .handlers_ica_artifact import (
        _eeglab_classify_ica,
        _eeglab_flag_components,
        _eeglab_remove_components,
        _eeglab_run_ica,
    )
    from .handlers_preprocessing import (
        _eeglab_clean_line_noise,
        _eeglab_clean_rawdata,
        _eeglab_edit_channels,
        _eeglab_filter,
        _eeglab_interpolate_channels,
        _eeglab_reref,
        _eeglab_resample,
        _eeglab_select_channels,
    )
    from .handlers_source import _eeglab_source_localization, _eeglab_source_settings
    from .handlers_study import (
        _eeglab_pipeline,
        _eeglab_study_create,
        _eeglab_study_design,
        _eeglab_study_statistics,
    )
    from .handlers_visualization import (
        _eeglab_plot_components,
        _eeglab_plot_erp,
        _eeglab_plot_timefreq,
        _eeglab_topoplot,
    )
    from .handlers_workflow import (
        _eeglab_erp_light_workflow,
        _eeglab_event_semantics_audit,
        _eeglab_method_preflight,
        _eeglab_plugin_check,
        _eeglab_project_plan,
        _eeglab_protocol_export,
        _eeglab_qc_report,
        _eeglab_workflow_recommend,
    )
except ImportError:  # pragma: no cover - direct script execution support
    from handlers_data import (
        _eeglab_history,
        _eeglab_import_bids,
        _eeglab_info,
        _eeglab_init,
        _eeglab_load_data,
        _eeglab_save_data,
    )
    from handlers_events_erp import (
        _eeglab_average_erp,
        _eeglab_epoch,
        _eeglab_erp_analysis,
        _eeglab_get_events,
        _eeglab_reject_epochs,
        _eeglab_sort_epochs,
    )
    from handlers_frequency_timefreq import (
        _eeglab_connectivity,
        _eeglab_spectral,
        _eeglab_timefreq,
    )
    from handlers_ica_artifact import (
        _eeglab_classify_ica,
        _eeglab_flag_components,
        _eeglab_remove_components,
        _eeglab_run_ica,
    )
    from handlers_preprocessing import (
        _eeglab_clean_line_noise,
        _eeglab_clean_rawdata,
        _eeglab_edit_channels,
        _eeglab_filter,
        _eeglab_interpolate_channels,
        _eeglab_reref,
        _eeglab_resample,
        _eeglab_select_channels,
    )
    from handlers_source import _eeglab_source_localization, _eeglab_source_settings
    from handlers_study import (
        _eeglab_pipeline,
        _eeglab_study_create,
        _eeglab_study_design,
        _eeglab_study_statistics,
    )
    from handlers_visualization import (
        _eeglab_plot_components,
        _eeglab_plot_erp,
        _eeglab_plot_timefreq,
        _eeglab_topoplot,
    )
    from handlers_workflow import (
        _eeglab_erp_light_workflow,
        _eeglab_event_semantics_audit,
        _eeglab_method_preflight,
        _eeglab_plugin_check,
        _eeglab_project_plan,
        _eeglab_protocol_export,
        _eeglab_qc_report,
        _eeglab_workflow_recommend,
    )

ToolHandler = Callable[[dict[str, Any]], Any]

TOOL_HANDLERS: Mapping[str, ToolHandler] = {
    "eeglab_init": _eeglab_init,
    "eeglab_load_data": _eeglab_load_data,
    "eeglab_save_data": _eeglab_save_data,
    "eeglab_import_bids": _eeglab_import_bids,
    "eeglab_info": _eeglab_info,
    "eeglab_history": _eeglab_history,
    "eeglab_filter": _eeglab_filter,
    "eeglab_resample": _eeglab_resample,
    "eeglab_reref": _eeglab_reref,
    "eeglab_select_channels": _eeglab_select_channels,
    "eeglab_interpolate_channels": _eeglab_interpolate_channels,
    "eeglab_edit_channels": _eeglab_edit_channels,
    "eeglab_clean_line_noise": _eeglab_clean_line_noise,
    "eeglab_clean_rawdata": _eeglab_clean_rawdata,
    "eeglab_run_ica": _eeglab_run_ica,
    "eeglab_classify_ica": _eeglab_classify_ica,
    "eeglab_flag_components": _eeglab_flag_components,
    "eeglab_remove_components": _eeglab_remove_components,
    "eeglab_reject_epochs": _eeglab_reject_epochs,
    "eeglab_get_events": _eeglab_get_events,
    "eeglab_epoch": _eeglab_epoch,
    "eeglab_erp_analysis": _eeglab_erp_analysis,
    "eeglab_sort_epochs": _eeglab_sort_epochs,
    "eeglab_average_erp": _eeglab_average_erp,
    "eeglab_spectral": _eeglab_spectral,
    "eeglab_timefreq": _eeglab_timefreq,
    "eeglab_connectivity": _eeglab_connectivity,
    "eeglab_topoplot": _eeglab_topoplot,
    "eeglab_plot_erp": _eeglab_plot_erp,
    "eeglab_plot_timefreq": _eeglab_plot_timefreq,
    "eeglab_plot_components": _eeglab_plot_components,
    "eeglab_source_localization": _eeglab_source_localization,
    "eeglab_source_settings": _eeglab_source_settings,
    "eeglab_study_create": _eeglab_study_create,
    "eeglab_study_design": _eeglab_study_design,
    "eeglab_study_statistics": _eeglab_study_statistics,
    "eeglab_pipeline": _eeglab_pipeline,
    "eeglab_qc_report": _eeglab_qc_report,
    "eeglab_erp_light_workflow": _eeglab_erp_light_workflow,
    "eeglab_workflow_recommend": _eeglab_workflow_recommend,
    "eeglab_project_plan": _eeglab_project_plan,
    "eeglab_protocol_export": _eeglab_protocol_export,
    "eeglab_plugin_check": _eeglab_plugin_check,
    "eeglab_event_semantics_audit": _eeglab_event_semantics_audit,
    "eeglab_method_preflight": _eeglab_method_preflight,
}
