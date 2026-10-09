function doc = eegmcp_claims()
%EEGMCP_CLAIMS The official alignment document (claims and method profiles).
%   Uses the versioned MATLAB method-gate definitions and regression expectations.
%   eeglab_official_claims returns, once per session.

persistent cached
if isempty(cached)
    root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
    path = fullfile(root, 'generated', 'eeglab-official-claims.json');
    cached = jsondecode(fileread(path));
end
doc = cached;
end
