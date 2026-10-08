function eegmcp_init(eeglab_path)
%EEGMCP_INIT Start EEGLAB without its GUI (MCP tool eeglab_init).
%   EEGMCP_INIT(EEGLAB_PATH) adds EEGLAB_PATH to the MATLAB path and runs
%   "eeglab nogui". Pass an empty string to use the EEGLAB already on the
%   MATLAB path, or the EEGLAB_PATH environment variable.

eeglab_path = char(eeglab_path);
if isempty(eeglab_path)
    eeglab_path = getenv('EEGLAB_PATH');
end

try
    if ~isempty(eeglab_path)
        if ~isfolder(eeglab_path)
            eegmcp_fail('eeglab_path_not_found', ['EEGLAB folder not found: ' eeglab_path], ...
                'Pass the absolute path of the EEGLAB installation folder.');
            return
        end
        addpath(eeglab_path);
    end
    if exist('eeglab', 'file') ~= 2
        eegmcp_fail('eeglab_not_found', 'eeglab.m is not on the MATLAB path.', ...
            'Pass eeglab_path, or set the EEGLAB_PATH environment variable.');
        return
    end

    % EEGLAB prints its startup log; keep it out of the tool result.
    evalc('eeglab(''nogui'');');

    result.status = 'success';
    result.eeglab_version = eeg_getversion;
    result.eeglab_path = fileparts(which('eeglab'));
    eegmcp_emit(result);
catch err
    eegmcp_fail('eeglab_init_failed', err.message, ...
        'Check the EEGLAB installation folder and the MATLAB version.');
end
end
