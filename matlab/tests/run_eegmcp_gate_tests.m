function run_eegmcp_gate_tests(cases_file)
%RUN_EEGMCP_GATE_TESTS Check the MATLAB method gates against the Python gates.
%   CASES_FILE is written by generate_gate_cases.py. Every case holds a
%   context and what the Python gate decided for it.

addpath(fileparts(fileparts(mfilename('fullpath'))));
cases = jsondecode(fileread(cases_file));

failures = {};
checks = as_cells(cases.checks);
for k = 1:numel(checks)
    item = checks{k};
    actual = eegmcp_check_requirement(item.check, context_of(item));
    if actual ~= item.expected
        failures{end + 1} = sprintf('check %s: MATLAB %d, Python %d, context %s', ...
            item.check, actual, item.expected, jsonencode(context_of(item))); %#ok<AGROW>
    end
end
fprintf('ok: %d requirement checks match Python\n', numel(checks) - numel(failures));

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
        failures{end + 1} = sprintf('preflight %s/%s: MATLAB %s, Python %s', item.method, item.tool_name, ...
            result.gate_status, item.gate_status); %#ok<AGROW>
    end
end
fprintf('ok: %d preflight evaluations match Python\n', numel(preflight) - mismatches);

if ~isempty(failures)
    fprintf('%s\n', failures{1:min(end, 40)});
    error('eegmcp:test', '%d gate cases differ from the Python gates', numel(failures));
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
