"""ICA and artifact handlers for the EEGLAB MCP server."""

from __future__ import annotations

import json

from mcp.types import TextContent

try:
    from .runtime import matlab, _arr, _error_response, _maybe_init
except ImportError:  # pragma: no cover - direct script execution support
    from runtime import matlab, _arr, _error_response, _maybe_init


async def _eeglab_run_ica(args: dict) -> list[TextContent]:
    """运行 ICA 分解。"""
    algorithm = args.get("algorithm", "runica")
    pca = args.get("pca_components")
    extended = args.get("extended", True)
    max_steps = args.get("max_steps", 512)

    pca_str = f", 'pca', {pca}" if pca else ""
    ext_val = 1 if extended else 0

    ica_algorithms = {
        "runica": f"EEG = pop_runica(EEG, 'extended', {ext_val}, 'maxsteps', {max_steps}{pca_str});",
        "picard": f"EEG = pop_runica(EEG, 'icatype', 'picard', 'extended', {ext_val}, 'maxsteps', {max_steps}{pca_str});",
    }

    ica_code = ica_algorithms.get(algorithm)
    if not ica_code:
        return _error_response(
            "invalid_arguments",
            f"不支持的 ICA 算法: {algorithm}。仅支持 runica 和 picard",
            next_step="algorithm 只能是 runica 或 picard。",
        )

    code = f"""
{_maybe_init()}
{ica_code}
result.algorithm = '{algorithm}';
result.ncomponents = size(EEG.icaweights, 1);
result.extended = {str(extended).lower()};
result.max_steps = {max_steps};
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_classify_ica(args: dict) -> list[TextContent]:
    """ICLabel 自动分类。"""
    code = f"""
{_maybe_init()}
if ~exist('EEG', 'var') || ~isstruct(EEG) || ~isfield(EEG, 'icaweights') || isempty(EEG.icaweights)
    result.status = 'error';
    result.error = '尚未运行 ICA 分解，请先调用 eeglab_run_ica';
else
    EEG = pop_iclabel(EEG);
    classifications = EEG.etc.ic_classification.ICLabel.classifications;
    labels = {{'Brain', 'Muscle', 'Eye', 'Heart', 'Line_Noise', 'Channel_Noise', 'Other'}};
    n_components = size(classifications, 1);
    result.n_components = n_components;
    result.labels = labels;
    result.classifications = struct();
    for i = 1:n_components
        probs = classifications(i,:);
        [max_prob, max_idx] = max(probs);
        comp_name = ['comp_' num2str(i)];
        result.classifications.(comp_name).predicted_class = labels{{max_idx}};
        result.classifications.(comp_name).max_probability = max_prob;
        for j = 1:length(labels)
            result.classifications.(comp_name).(labels{{j}}) = probs(j);
        end
    end
end
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_flag_components(args: dict) -> list[TextContent]:
    """标记 ICA 成分。"""
    # 7 个类别: Brain, Muscle, Eye, Heart, Line_Noise, Channel_Noise, Other
    param_names = [
        "brain_range",
        "muscle_range",
        "eye_range",
        "heart_range",
        "line_noise_range",
        "channel_noise_range",
        "other_range",
    ]

    rows = []
    for param in param_names:
        r = args.get(param)
        if r and len(r) == 2:
            rows.append(f"{r[0]} {r[1]}")
        else:
            rows.append("NaN NaN")

    matrix_str = "; ".join(rows)

    code = f"""
{_maybe_init()}
if ~exist('EEG', 'var') || ~isstruct(EEG) || ~isfield(EEG, 'icaweights') || isempty(EEG.icaweights)
    result.status = 'error';
    result.error = '尚未运行 ICA 分解，请先调用 eeglab_run_ica';
else
    if ~isfield(EEG, 'etc') || ~isfield(EEG.etc, 'ic_classification') || ~isfield(EEG.etc.ic_classification, 'ICLabel')
        EEG = pop_iclabel(EEG);
    end
    EEG = pop_icflag(EEG, [{matrix_str}]);
    result.flag_thresholds = [{matrix_str}];
    if isfield(EEG, 'reject') && isfield(EEG.reject, 'gcompreject')
        flagged = find(EEG.reject.gcompreject);
        result.flagged_components = flagged';
        result.num_flagged = length(flagged);
    else
        result.flagged_components = [];
        result.num_flagged = 0;
    end
end
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_remove_components(args: dict) -> list[TextContent]:
    """移除 ICA 成分。"""
    component_indices = args.get("component_indices", [])
    auto_threshold = args.get("auto_remove_brain_threshold")

    if auto_threshold is not None:
        remove_code = f"""
if ~exist('EEG', 'var') || ~isstruct(EEG) || ~isfield(EEG, 'icaweights') || isempty(EEG.icaweights)
    result.status = 'error';
    result.error = '尚未运行 ICA 分解，请先调用 eeglab_run_ica';
elseif ~isfield(EEG, 'etc') || ~isfield(EEG.etc, 'ic_classification') || ~isfield(EEG.etc.ic_classification, 'ICLabel')
    result.status = 'error';
    result.error = '尚未运行 ICLabel 分类，请先调用 eeglab_classify_ica';
else
    classifications = EEG.etc.ic_classification.ICLabel.classifications;
    brain_probs = classifications(:,1);
    remove_idx = find(brain_probs < {auto_threshold});
    if isempty(remove_idx)
        result.message = '没有需要移除的成分(所有成分 Brain 概率均高于阈值)';
        result.removed_components = [];
    else
        EEG = pop_subcomp(EEG, remove_idx, 0);
        result.removed_components = remove_idx';
        result.num_removed = length(remove_idx);
        result.remaining_channels = EEG.nbchan;
    end
end
"""
    elif component_indices:
        indices_str = _arr(component_indices)
        remove_code = f"""
EEG = pop_subcomp(EEG, {indices_str}, 0);
result.removed_components = {indices_str};
result.num_removed = length({indices_str});
result.remaining_channels = EEG.nbchan;
"""
    else:
        return _error_response(
            "missing_required_argument",
            "请指定 component_indices 或 auto_remove_brain_threshold",
            next_step="传入要移除的 ICA 成分索引，或传入自动移除阈值后重试。",
        )

    code = f"""
{_maybe_init()}
{remove_code}
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
