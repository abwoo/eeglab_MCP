function output_path = eegmcp_derivative_path(input_path, output_dir, filename)
%EEGMCP_DERIVATIVE_PATH Refuse aliases of raw .set/.fdt files and traversal.
[folder, name, ext] = fileparts(filename);
if ~isempty(folder) || isempty(name) || ~strcmpi(ext, '.set')
    error('eegmcp:arguments', 'output_filename must be a simple .set filename without folders.');
end
if isempty(strtrim(output_dir))
    error('eegmcp:arguments', 'output_dir must identify a derivative directory.');
end
input_path = char(java.io.File(input_path).getCanonicalPath());
output_path = char(java.io.File(fullfile(output_dir, filename)).getCanonicalPath());
[input_folder, input_name] = fileparts(input_path);
[output_folder, output_name] = fileparts(output_path);
input_data = fullfile(input_folder, [input_name '.fdt']);
output_data = fullfile(output_folder, [output_name '.fdt']);
if (ispc && (strcmpi(input_path, output_path) || strcmpi(input_data, output_data))) || ...
        (~ispc && (strcmp(input_path, output_path) || strcmp(input_data, output_data)))
    error('eegmcp:arguments', 'Derivative output must not overwrite the input dataset or its .fdt file.');
end
end
