"""Source-localization handlers for the EEGLAB MCP server."""

from __future__ import annotations

import json

from mcp.types import TextContent

try:
    from .runtime import matlab, matlab_string, _arr, _maybe_init
except ImportError:  # pragma: no cover - direct script execution support
    from runtime import matlab, matlab_string, _arr, _maybe_init


async def _eeglab_source_localization(args: dict) -> list[TextContent]:
    """源定位分析（偶极子拟合）。"""
    component_indices = args.get("component_indices", [])
    head_model = args.get("head_model", "bem")
    template = args.get("template", "mni")

    if component_indices:
        comp_str = _arr(component_indices)
    else:
        comp_str = "1:size(EEG.icaweights,1)"

    # Bug fix: pop_dipfit_settings 需要完整参数
    if head_model == "bem":
        hdmfile = "standard_bem.mat"
    else:
        hdmfile = "standard_vol.mat"

    coord = "MNI" if template == "mni" else "Colin27"

    # Determine chanfile and mrifile based on template
    if template == "mni":
        chanfile = "standard-10-5-cap385.elp"
        mrifile = "standard_mri.mat"
    else:
        chanfile = "standard-10-5-cap385.elp"
        mrifile = "colin27_mri.mat"

    head_model_lit = matlab_string(head_model)
    template_lit = matlab_string(template)
    hdmfile_lit = matlab_string(hdmfile)
    chanfile_lit = matlab_string(chanfile)
    mrifile_lit = matlab_string(mrifile)
    coord_lit = matlab_string(coord)

    code = f"""
{_maybe_init()}
if ~exist('EEG', 'var') || ~isstruct(EEG) || ~isfield(EEG, 'icaweights') || isempty(EEG.icaweights)
    result.status = 'error';
    result.error = '尚未运行 ICA 分解，请先调用 eeglab_run_ica';
else
    EEG = pop_dipfit_settings(EEG, 'hdmfile', {hdmfile_lit}, 'chanfile', {chanfile_lit}, 'mrifile', {mrifile_lit}, 'coordformat', {coord_lit});
    EEG = pop_multifit(EEG, {comp_str});
    result.head_model = {head_model_lit};
    result.template = {template_lit};
    result.ncomponents = length({comp_str});
    if isfield(EEG, 'dipfit') && ~isempty(EEG.dipfit)
        dipoles = struct();
        comp_list = {comp_str};
        for i = 1:length(comp_list)
            ci = comp_list(i);
            if length(EEG.dipfit) >= ci && ~isempty(EEG.dipfit(ci).dippos)
                comp_name = ['comp_' num2str(ci)];
                dipoles.(comp_name).position_x = EEG.dipfit(ci).dippos(1);
                dipoles.(comp_name).position_y = EEG.dipfit(ci).dippos(2);
                dipoles.(comp_name).position_z = EEG.dipfit(ci).dippos(3);
                dipoles.(comp_name).residual_variance = EEG.dipfit(ci).rv;
            end
        end
        result.dipoles = dipoles;
    end
end
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


async def _eeglab_source_settings(args: dict) -> list[TextContent]:
    """Dipfit 模型设置。"""
    head_model = args.get("head_model", "bem")
    template = args.get("template", "mni")
    chanfile = args.get("chanfile", "")
    mrifile = args.get("mrifile", "")

    if head_model == "bem":
        hdmfile = "standard_bem.mat"
    else:
        hdmfile = "standard_vol.mat"

    coord = "MNI" if template == "mni" else "Colin27"

    if not chanfile:
        chanfile = "standard-10-5-cap385.elp"
    if not mrifile:
        mrifile = "standard_mri.mat" if template == "mni" else "colin27_mri.mat"

    head_model_lit = matlab_string(head_model)
    template_lit = matlab_string(template)
    hdmfile_lit = matlab_string(hdmfile)
    chanfile_lit = matlab_string(chanfile)
    mrifile_lit = matlab_string(mrifile)
    coord_lit = matlab_string(coord)

    code = f"""
{_maybe_init()}
EEG = pop_dipfit_settings(EEG, 'hdmfile', {hdmfile_lit}, 'chanfile', {chanfile_lit}, 'mrifile', {mrifile_lit}, 'coordformat', {coord_lit});
result.head_model = {head_model_lit};
result.template = {template_lit};
result.hdmfile = {hdmfile_lit};
result.chanfile = {chanfile_lit};
result.mrifile = {mrifile_lit};
result.coordformat = {coord_lit};
"""

    result = await matlab.execute(code)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
