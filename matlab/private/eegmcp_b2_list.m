function items = eegmcp_b2_list(values)
%EEGMCP_B2_LIST Numeric vector as a 1xN cell, so jsonencode always writes a JSON array.

items = num2cell(double(values(:)'));
end
