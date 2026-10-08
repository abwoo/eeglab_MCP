function derived = eegmcp_b2_output_context(opts, derived)
%EEGMCP_B2_OUTPUT_CONTEXT Output facts for the gate, as the last block of
%   _preflight_context_from_arguments in server.py: when the call carries
%   output_dir, output_path or filepath, record whether a separate
%   derivative output is planned. Fields already in DERIVED are kept.

output_dir = eegmcp_opt(opts, 'output_dir', []);
output_path = eegmcp_opt(opts, 'output_path', []);
filepath = eegmcp_opt(opts, 'filepath', []);
if b2_truthy(output_dir) || b2_truthy(output_path) || b2_truthy(filepath)
    derived = set_default(derived, 'derivative_output_planned', b2_truthy(output_dir) || b2_truthy(output_path));
    derived = set_default(derived, 'output_dir', output_dir);
    derived = set_default(derived, 'output_path', output_path);
end
end

function derived = set_default(derived, name, value)
if ~isfield(derived, name)
    derived.(name) = value;
end
end

function ok = b2_truthy(value)
if ischar(value) || isstring(value)
    ok = ~isempty(strtrim(char(value)));
elseif isnumeric(value) || islogical(value)
    ok = ~isempty(value) && (~isscalar(value) || value ~= 0);
else
    ok = ~isempty(value);
end
end
