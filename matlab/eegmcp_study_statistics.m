function eegmcp_study_statistics(options)
%EEGMCP_STUDY_STATISTICS Test precomputed channel measures with statcond.
%   Correction applies to the complete returned family of p-values. Cluster
%   inference is outside this tool and requires a separately validated model.
global STUDY ALLEEG
try
    opts = eegmcp_options(options);
    eegmcp_validate_options(opts, {'measure', 'string', {'erp', 'spectrum', 'ersp'}; ...
        'alpha', 'positive', []; 'correction', 'string', {'fdr', 'bonferroni', 'none'}; ...
        'channels', 'strings', []; 'method', 'string', {'parametric', 'permutation'}; ...
        'naccu', 'positive', []});
    alpha = eegmcp_opt(opts, 'alpha', 0.05);
    if alpha >= 1
        error('eegmcp:arguments', 'alpha must be between zero and one.');
    end
    if isempty(STUDY) || isempty(ALLEEG)
        eegmcp_fail('no_study', 'No STUDY is active.', 'Create a STUDY and define its design first.');
        return
    end
    measure = eegmcp_opt(opts, 'measure', 'erp');
    correction = eegmcp_opt(opts, 'correction', 'fdr');
    derived = struct('project_scale', 'multi_subject', 'measure', measure, 'alpha', alpha, 'correction', correction);
    [gate, blocked] = eegmcp_gate('eeglab_study_statistics', opts, derived);
    if blocked
        return
    end
    channels = eegmcp_cellstr(eegmcp_opt(opts, 'channels', {}));
    if isempty(channels)
        error('eegmcp:arguments', 'channels must explicitly select the precomputed measure.');
    end
    data = {}; axis_values = [];
    reader = struct('erp', 'std_readerp', 'spectrum', 'std_readspec', 'ersp', 'std_readersp');
    function_name = reader.(measure);
    evalc('[~, data, axis_values] = feval(function_name, STUDY, ALLEEG, ''channels'', channels);');
    if isempty(data) || numel(data) < 2 || any(cellfun(@isempty, data))
        eegmcp_fail('measure_not_precomputed', 'No complete multi-condition measure is available.', ...
            'Precompute the selected measure using std_precomp after locking the single-subject protocol.');
        return
    end
    pairing = 'off';
    if isfield(STUDY, 'currentdesign') && STUDY.currentdesign > 0
        design = STUDY.design(STUDY.currentdesign);
        if ~isempty(design.variable) && isfield(design.variable, 'pairing')
            pairing = design.variable(1).pairing;
        end
    end
    method = eegmcp_opt(opts, 'method', 'parametric');
    naccu = eegmcp_opt(opts, 'naccu', 2000);
    if fix(naccu) ~= naccu
        error('eegmcp:arguments', 'naccu must be a positive integer.');
    end
    pvalues = []; statistics = []; degrees = [];
    evalc('[statistics, degrees, pvalues] = statcond(data, ''method'', method, ''paired'', pairing, ''naccu'', naccu);');
    corrected = correct_family(pvalues, correction);
    result = struct('status', 'success', 'measure', measure, 'alpha', alpha, 'correction', correction, ...
        'method', method, 'paired', pairing, 'channels', {channels}, 'axis', axis_values, ...
        'pvalues', {pvalues}, 'corrected_pvalues', {corrected}, 'statistics', {statistics}, ...
        'degrees_of_freedom', {degrees}, 'correction_family', 'all returned contrasts and sampled cells');
    eegmcp_emit(eegmcp_with_gate(result, gate));
catch err
    eegmcp_workflow_fail(err, 'study_statistics_failed');
end
end

function corrected = correct_family(values, method)
is_cell = iscell(values);
if ~is_cell
    values = {values};
end
sizes = cellfun(@size, values, 'UniformOutput', false);
lengths = cellfun(@numel, values);
flat = cellfun(@(x) x(:), values, 'UniformOutput', false);
flat = vertcat(flat{:});
finite = isfinite(flat);
if strcmp(method, 'bonferroni')
    flat(finite) = min(1, flat(finite) * sum(finite));
elseif strcmp(method, 'fdr')
    [sorted, order] = sort(flat(finite));
    adjusted = sorted .* numel(sorted) ./ (1:numel(sorted))';
    adjusted = min(1, flipud(cummin(flipud(adjusted))));
    restored = adjusted;
    restored(order) = adjusted;
    flat(finite) = restored;
end
corrected = cell(size(values));
offset = 0;
for k = 1:numel(values)
    corrected{k} = reshape(flat(offset + (1:lengths(k))), sizes{k});
    offset = offset + lengths(k);
end
if ~is_cell
    corrected = corrected{1};
end
end
