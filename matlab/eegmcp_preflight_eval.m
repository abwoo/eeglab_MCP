function result = eegmcp_preflight_eval(method, tool_name, ctx, strictness, override_reason)
%EEGMCP_PREFLIGHT_EVAL Evaluate an official method gate in MATLAB.
%   METHOD or TOOL_NAME selects the method profile. CTX is a struct with the
%   facts the user has confirmed. STRICTNESS is 'hard' (the default) or
%   'advisory'. A non-empty OVERRIDE_REASON accepts missing critical
%   requirements and records why.

strictness = lower(char(strictness));
if isempty(strictness)
    strictness = 'hard';
end
override_reason = strtrim(char(override_reason));
[profile_id, profile] = resolve_profile(char(method), char(tool_name));

if isempty(profile_id)
    result = struct();
    result.method_profile_id = '';
    result.gate_status = 'unknown_method';
    result.official_requirements = {};
    result.missing_requirements = {};
    result.not_recommended = {['Do not treat an unmapped method as officially aligned until it ' ...
        'is added to the claim map.']};
    result.safe_next_step = ['Use a mapped method/tool name or update the official claim map before ' ...
        'treating this workflow as supported.'];
    result.source_claim_ids = {};
    result.override_used = false;
    result.official_alignment = struct('strictness', strictness, 'source', 'local_official_claim_map');
    return
end

requirements = num2cell(profile.requirements(:)');
missing = {};
for k = 1:numel(requirements)
    if ~eegmcp_check_requirement(requirements{k}.check, ctx)
        missing{end + 1} = requirements{k}; %#ok<AGROW>
    end
end
is_critical = cellfun(@(r) strcmp(r.severity, 'critical'), missing);
critical = missing(is_critical);
advisory = missing(~is_critical);
override_used = ~isempty(critical) && ~isempty(override_reason);

if ~isempty(critical) && ~override_used
    if any(strcmp(strictness, {'hard', 'strict', 'default'}))
        gate_status = 'blocked';
    else
        gate_status = 'advisory';
    end
    next_step = ['Resolve missing critical requirements before execution, or rerun with override_reason ' ...
        'when the user explicitly accepts the risk.'];
elseif override_used
    gate_status = 'override_accepted';
    next_step = 'Proceed only with the override rationale recorded in provenance/protocol outputs.';
elseif ~isempty(advisory)
    gate_status = 'advisory';
    next_step = 'Proceed after recording advisory gaps in the report/protocol.';
else
    gate_status = 'pass';
    next_step = 'Proceed with the mapped EEGLAB method and preserve parameters/provenance.';
end

result = struct();
result.method_profile_id = profile_id;
result.gate_status = gate_status;
result.official_requirements = requirements;
result.missing_requirements = missing;
result.critical_missing_requirements = critical;
result.advisory_missing_requirements = advisory;
result.not_recommended = as_cell(profile.not_recommended);
result.safe_next_step = next_step;
result.source_claim_ids = as_cell(profile.source_claim_ids);
result.override_used = override_used;
if override_used
    result.override_reason = override_reason;
    result.blocked_requirements_acknowledged = cellfun(@(r) r.id, critical, 'UniformOutput', false);
else
    result.override_reason = '';
    result.blocked_requirements_acknowledged = {};
end
result.official_alignment = struct('strictness', strictness, 'source', 'local_official_claim_map', ...
    'claim_count', numel(result.source_claim_ids));
end

function [profile_id, profile] = resolve_profile(method, tool_name)
doc = eegmcp_claims();
profile_id = '';
profile = [];
if ~isempty(tool_name) && isfield(doc.tool_to_profile, tool_name)
    profile_id = doc.tool_to_profile.(tool_name);
    profile = doc.method_profiles.(matlab.lang.makeValidName(profile_id));
    return
end
key = lower(strtrim(method));
if isempty(key)
    key = lower(strtrim(tool_name));
end
names = fieldnames(doc.method_profiles);
% Exact profile names take precedence over aliases in other profiles.
hit = find(strcmp(key, names), 1);
if ~isempty(hit)
    profile_id = names{hit};
    profile = doc.method_profiles.(profile_id);
    return
end
for k = 1:numel(names)
    candidate = doc.method_profiles.(names{k});
    if strcmp(key, names{k}) || any(strcmp(key, lower(as_cell(candidate.aliases))))
        profile_id = names{k};
        profile = candidate;
        return
    end
end
end

function items = as_cell(value)
if iscell(value)
    items = value(:)';
elseif isempty(value)
    items = {};
else
    items = {value};
end
end
