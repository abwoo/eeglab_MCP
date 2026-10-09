function eegmcp_plot_timefreq(options)
%EEGMCP_PLOT_TIMEFREQ Save ERSP and/or ITC images of one channel (MCP tool eeglab_plot_timefreq).
%   Computes newtimef (Morlet wavelets, 3 to 80 Hz clipped at Nyquist,
%   cycles [3 10], newtimef's default pre-stimulus baseline) on the channel
%   of the current epoched dataset and writes the ERSP (dB) and ITC images
%   to output_path (PNG unless the extension says otherwise). The dataset
%   is not changed.

try
    opts = eegmcp_options(options);
    if eegmcp_require(opts, {'channel', 'output_path'})
        return
    end
    output_path = eegmcp_text(opts.output_path);
    channel = eegmcp_text(opts.channel);
    [plot_ersp, message] = eegmcp_b3_bool(opts, 'plot_ersp', true);
    if isempty(message)
        [plot_itc, message] = eegmcp_b3_bool(opts, 'plot_itc', true);
    end
    if isempty(message) && isempty(strtrim(output_path))
        message = 'output_path must be a non-empty path';
    end
    if isempty(message) && ~plot_ersp && ~plot_itc
        message = 'at least one of plot_ersp and plot_itc must be true';
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

    derived = struct('derivative_output_planned', true, 'output_dir', [], 'output_path', output_path);
    [gate, blocked] = eegmcp_gate('eeglab_plot_timefreq', opts, derived);
    if blocked
        return
    end

    if dataset.trials < 2
        eegmcp_fail('not_epoched', 'Time-frequency plots need epoched data.', 'Call eeglab_epoch first.');
        return
    end
    [chan, missing] = eegmcp_b3_channels(dataset, {channel});
    if ~isempty(missing) || numel(chan) ~= 1
        eegmcp_fail('unknown_channels', ['Channel not found: ' channel], ...
            'Call eeglab_info to list the channel labels.');
        return
    end

    [ersp, itc, times, freqs, used_freqs] = eegmcp_b3_newtimef(dataset, chan, [3 80], [3 10], []);

    label = eegmcp_b3_labels(dataset, chan);
    title_text = eegmcp_text(eegmcp_opt(opts, 'title', ''));
    if isempty(title_text)
        title_text = label{1};
    end
    panels = {};
    if plot_ersp
        panels{end + 1} = 'ersp';
    end
    if plot_itc
        panels{end + 1} = 'itc';
    end
    fig = figure('Visible', 'off', 'Position', [100 100 800 320 * numel(panels)]);
    cleanup = onCleanup(@() close_figure(fig));
    for p = 1:numel(panels)
        subplot(numel(panels), 1, p);
        if strcmp(panels{p}, 'ersp')
            imagesc(times, freqs, ersp);
            limit = max(abs(ersp(:)));
            if limit > 0
                caxis([-limit, limit]);
            end
            cbar = colorbar;
            ylabel(cbar, 'ERSP (dB)');
            name = 'ERSP';
        else
            imagesc(times, freqs, itc);
            caxis([0, max(eps, max(itc(:)))]);
            cbar = colorbar;
            ylabel(cbar, 'ITC');
            name = 'ITC';
        end
        set(gca, 'YDir', 'normal');
        hold on
        plot([0 0], [freqs(1), freqs(end)], 'k:');
        hold off
        ylabel('Frequency (Hz)');
        title([title_text ' - ' name], 'Interpreter', 'none');
        if p == numel(panels)
            xlabel('Time (ms)');
        end
    end
    colormap(fig, jet(256));
    eegmcp_b3_save_figure(fig, output_path);
    clear cleanup

    result.status = 'success';
    result.output_path = output_path;
    result.file_exists = isfile(output_path);
    result.channel = label{1};
    result.panels = panels;
    result.freq_range = used_freqs;
    result.cycles = [3 10];
    result.baseline = 'newtimef default (all pre-stimulus times)';
    result.n_trials = dataset.trials;
    result.time_range_ms = [min(times), max(times)];
    result = eegmcp_with_gate(result, gate);
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('plot_timefreq_failed', err.message, ['Check that the epochs are at least 1 s long ' ...
        '(3 cycles at 3 Hz) and that output_path is writable, then retry.']);
end
end

function close_figure(fig)
if isgraphics(fig)
    close(fig);
end
end
