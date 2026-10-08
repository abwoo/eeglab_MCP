function eegmcp_plot_erp(options)
%EEGMCP_PLOT_ERP Save ERP waveforms of the current epoched dataset (MCP tool eeglab_plot_erp).
%   Draws one panel per channel with the trial-average waveform. With
%   conditions, each condition is the set of epochs whose time-locking
%   event (latency 0) has that type, and the conditions are overlaid. A
%   shaded band shows the 95% confidence interval of the mean
%   (1.96 x standard error). The figure is written to output_path (PNG
%   unless the extension says otherwise). The dataset is not changed.

try
    opts = eegmcp_options(options);
    if eegmcp_require(opts, {'channels', 'output_path'})
        return
    end
    output_path = eegmcp_text(opts.output_path);
    if isempty(strtrim(output_path))
        eegmcp_fail('invalid_arguments', 'output_path must be a non-empty path', ...
            'Pass the absolute path of the output image.');
        return
    end
    conditions = eegmcp_cellstr(eegmcp_opt(opts, 'conditions', {}));

    dataset = eegmcp_current_dataset();
    if isempty(dataset)
        eegmcp_fail('no_dataset', 'No dataset is loaded.', 'Call eeglab_load_data first.');
        return
    end
    if dataset.trials < 2
        eegmcp_fail('not_epoched', 'ERP plots need epoched data.', 'Call eeglab_epoch first.');
        return
    end
    [chans, missing] = eegmcp_b3_channels(dataset, opts.channels);
    if ~isempty(missing)
        eegmcp_fail('unknown_channels', ['Channels not found: ' strjoin(missing, ', ')], ...
            'Call eeglab_info to list the channel labels.');
        return
    end
    if isempty(chans)
        eegmcp_fail('invalid_arguments', 'channels must list at least one channel', ...
            'Pass channel labels, for example ["Cz", "Pz"].');
        return
    end

    if isempty(conditions)
        groups = {1:dataset.trials};
        names = {'all trials'};
    else
        locking = locking_types(dataset);
        groups = cell(1, numel(conditions));
        for c = 1:numel(conditions)
            groups{c} = find(cellfun(@(types) any(strcmp(types, conditions{c})), locking));
        end
        empty = conditions(cellfun(@isempty, groups));
        if ~isempty(empty)
            eegmcp_fail('no_trials_for_condition', ['No epoch is time-locked to: ' strjoin(empty, ', ')], ...
                'Call eeglab_get_events to list the event types, then retry.');
            return
        end
        names = conditions;
    end

    labels = eegmcp_b3_labels(dataset, chans);
    times = dataset.times;
    colors = lines(numel(groups));
    fig = figure('Visible', 'off', 'Position', [100 100 800 max(300, 220 * numel(chans))]);
    cleanup = onCleanup(@() close_figure(fig));
    counts = cell(1, numel(groups));
    for k = 1:numel(chans)
        subplot(numel(chans), 1, k);
        hold on
        handles = gobjects(1, numel(groups));
        for c = 1:numel(groups)
            trials = double(squeeze(dataset.data(chans(k), :, groups{c})));
            if isvector(trials)
                trials = trials(:);
            end
            erp = mean(trials, 2)';
            sem = std(trials, 0, 2)' / sqrt(max(1, size(trials, 2)));
            fill([times, fliplr(times)], [erp + 1.96 * sem, fliplr(erp - 1.96 * sem)], colors(c, :), ...
                'FaceAlpha', 0.2, 'EdgeColor', 'none');
            handles(c) = plot(times, erp, 'Color', colors(c, :), 'LineWidth', 1.5);
            counts{c} = struct('condition', names{c}, 'n_trials', numel(groups{c}));
        end
        xline(0, ':');
        yline(0, ':');
        hold off
        xlim([times(1), times(end)]);
        ylabel([labels{k} ' (uV)'], 'Interpreter', 'none');
        if k == 1
            legend(handles, names, 'Interpreter', 'none', 'Location', 'best');
            title_text = eegmcp_text(eegmcp_opt(opts, 'title', ''));
            if ~isempty(title_text)
                title(title_text, 'Interpreter', 'none');
            end
        end
        if k == numel(chans)
            xlabel('Time (ms)');
        end
    end
    eegmcp_b3_save_figure(fig, output_path);
    clear cleanup

    result.status = 'success';
    result.output_path = output_path;
    result.file_exists = isfile(output_path);
    result.channels = labels;
    result.conditions = counts;
    result.time_range_ms = [times(1), times(end)];
    result.confidence_band = '95% CI of the mean (1.96 x SEM)';
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('plot_erp_failed', err.message, 'Check the channels, conditions and output_path, then retry.');
end
end

function locking = locking_types(dataset)
% For each epoch, the types (as text) of the events at latency 0.
locking = repmat({{}}, 1, dataset.trials);
if ~isfield(dataset, 'epoch') || numel(dataset.epoch) ~= dataset.trials || ...
        ~isfield(dataset.epoch, 'eventtype')
    return
end
for k = 1:dataset.trials
    types = dataset.epoch(k).eventtype;
    lats = dataset.epoch(k).eventlatency;
    if ~iscell(types)
        types = {types};
    end
    if ~iscell(lats)
        lats = num2cell(lats);
    end
    keep = cellfun(@(v) isnumeric(v) && ~isempty(v) && abs(v(1)) < 1e-3, lats);
    locking{k} = cellfun(@type_text, types(keep), 'UniformOutput', false);
end
end

function text = type_text(value)
if isnumeric(value) || islogical(value)
    text = num2str(value);
else
    text = char(value);
end
end

function close_figure(fig)
if isgraphics(fig)
    close(fig);
end
end
