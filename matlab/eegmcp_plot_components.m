function eegmcp_plot_components(options)
%EEGMCP_PLOT_COMPONENTS Save scalp maps of ICA components (MCP tool eeglab_plot_components).
%   Draws, with topoplot, the scalp map (column of EEG.icawinv) of each
%   requested component in a grid and writes it to output_path (PNG unless
%   the extension says otherwise). Defaults to the first 10 components.
%   The dataset is not changed.

try
    opts = eegmcp_options(options);
    if eegmcp_require(opts, {'output_path'})
        return
    end
    output_path = eegmcp_text(opts.output_path);
    if isempty(strtrim(output_path))
        eegmcp_fail('invalid_arguments', 'output_path must be a non-empty path', ...
            'Pass the absolute path of the output image.');
        return
    end
    comps = eegmcp_numeric(eegmcp_opt(opts, 'component_indices', []), 'component_indices');
    if any(comps < 1 | comps ~= round(comps))
        eegmcp_fail('invalid_arguments', 'component_indices must be positive integers (1-based)', ...
            'Adjust component_indices, then retry.');
        return
    end

    dataset = eegmcp_current_dataset();
    if isempty(dataset)
        eegmcp_fail('no_dataset', 'No dataset is loaded.', 'Call eeglab_load_data first.');
        return
    end
    if ~isfield(dataset, 'icaweights') || isempty(dataset.icaweights)
        eegmcp_fail('no_ica', 'ICA has not been run on the current dataset.', 'Call eeglab_run_ica first.');
        return
    end
    if isempty(dataset.icawinv)
        dataset.icawinv = pinv(dataset.icaweights * dataset.icasphere);
    end
    ncomp = size(dataset.icawinv, 2);
    if isempty(comps)
        comps = 1:min(10, ncomp);
    end
    comps = unique(comps, 'stable');
    if any(comps > ncomp)
        eegmcp_fail('invalid_arguments', sprintf('component_indices must be between 1 and %d', ncomp), ...
            'Adjust component_indices, then retry.');
        return
    end
    chansind = dataset.icachansind;
    if isempty(chansind)
        chansind = 1:size(dataset.icawinv, 1);
    end
    located = eegmcp_b3_located(dataset);
    if sum(located(chansind)) < 3
        eegmcp_fail('no_channel_locations', 'The ICA channels have no usable locations for scalp maps.', ...
            'Load channel locations with eeglab_edit_channels (action load_loc), then retry.');
        return
    end

    ncols = ceil(sqrt(numel(comps)));
    nrows = ceil(numel(comps) / ncols);
    fig = figure('Visible', 'off', 'Position', [100 100 220 * ncols 240 * nrows]);
    cleanup = onCleanup(@() close_figure(fig));
    for k = 1:numel(comps)
        subplot(nrows, ncols, k);
        map = dataset.icawinv(:, comps(k));
        evalc('topoplot(map, dataset.chanlocs(chansind), ''electrodes'', ''off'');');
        title(sprintf('IC %d', comps(k)));
    end
    title_text = eegmcp_text(eegmcp_opt(opts, 'title', ''));
    if ~isempty(title_text)
        sgtitle(title_text, 'Interpreter', 'none');
    end
    eegmcp_b3_save_figure(fig, output_path);
    clear cleanup

    result.status = 'success';
    result.output_path = output_path;
    result.file_exists = isfile(output_path);
    result.components = num2cell(comps);
    result.n_components_total = ncomp;
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('plot_components_failed', err.message, ...
        'Check the ICA decomposition, channel locations and output_path, then retry.');
end
end

function close_figure(fig)
if isgraphics(fig)
    close(fig);
end
end
