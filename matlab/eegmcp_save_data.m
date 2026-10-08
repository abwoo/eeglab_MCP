function eegmcp_save_data(options)
%EEGMCP_SAVE_DATA Save the current dataset to a .set file (MCP tool eeglab_save_data).
%   filepath is the absolute path of the .set file to write; the folder is
%   created when needed. With filename, the file is written under that name
%   in the folder of filepath (filepath may then also be the folder itself).
%   Uses pop_saveset, which may also write a .fdt data file next to it.
%   Save derivatives under a new name rather than over the raw input.

try
    opts = eegmcp_options(options);
    if eegmcp_require(opts, {'filepath'})
        return
    end
    errors = eegmcp_b1_check(opts, {'filepath', 'string'; 'filename', 'string'});
    if isempty(errors) && ~eegmcp_b1_present(opts, 'filepath')
        errors{end + 1} = 'filepath must not be empty';
    end
    if ~isempty(errors)
        eegmcp_b1_invalid('eeglab_save_data', errors);
        return
    end
    filepath = strtrim(char(opts.filepath));
    filename = strtrim(char(eegmcp_opt(opts, 'filename', '')));

    dataset = eegmcp_current_dataset();
    if isempty(dataset)
        eegmcp_fail('no_dataset', 'No dataset is loaded.', 'Call eeglab_load_data first.');
        return
    end

    [folder, name, ext] = fileparts(filepath);
    if ~isempty(filename)
        if isfolder(filepath) || isempty(ext)
            folder = filepath;
        end
        [~, name, ext] = fileparts(filename);
    end
    if ~isempty(ext) && ~strcmpi(ext, '.set')
        eegmcp_fail('invalid_arguments', ['Only .set files can be written, not ' ext '.'], ...
            'Use a file name ending in .set.');
        return
    end
    if isempty(name)
        eegmcp_fail('invalid_arguments', 'The file name is empty.', ...
            'Pass a file path such as C:/data/sub-01_filtered.set.');
        return
    end
    if isempty(folder)
        folder = pwd;
    end
    if ~isfolder(folder)
        mkdir(folder);
    end
    saved_path = fullfile(folder, [name '.set']);

    warnings = {};
    if ~isempty(dataset.filename) && ~isempty(dataset.filepath) && ...
            strcmp(fullfile(char(dataset.filepath), char(dataset.filename)), saved_path)
        warnings{end + 1} = 'The dataset was saved over the file it was loaded from.';
    end

    com = '';
    evalc('[dataset, com] = pop_saveset(dataset, ''filename'', [name ''.set''], ''filepath'', folder);');
    dataset = eegmcp_b1_hist(dataset, com);
    eegmcp_commit(dataset);

    result.status = 'success';
    result.saved_path = saved_path;
    files = {saved_path};
    data_file = fullfile(folder, [name '.fdt']);
    if isfile(data_file)
        files{end + 1} = data_file;
    end
    result.saved_files = files;
    result.nbchan = dataset.nbchan;
    result.pnts = dataset.pnts;
    result.trials = dataset.trials;
    result.warnings = warnings;
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('save_failed', err.message, 'Check that the output folder is writable.');
end
end
