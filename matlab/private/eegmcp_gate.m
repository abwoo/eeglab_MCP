function [gate, blocked] = eegmcp_gate(tool_name, opts, derived)
%EEGMCP_GATE Run the method gate for a high-risk tool before it executes.
%   CONTEXT is options.method_context, plus the DERIVED facts the tool reads
%   from its own arguments, without replacing facts in method_context. When
%   the gate blocks, this prints the official_gate_blocked error and BLOCKED
%   is true, so the caller just returns.

if nargin < 3
    derived = struct();
end
ctx = eegmcp_opt(opts, 'method_context', struct());
if ~isstruct(ctx)
    ctx = struct();
end
names = fieldnames(derived);
for k = 1:numel(names)
    if ~isfield(ctx, names{k})
        ctx.(names{k}) = derived.(names{k});
    end
end

reason = '';
if isequal(eegmcp_opt(opts, 'override_gate', false), true)
    reason = eegmcp_text(eegmcp_opt(opts, 'override_reason', ''));
end
gate = eegmcp_preflight_eval('', tool_name, ctx, 'hard', reason);
blocked = strcmp(gate.gate_status, 'blocked');
if blocked
    result = struct('status', 'error', 'code', 'official_gate_blocked', ...
        'error', [tool_name ' is blocked by an official precondition gate.'], ...
        'next_step', gate.safe_next_step, 'details', gate);
    eegmcp_emit(result);
end
end
