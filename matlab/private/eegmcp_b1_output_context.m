function derived = eegmcp_b1_output_context(opts, derived)
%EEGMCP_B1_OUTPUT_CONTEXT Add the output facts every gated tool derives in server.py.
%   Uses the versioned MATLAB method-gate definitions and regression expectations.
%   derivative_output_planned (true when output_dir or output_path is set)
%   and the output folder or path to the gate context.

if eegmcp_b1_present(opts, 'output_dir') || eegmcp_b1_present(opts, 'output_path') || ...
        eegmcp_b1_present(opts, 'filepath')
    if ~isfield(derived, 'derivative_output_planned')
        derived.derivative_output_planned = eegmcp_b1_present(opts, 'output_dir') || ...
            eegmcp_b1_present(opts, 'output_path');
    end
    names = {'output_dir', 'output_path'};
    for k = 1:numel(names)
        if eegmcp_b1_present(opts, names{k}) && ~isfield(derived, names{k})
            derived.(names{k}) = opts.(names{k});
        end
    end
end
end
