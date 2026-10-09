function run_eegmcp_gate_tests(cases_file)
%RUN_EEGMCP_GATE_TESTS Check requirement semantics and all official gate profiles.
%   Frozen regression expectations cover empty contexts, explicit evidence,
%   hard/advisory modes, tool routing and recorded overrides.

if nargin < 1
    cases_file = fullfile(fileparts(mfilename('fullpath')), 'fixtures', 'gate_cases.json');
end

addpath(fileparts(fileparts(mfilename('fullpath'))));
cases = jsondecode(fileread(cases_file));

failures = {};
checks = as_cells(cases.checks);
for k = 1:numel(checks)
    item = checks{k};
    actual = eegmcp_check_requirement(item.check, context_of(item));
    if actual ~= item.expected
        failures{end + 1} = sprintf('check %s: actual %d, expected %d, context %s', ...
            item.check, actual, item.expected, jsonencode(context_of(item))); %#ok<AGROW>
    end
end
fprintf('ok: %d requirement regression checks\n', numel(checks) - numel(failures));

preflight = as_cells(cases.preflight);
mismatches = 0;
for k = 1:numel(preflight)
    item = preflight{k};
    result = eegmcp_preflight_eval(item.method, item.tool_name, context_of(item), ...
        item.strictness, item.override_reason);
    actual_missing = cellfun(@(r) r.id, result.missing_requirements, 'UniformOutput', false);
    expected_missing = as_cells(item.missing_ids);
    if ~strcmp(result.gate_status, item.gate_status) || ~strcmp(result.method_profile_id, item.method_profile_id) ...
            || ~isequal(sort(actual_missing), sort(expected_missing))
        mismatches = mismatches + 1;
        failures{end + 1} = sprintf('preflight %s/%s: actual %s, expected %s', item.method, item.tool_name, ...
            result.gate_status, item.gate_status); %#ok<AGROW>
    end
end
fprintf('ok: %d official preflight regression checks\n', numel(preflight) - mismatches);

if ~isempty(failures)
    fprintf('%s\n', failures{1:min(end, 40)});
    error('eegmcp:test', '%d gate cases differ from their regression expectations', numel(failures));
end
end

function ctx = context_of(item)
ctx = item.context;
if ~isstruct(ctx)
    ctx = struct();
end
end

function items = as_cells(value)
if iscell(value)
    items = value(:)';
elseif isstruct(value)
    items = num2cell(value(:)');
elseif isempty(value)
    items = {};
else
    items = {value};
end
end
