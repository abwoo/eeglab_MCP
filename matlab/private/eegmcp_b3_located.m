function located = eegmcp_b3_located(dataset)
%EEGMCP_B3_LOCATED Logical row: which channels have 2-D locations topoplot can draw.
%   A channel counts as located when its chanlocs theta and radius are set,
%   which is what topoplot reads.

located = false(1, dataset.nbchan);
if ~isfield(dataset, 'chanlocs') || isempty(dataset.chanlocs) || ...
        ~isfield(dataset.chanlocs, 'theta') || ~isfield(dataset.chanlocs, 'radius')
    return
end
for k = 1:min(dataset.nbchan, numel(dataset.chanlocs))
    theta = dataset.chanlocs(k).theta;
    radius = dataset.chanlocs(k).radius;
    located(k) = isnumeric(theta) && isscalar(theta) && ~isnan(theta) && ...
        isnumeric(radius) && isscalar(radius) && ~isnan(radius);
end
end
