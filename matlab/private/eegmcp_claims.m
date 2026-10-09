function doc = eegmcp_claims()
%EEGMCP_CLAIMS The official alignment document (claims and method profiles).
%   Cache the source document returned by eeglab_official_claims once per session.

persistent cached
if isempty(cached)
    root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
    path = fullfile(root, 'generated', 'eeglab-official-claims.json');
    cached = jsondecode(fileread(path));
end
doc = cached;
end
