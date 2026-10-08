function eegmcp_topoplot(options)
%EEGMCP_TOPOPLOT Save a scalp map of the current dataset (MCP tool eeglab_topoplot).
%   Plots, with topoplot, the potential at time_point (ms, nearest sample)
%   or averaged over time_window ([start end] ms). Epoched data are first
%   averaged over trials (the ERP). With neither option the whole epoch
%   (or the whole recording) is averaged. channels restricts the map to a
%   subset of channels. The figure is written to output_path (PNG unless
%   the extension says otherwise). The dataset is not changed.

try
    opts = eegmcp_options(options);
    if eegmcp_require(opts, {'output_path'})
        return
    end
    output_path = eegmcp_text(opts.output_path);
    has_point = isfield(opts, 'time_point') && ~isempty(opts.time_point);
    has_window = isfield(opts, 'time_window') && ~isempty(opts.time_window);
    message = '';
    if isempty(strtrim(output_path))
        message = 'output_path must be a non-empty path';
    elseif has_point && has_window
        message = 'specify exactly one of time_point and time_window';
    elseif has_point && ~(isnumeric(opts.time_point) && isscalar(opts.time_point) && isfinite(opts.time_point))
        message = 'time_point must be a number (ms)';
    elseif has_window
        [time_window, message] = eegmcp_b3_pair(opts, 'time_window', [], false);
    end
    if ~isempty(message)
        eegmcp_fail('invalid_arguments', message, 'Adjust the options, then retry.');
        return
    end

    dataset = eegmcp_current_dataset();
    if isempty(dataset)
        eegmcp_fail('no_dataset', 'No dataset is loaded.', 'Call eeglab_load_data first.');
        return
    end

    derived = struct();
    if has_point || has_window
        derived.parameters_recorded = true;
    end
    if isfield(opts, 'channels') && ~isempty(opts.channels)
        derived.channels = opts.channels;
    end
    derived.output_path = output_path;
    derived.derivative_output_planned = true;
    derived.output_dir = [];
    [gate, blocked] = eegmcp_gate('eeglab_topoplot', opts, derived);
    if blocked
        return
    end

    [chans, missing] = eegmcp_b3_channels(dataset, eegmcp_opt(opts, 'channels', {}));
    if ~isempty(missing)
        eegmcp_fail('unknown_channels', ['Channels not found: ' strjoin(missing, ', ')], ...
            'Call eeglab_info to list the channel labels.');
        return
    end
    located = eegmcp_b3_located(dataset);
    chans = chans(located(chans));
    if numel(chans) < 3
        eegmcp_fail('no_channel_locations', ['Fewer than 3 of the selected channels have ' ...
            'locations; a scalp map cannot be drawn.'], ...
            'Load channel locations with eeglab_edit_channels (action load_loc), then retry.');
        return
    end

    times = dataset.times;
    if has_point
        [~, first] = min(abs(times - opts.time_point));
        last = first;
        plotted = struct('time_point_ms', times(first));
    elseif has_window
        inside = find(times >= time_window(1) & times <= time_window(2));
        if isempty(inside)
            eegmcp_fail('invalid_analysis_window', sprintf(['time_window [%g %g] ms holds no sample; ' ...
                'the data span [%g %g] ms.'], time_window, times(1), times(end)), ...
                'Adjust time_window, then retry.');
            return
        end
        first = inside(1);
        last = inside(end);
        plotted = struct('time_window_ms', [times(first), times(last)]);
    else
        first = 1;
        last = numel(times);
        plotted = struct('time_window_ms', [times(first), times(last)]);
    end
    if has_point && (opts.time_point < times(1) || opts.time_point > times(end))
        eegmcp_fail('invalid_analysis_window', sprintf(['time_point %g ms is outside the data ' ...
            '[%g %g] ms.'], opts.time_point, times(1), times(end)), 'Adjust time_point, then retry.');
        return
    end
    values = mean(mean(double(dataset.data(chans, first:last, :)), 3), 2);

    title_text = eegmcp_text(eegmcp_opt(opts, 'title', ''));
    fig = figure('Visible', 'off');
    cleanup = onCleanup(@() close_figure(fig));
    evalc('topoplot(values, dataset.chanlocs(chans), ''style'', ''both'', ''electrodes'', ''on'');');
    colorbar;
    if ~isempty(title_text)
        title(title_text, 'Interpreter', 'none');
    end
    eegmcp_b3_save_figure(fig, output_path);
    clear cleanup

    result.status = 'success';
    result.output_path = output_path;
    result.file_exists = isfile(output_path);
    result.plotted = plotted;
    result.data_shape = shape_of(dataset);
    result.n_channels = numel(chans);
    result.channels = eegmcp_b3_labels(dataset, chans);
    result.value_range_uv = [min(values), max(values)];
    result = eegmcp_with_gate(result, gate);
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('topoplot_failed', err.message, 'Check the channel locations and output_path, then retry.');
end
end

function shape = shape_of(dataset)
if dataset.trials > 1
    shape = 'epoched (trial average)';
else
    shape = 'continuous';
end
end

function close_figure(fig)
if isgraphics(fig)
    close(fig);
end
end
