function result = eegmcp_with_gate(result, gate)
%EEGMCP_WITH_GATE Attach the gate outcome to a high-risk tool's result.
%   Mirrors _with_official_gate_metadata in server.py.

result.official_gate = gate;
if isfield(gate, 'override_used') && isequal(gate.override_used, true)
    result.override_used = true;
    result.override_reason = gate.override_reason;
    result.blocked_requirements_acknowledged = gate.blocked_requirements_acknowledged;
end
end
