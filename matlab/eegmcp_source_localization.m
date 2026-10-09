function eegmcp_source_localization(options)
%EEGMCP_SOURCE_LOCALIZATION Fit equivalent dipoles to ICA components with DIPFIT (MCP tool eeglab_source_localization).
%   Applies the DIPFIT template settings (as eeglab_source_settings does)
%   unless the dataset already has DIPFIT settings and neither head_model
%   nor template is given, then runs pop_multifit (grid scan plus
%   nonlinear fit, single dipole, no rejection threshold) on the requested
%   components (default: all). Returns each dipole position, moment and
%   residual variance, and stores the model in EEG.dipfit. Needs ICA and
%   the DIPFIT and FieldTrip-lite plugins.

try
    opts = eegmcp_options(options);
    [head_model, template, derived, message] = eegmcp_b3_source_opts(opts);
    comps = eegmcp_numeric(eegmcp_opt(opts, 'component_indices', []), 'component_indices');
    if isempty(message) && any(comps < 1 | comps ~= round(comps))
        message = 'component_indices must be positive integers (1-based)';
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

    [gate, blocked] = eegmcp_gate('eeglab_source_localization', opts, derived);
    if blocked
        return
    end

    if ~isfield(dataset, 'icaweights') || isempty(dataset.icaweights)
        eegmcp_fail('no_ica', 'ICA has not been run on the current dataset.', 'Call eeglab_run_ica first.');
        return
    end
    ncomp = size(dataset.icaweights, 1);
    if isempty(comps)
        comps = 1:ncomp;
    end
    comps = unique(comps, 'stable');
    if any(comps > ncomp)
        eegmcp_fail('invalid_arguments', sprintf('component_indices must be between 1 and %d', ncomp), ...
            'Adjust component_indices, then retry.');
        return
    end

    has_settings = isfield(dataset, 'dipfit') && isstruct(dataset.dipfit) && ...
        isfield(dataset.dipfit, 'hdmfile') && ~isempty(dataset.dipfit.hdmfile);
    explicit = isfield(opts, 'head_model') || isfield(opts, 'template');
    if has_settings && ~explicit
        problem = '';
        if exist('pop_multifit', 'file') ~= 2 || exist('ft_dipolefitting', 'file') ~= 2
            problem = 'DIPFIT needs the DIPFIT and FieldTrip-lite plugins, which are not both installed.';
        end
        settings = struct('reused_existing_settings', true, 'coordformat', dataset.dipfit.coordformat);
        head_model = 'existing DIPFIT settings';
        template = 'existing DIPFIT settings';
    else
        [dataset, settings, problem] = eegmcp_b3_dipfit(dataset, head_model, template, '', '');
    end
    if ~isempty(problem)
        eegmcp_fail('plugin_missing', problem, 'Install the missing EEGLAB plugin, then retry.');
        return
    end

    evalc('dataset = pop_multifit(dataset, comps, ''threshold'', 100, ''dipplot'', ''off'');');
    eegmcp_commit(dataset);

    dipoles = cell(1, numel(comps));
    for k = 1:numel(comps)
        ci = comps(k);
        entry = struct('component', ci, 'position', [], 'moment', [], ...
            'residual_variance_percent', [], 'good_fit', false);
        if ci <= numel(dataset.dipfit.model) && ~isempty(dataset.dipfit.model(ci).posxyz)
            model = dataset.dipfit.model(ci);
            entry.position = model.posxyz(1, :);
            entry.moment = model.momxyz(1, :);
            entry.residual_variance_percent = model.rv * 100;
            entry.good_fit = ~isnan(model.rv) && model.rv < 0.15;
        end
        dipoles{k} = entry;
    end

    result.status = 'success';
    result.head_model = head_model;
    result.template = template;
    result.settings = settings;
    result.coordinate_system = dataset.dipfit.coordformat;
    result.ncomponents = numel(comps);
    result.n_good_fits = sum(cellfun(@(d) d.good_fit, dipoles));
    result.dipoles = dipoles;
    result.note = 'A residual variance below 15 percent is usually taken as a good fit.';
    result = eegmcp_with_gate(result, gate);
    eegmcp_emit(result);
catch err
    if strcmp(err.identifier, 'eegmcp:options')
        eegmcp_fail('invalid_options', err.message, 'Pass options as a JSON object.');
        return
    end
    eegmcp_fail('source_localization_failed', err.message, ...
        'Call eeglab_source_settings, check the channel coregistration, then retry.');
end
end
