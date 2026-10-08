function [head_model, template, derived, message] = eegmcp_b3_source_opts(opts)
%EEGMCP_B3_SOURCE_OPTS Read head_model and template, and the source gate context.
%   DERIVED follows _preflight_context_from_arguments in server.py for
%   eeglab_source_localization and eeglab_source_settings: head_model and
%   template as given (or [] when absent), and a chanfile marks a planned
%   channel-location repair. MESSAGE is '' when the options are valid.

message = '';
head_model = eegmcp_text(eegmcp_opt(opts, 'head_model', 'bem'));
template = eegmcp_text(eegmcp_opt(opts, 'template', 'mni'));
if ~any(strcmp(head_model, {'bem', 'spherical'}))
    message = 'head_model must be one of bem, spherical';
elseif ~any(strcmp(template, {'mni', 'colin27'}))
    message = 'template must be one of mni, colin27';
end
derived = struct();
derived.head_model = eegmcp_opt(opts, 'head_model', []);
derived.template = eegmcp_opt(opts, 'template', []);
chanfile = eegmcp_opt(opts, 'chanfile', '');
if ischar(chanfile) && ~isempty(strtrim(chanfile))
    derived.channel_location_repair_planned = true;
    derived.loc_file = chanfile;
end
end
