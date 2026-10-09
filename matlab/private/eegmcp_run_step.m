function result = eegmcp_run_step(function_name, varargin)
%EEGMCP_RUN_STEP Call a MATLAB tool and capture its single JSON result.
text = evalc('feval(function_name, varargin{:});');
result = jsondecode(strtrim(text));
end
