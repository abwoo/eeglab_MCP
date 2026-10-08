function eegmcp_load_data(filepath)
%EEGMCP_LOAD_DATA Load an EEG file as the current EEGLAB dataset (MCP tool eeglab_load_data).
%   Supports .set, .edf, .bdf, .vhdr and .cnt files. The file on disk is
%   not modified. The dataset is stored with eeg_store, so it becomes the
%   current dataset of the EEGLAB session.

global EEG ALLEEG CURRENTSET

filepath = char(filepath);
try
    if exist('pop_loadset', 'file') ~= 2
        eegmcp_fail('eeglab_not_initialized', 'EEGLAB functions are not on the MATLAB path.', ...
            'Call eeglab_init first.');
        return
    end
    if ~isfile(filepath)
        eegmcp_fail('file_not_found', ['File not found: ' filepath], ...
            'Pass the absolute path of an existing EEG file.');
        return
    end

    [folder, name, ext] = fileparts(filepath);
    switch lower(ext)
        case '.set'
            load_command = 'loaded = pop_loadset(''filename'', [name ext], ''filepath'', folder);';
        case {'.edf', '.bdf'}
            load_command = 'loaded = pop_biosig(filepath);';
        case '.vhdr'
            load_command = 'loaded = pop_loadbv(folder, [name ext]);';
        case '.cnt'
            load_command = 'loaded = pop_loadcnt(filepath);';
        otherwise
            eegmcp_fail('unsupported_format', ['Unsupported file extension: ' ext], ...
                'Use a .set, .edf, .bdf, .vhdr or .cnt file.');
            return
    end

    % Loaders print progress; keep it out of the tool result.
    evalc(load_command);
    evalc('[ALLEEG, EEG, CURRENTSET] = eeg_store(ALLEEG, loaded, 0);');

    info = eegmcp_dataset_info(EEG);
    result.status = 'success';
    result.current_set = CURRENTSET;
    result.setname = info.setname;
    result.nbchan = info.nbchan;
    result.srate = info.srate;
    result.pnts = info.pnts;
    result.trials = info.trials;
    result.duration_sec = info.duration_sec;
    result.channel_labels = info.channel_labels;
    result.event_types = info.event_types;
    result.num_events = info.num_events;
    eegmcp_emit(result);
catch err
    eegmcp_fail('load_failed', err.message, ...
        'Check that the file format plugin (for example BIOSIG or bva-io) is installed.');
end
end
