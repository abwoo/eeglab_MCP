function missing = eegmcp_require(opts, names)
%   Uses the versioned MATLAB method-gate definitions and regression expectations.
%   NAMES is a cell array of option names. When any is missing this prints
%   the missing_required_argument error and returns true, so the caller
%   just returns.

absent = names(~cellfun(@(n) isfield(opts, n) && ~(isnumeric(opts.(n)) && isempty(opts.(n))), names));
missing = ~isempty(absent);
if missing
    result = struct('status', 'error', 'code', 'missing_required_argument', ...
        'error', ['missing required options: ' strjoin(absent, ', ')], ...
        'next_step', 'supply the missing options, then retry.', ...
        'details', struct('missing', {absent}));
    eegmcp_emit(result);
end
end
