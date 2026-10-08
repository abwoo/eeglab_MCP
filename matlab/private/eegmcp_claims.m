function doc = eegmcp_claims()
%EEGMCP_CLAIMS The official alignment document (claims and method profiles).
%   Reads generated/eeglab-official-claims.json, the same file the Python
%   server publishes as eeglab://official/claims.json, once per session.

persistent cached
if isempty(cached)
    root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
    path = fullfile(root, 'generated', 'eeglab-official-claims.json');
    cached = jsondecode(fileread(path));
end
doc = cached;
end
