function [dataset, settings, problem] = eegmcp_b3_dipfit(dataset, head_model, template, chanfile, mrifile)
%EEGMCP_B3_DIPFIT Apply DIPFIT template settings to DATASET with pop_dipfit_settings.
%   HEAD_MODEL is 'bem' (standardBEM, MNI coordinates) or 'spherical'
%   (standardBESA four-shell sphere). TEMPLATE 'mni' keeps the model's own
%   MRI (standard_mri.mat for BEM, avg152t1.mat for the sphere); 'colin27'
%   uses DIPFIT's standard_BEM/standard_mri.mat, the Colin27 brain in MNI
%   space. CHANFILE and MRIFILE override the template files when not
%   empty. When DIPFIT knows no transform for the dataset's montage, the
%   channels are coregistered to the template by matching labels
%   (coregister 'warp' 'auto'). PROBLEM is '' on success, else the reason
%   DIPFIT is unavailable (the caller reports plugin_missing).

settings = struct();
problem = '';
if exist('pop_dipfit_settings', 'file') ~= 2
    problem = 'The DIPFIT plugin (pop_dipfit_settings) is not on the MATLAB path.';
    return
end
if exist('ft_dipolefitting', 'file') ~= 2
    problem = ['DIPFIT needs the FieldTrip-lite plugin (ft_dipolefitting), which is not installed. ' ...
        'Install it with the EEGLAB extension manager.'];
    return
end

folder = fileparts(which('pop_dipfit_settings'));
if strcmp(head_model, 'bem')
    model = 'standardBEM';
else
    model = 'standardBESA';
end
evalc('dataset = pop_dipfit_settings(dataset, ''model'', model);');
if strcmp(template, 'colin27')
    dataset.dipfit.mrifile = fullfile(folder, 'standard_BEM', 'standard_mri.mat');
end
if ~isempty(mrifile)
    dataset.dipfit.mrifile = mrifile;
end
recompute = false;
if ~isempty(chanfile)
    dataset.dipfit.chanfile = chanfile;
    recompute = true;
end
if recompute || isempty(dataset.dipfit.coord_transform)
    transform = [];
    evalc(['[~, transform] = coregister(dataset.chanlocs, dataset.dipfit.chanfile, ' ...
        '''warp'', ''auto'', ''manual'', ''off'');']);
    dataset.dipfit.coord_transform = transform;
end

settings.head_model = head_model;
settings.template = template;
settings.model = model;
settings.hdmfile = file_text(dataset.dipfit.hdmfile);
settings.mrifile = file_text(dataset.dipfit.mrifile);
settings.chanfile = file_text(dataset.dipfit.chanfile);
settings.coordformat = dataset.dipfit.coordformat;
settings.coord_transform = dataset.dipfit.coord_transform;
settings.n_channels_used = numel(dataset.dipfit.chansel);
end

function text = file_text(value)
if ischar(value)
    text = value;
else
    text = '(in-memory structure)';
end
end
