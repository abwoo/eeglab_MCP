function text = eegmcp_b2_type_text(value)
%EEGMCP_B2_TYPE_TEXT Event type as trimmed text (numeric types via num2str).

if isnumeric(value) || islogical(value)
    text = strtrim(num2str(value));
elseif ischar(value) || isstring(value)
    text = strtrim(char(value));
else
    text = '';
end
end
