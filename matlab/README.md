# EEGLAB MCP tools in pure MATLAB (prototype)

This folder is a Python-free prototype of the EEGLAB MCP server. It does not start its own server. The tools are plain MATLAB functions, and MathWorks' [MATLAB MCP Core Server](https://github.com/matlab/matlab-mcp-core-server) exposes them to MCP clients through its [custom tools](https://github.com/matlab/matlab-mcp-core-server/blob/main/guides/custom-tools.md) extension file.

The prototype exposes 34 tools: the five first-contact tools below, plus 29 data, preprocessing, ICA, ERP, spectral, plotting and source tools. Start with the first-contact sequence:

| MCP tool | MATLAB function | What it does |
| --- | --- | --- |
| `eeglab_init` | `eegmcp_init(eeglab_path)` | Runs `eeglab nogui`. Pass `""` to use the EEGLAB on the MATLAB path or `EEGLAB_PATH`. |
| `eeglab_load_data` | `eegmcp_load_data(filepath)` | Loads `.set`, `.edf`, `.bdf`, `.vhdr` or `.cnt` as the current dataset. |
| `eeglab_info` | `eegmcp_info()` | Dimensions, reference, channel-location coverage, events, ICA, history. |
| `eeglab_get_events` | `eegmcp_get_events()` | Event types, counts and latency range. |
| `eeglab_qc_report` | `eegmcp_qc_report()` | The same summary plus risk and provenance hints. |

Each function prints one JSON object, which the server returns as the tool result. The tools share EEGLAB's own globals (`EEG`, `ALLEEG`, `CURRENTSET`), so a dataset loaded through MCP is the current dataset of that EEGLAB session.

## Setup

1. Install MATLAB R2021a or later and EEGLAB.
2. Download the MATLAB MCP Core Server binary from its [releases page](https://github.com/matlab/matlab-mcp-core-server/releases).
3. Register it in your MCP client with this folder's extension file. Setting the initial working folder to this folder puts the functions on the MATLAB path:

```json
{
  "mcpServers": {
    "eeglab": {
      "command": "C:\\tools\\matlab-mcp-core-server.exe",
      "args": [
        "--extension-file=C:\\path\\to\\eeglab_MCP\\matlab\\eeglab-mcp-tools.json",
        "--initial-working-folder=C:\\path\\to\\eeglab_MCP\\matlab",
        "--matlab-display-mode=nodesktop"
      ]
    }
  }
}
```

If the server connects to a MATLAB session you already have open (`--matlab-session-mode=auto` or `existing`), run `addpath('C:\path\to\eeglab_MCP\matlab')` in that session instead.

## Processing Tools And Method Gates

The extension file additionally registers:

- Data and preprocessing: save, BIDS import, history, filter, resample, rereference, channel selection/interpolation/editing, line-noise cleanup and clean_rawdata.
- ICA and ERP: ICA, ICLabel, component flagging/removal, epoch rejection, epoching, ERP analysis, epoch sorting and averaging.
- Spectral and visualization: spectral power, time-frequency, connectivity, topography, ERP/time-frequency/component plots and source configuration/localization.

These functions take one required `options` string containing a JSON object. Use an empty string or `{}` when no options are needed. For example, a filter call uses `{"filter_type":"bandpass","low_cutoff":1,"high_cutoff":40,"method_context":{"raw_input_preserved":true,"derivative_output_planned":true}}`. High-risk tools evaluate the official method gates before changing data; blocked gates return `official_gate_blocked`. Overrides require an explicit reason and are recorded in the output.

The MATLAB gate evaluator reads `generated/eeglab-official-claims.json`, the same exported profiles as the Python server. CI checks 4,758 requirement cases and 469 preflight evaluations against Python, then exercises the first-contact and three processing batches on the real EEGLAB sample recording. The processing tests include invalid options, missing datasets and gate failures before scientific operations. Tool availability still depends on installed EEGLAB plugins and MATLAB toolboxes.

## Limits of this approach

- Custom tool arguments can only be `string`, `number`, `integer` or `boolean`. Tools that take lists, such as channel or event selections, need those values passed as text.
- The server passes every argument listed in `input.order`, so there are no optional arguments. Every argument is listed as required, and an empty string stands for "not set".
- The MathWorks server exposes custom tools, not the Python server's prompts or resources. Method gates are ported, but the STUDY/pipeline tools and the remaining research workflow tools still use the Python server. This is a 34-tool prototype, not a complete replacement of all 45 Python tools.
