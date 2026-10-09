function result = eegmcp_rpc_dispatch(message, catalog)
%EEGMCP_RPC_DISPATCH Route MCP requests to the reviewed MATLAB extension only.
switch message.method
    case 'ping'
        result = struct();
    case 'tools/list'
        result = struct('tools', {catalog.tools});
    case 'tools/call'
        params = eegmcp_opt(message, 'params', struct());
        name = eegmcp_opt(params, 'name', '');
        tools = catalog.tools;
        if isstruct(tools)
            tools = num2cell(tools);
        end
        hit = find(cellfun(@(t) strcmp(t.name, name), tools), 1);
        if isempty(hit)
            error('eegmcp:rpc_params', 'Unknown reviewed tool.');
        end
        definition = tools{hit};
        args = eegmcp_opt(params, 'arguments', struct());
        if ~isstruct(args) || ~isscalar(args)
            error('eegmcp:rpc_params', 'Tool arguments must be a JSON object.');
        end
        properties = definition.inputSchema.properties;
        required = eegmcp_cellstr(definition.inputSchema.required);
        if any(~isfield(args, required)) || any(~ismember(fieldnames(args), fieldnames(properties)))
            error('eegmcp:rpc_params', 'Tool arguments do not match its reviewed schema.');
        end
        signature = catalog.signatures.(name);
        order = eegmcp_cellstr(signature.input.order);
        values = cell(1, numel(order));
        for k = 1:numel(order)
            value = args.(order{k});
            type = properties.(order{k}).type;
            valid = (strcmp(type, 'string') && ischar(value)) || ...
                (strcmp(type, 'boolean') && islogical(value) && isscalar(value)) || ...
                (any(strcmp(type, {'number', 'integer'})) && isnumeric(value) && ...
                isscalar(value) && isreal(value) && isfinite(value));
            if strcmp(type, 'integer') && valid
                valid = fix(value) == value;
            end
            if ~valid
                error('eegmcp:rpc_params', 'Tool argument type does not match its reviewed schema.');
            end
            values{k} = value;
        end
        try
            text = evalc('feval(signature.function, values{:});');
            result = struct('content', {{struct('type', 'text', 'text', strtrim(text))}}, 'isError', false);
        catch err
            result = struct('content', {{struct('type', 'text', 'text', err.message)}}, 'isError', true);
        end
    otherwise
        error('eegmcp:rpc_method', 'Unknown MCP method.');
end
end
