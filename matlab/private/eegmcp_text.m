function text = eegmcp_text(value)
%EEGMCP_TEXT Text form of a JSON value, used where the gates compare strings.
%   Char stays as is; anything else is JSON-encoded, so true becomes 'true'.

if ischar(value)
    text = value;
elseif isstring(value) && isscalar(value)
    text = char(value);
else
    text = jsonencode(value);
end
end
