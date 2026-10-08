function eegmcp_sort_epochs(options)
%EEGMCP_SORT_EPOCHS Reorder the epochs of the current dataset (MCP tool eeglab_sort_epochs).
%   Options (JSON object): sort_by (string, required): the event field to
%   sort on, for example "type". Epochs are ordered by the value of that
%   field for their time-locking event (stable, so equal values keep their
%   order). Data, ICA activations, epoch and event structures are reordered
%   together.

try
    opts = eegmcp_options(options);
    if isfield(opts, 'sort_by') && (ischar(opts.sort_by) || isstring(opts.sort_by)) && ...
            isempty(strtrim(char(opts.sort_by)))
        opts = rmfield(opts, 'sort_by');
    end
    if eegmcp_require(opts, {'sort_by'})
        return
    end
    sort_by = opts.sort_by;
    if ~(ischar(sort_by) || (isstring(sort_by) && isscalar(sort_by)))
        eegmcp_b2_invalid('eeglab_sort_epochs', {'sort_by must be string'});
        return
    end
    sort_by = strtrim(char(sort_by));

    dataset = eegmcp_current_dataset();
    if isempty(dataset)
        eegmcp_fail('no_dataset', 'No dataset is loaded.', 'Call eeglab_load_data first.');
        return
    end
    if dataset.trials <= 1 || ~isfield(dataset, 'epoch') || isempty(dataset.epoch)
        eegmcp_fail('not_epoched', 'Sorting epochs needs epoched data.', 'Call eeglab_epoch first.');
        return
    end
    if isempty(dataset.event) || ~isfield(dataset.event, sort_by) || ~isfield(dataset.epoch, ['event' sort_by])
        eegmcp_fail('unknown_field', ['Events have no field named ' sort_by '.'], ...
            'Use an event field such as type; eeglab_get_events lists the events.');
        return
    end

    keys = cell(1, dataset.trials);
    for k = 1:dataset.trials
        keys{k} = eegmcp_b2_locking_value(dataset.epoch(k), sort_by);
    end
    numeric = all(cellfun(@(v) (isnumeric(v) || islogical(v)) && isscalar(v), keys));
    if numeric
        [~, order] = sort(cellfun(@double, keys));
    else
        [~, order] = sort(cellfun(@eegmcp_b2_type_text, keys, 'UniformOutput', false));
    end
    order = order(:)';
    dataset = reorder(dataset, order);
    evalc('dataset = eeg_checkset(dataset, ''eventconsistency'');');
    evalc('eegmcp_commit(dataset);');

    result.status = 'success';
    result.sorted_by = sort_by;
    result.trials = dataset.trials;
    result.order = eegmcp_b2_list(order);
    sorted_keys = cell(1, dataset.trials);
    for k = 1:dataset.trials
        sorted_keys{k} = eegmcp_b2_type_text(eegmcp_b2_locking_value(dataset.epoch(k), sort_by));
    end
    result.sorted_values = sorted_keys;
    [result.event_types, result.event_counts] = eegmcp_event_counts(dataset.event);
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('sort_epochs_failed', err.message, 'Check that the data are epoched and sort_by is an event field.');
end
end

function dataset = reorder(dataset, order)
% Move epoch ORDER(k) to position k, keeping events attached to their epoch.
dataset.data = dataset.data(:, :, order);
if isfield(dataset, 'icaact') && ~isempty(dataset.icaact) && size(dataset.icaact, 3) == numel(order)
    dataset.icaact = dataset.icaact(:, :, order);
end
dataset.epoch = dataset.epoch(order);
new_position = zeros(1, numel(order));
new_position(order) = 1:numel(order);
for e = 1:numel(dataset.event)
    old = dataset.event(e).epoch;
    new = new_position(old);
    dataset.event(e).latency = dataset.event(e).latency + (new - old) * dataset.pnts;
    dataset.event(e).epoch = new;
end
% Per-trial rejection marks (rej*, icarej*) follow their trials.
if isfield(dataset, 'reject') && isstruct(dataset.reject)
    names = fieldnames(dataset.reject);
    for k = 1:numel(names)
        value = dataset.reject.(names{k});
        per_trial = (startsWith(names{k}, 'rej') || startsWith(names{k}, 'icarej')) && ...
            ~endsWith(names{k}, 'col');
        if per_trial && (isnumeric(value) || islogical(value)) && ~isempty(value) && ...
                size(value, 2) == numel(order)
            dataset.reject.(names{k}) = value(:, order);
        end
    end
end
end
