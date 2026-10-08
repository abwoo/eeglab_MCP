function eegmcp_b3_save_figure(fig, output_path)
%EEGMCP_B3_SAVE_FIGURE Save a figure to OUTPUT_PATH, creating its folder.
%   A .png path (or one without an extension) is written with print at
%   150 dpi; other extensions use saveas, which picks the format from it.

folder = fileparts(output_path);
if ~isempty(folder) && ~isfolder(folder)
    mkdir(folder);
end
[~, ~, ext] = fileparts(output_path);
if isempty(ext) || strcmpi(ext, '.png')
    print(fig, output_path, '-dpng', '-r150');
else
    saveas(fig, output_path);
end
end
