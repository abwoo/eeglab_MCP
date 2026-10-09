# EEGLAB MCP for MATLAB

EEGLAB research tools and an MCP Streamable HTTP server implemented in MATLAB. GitHub Actions runs the server inside its licensed MATLAB batch session. The tool manifest also uses MathWorks' documented [custom-tool format](https://github.com/matlab/matlab-mcp-server/blob/main/guides/custom-tools.md), with catalog compatibility checked against the [official MATLAB MCP Server](https://github.com/matlab/matlab-mcp-server).

All execution and validation run on GitHub Actions. There is no desktop installer, interpreter environment, or client configuration to install on your computer.

## Run In GitHub Cloud

Open **Actions → MATLAB cloud request → Run workflow**. Choose a tool and provide its arguments as a JSON object. The workflow provisions MATLAB and EEGLAB on a GitHub runner, starts the MATLAB MCP server, initializes the sample recording, executes the requested tool over MCP, and uploads the response and derivative outputs as an artifact.

For example:

- Tool: `eeglab_method_preflight`
- Arguments: `{"method":"epoch","context":{}}`

A blocked gate is a useful result: its response lists the missing requirements and source claims. For a sample ERP derivative, choose `eeglab_erp_light_workflow` with:

```json
{"data_path":"@sample","output_dir":"@artifacts","event_types":["square"],"channels":["Cz"],"method_context":{"confirmed_condition_events":true,"raw_input_preserved":true,"derivative_output_planned":true}}
```

`@sample` resolves to the EEGLAB sample dataset on the runner; `@artifacts` resolves to the job's output folder. Other data paths must already exist in the cloud session. No participant EEG files are committed to this repository. The server and MATLAB session stop when the job finishes; GitHub Actions does not provide a persistent MCP endpoint.

## Tools And Method Gates

The extension exposes **46 custom tools**: the original 45 EEGLAB and research workflow tools, plus `eeglab_official_claims`. The first-contact sequence is `eeglab_init`, `eeglab_load_data`, `eeglab_qc_report`, `eeglab_info`, `eeglab_get_events`, and `eeglab_history`.

Planning, event audit, plugin checks, method preflight, protocol export, light ERP, STUDY design/statistics, preprocessing, ICA, spectral/time-frequency analysis, connectivity, figures and source tools all execute as MATLAB functions in the same session. High-risk tools enforce official prerequisites and record explicit overrides. Bundled pipelines stop at the first failed child gate and write derivatives; ASR and ICA are opt-in and components are never removed automatically.

MathWorks custom tools accept scalar argument types. Tools with lists or nested options use one required string argument named `options`, containing a JSON object. The cloud workflow converts its arguments object into that string. Direct tools retain their documented scalar arguments. See [the MATLAB interface](matlab/README.md) and [the complete tool catalog](docs/tools.md).

The versioned source document retains **47 official claims and 39 method profiles**. Read it through `eeglab_official_claims`, or inspect [the claims document](generated/eeglab-official-claims.json). The official extension does not add custom prompt/resource URI handlers; research guidance is provided through the tools and repository documents.

## Cloud Validation

The required `CI / validate` check validates the tool manifest, all method profiles, MATLAB option/error paths, every processing batch, research workflows, real STUDY ERP statistics, MCP protocol/error handling and real ERP artifacts through native MATLAB MCP HTTP calls. Linux, Windows and macOS jobs also verify catalog compatibility over the official MathWorks MCP transport. MATLAB R2024b, Signal Processing Toolbox and Statistics and Machine Learning Toolbox are provisioned on GitHub runners. MathWorks v0.14.0 downloads are pinned and checked against official SHA-256 digests.

## Repository Map

| Path | Purpose |
| --- | --- |
| `matlab/` | MATLAB tools, method gates, official extension and tests. |
| `generated/` | Versioned claims, plugin metadata and report-field definitions. |
| `.github/workflows/` | Cloud validation and on-demand MCP requests. |
| `scripts/` | Dependency-free JSON-RPC/cloud verification helpers; no analysis logic. |
| `docs/` | Official method, plugin, risk and reporting guidance. |
| `skills/eeglab-analysis/` | Optional research guidance; installation is not required. |

Scientific outputs depend on recording quality, validated event meanings, channel metadata and available EEGLAB plugins. Advanced plugins remain indexed guidance until an execution tool supports them. EEG signal processing is not a clinical diagnosis.

## Repository Maintenance

Licensed under [Apache-2.0](LICENSE). See [SECURITY.md](SECURITY.md) for vulnerability reporting. CODEOWNERS, weekly GitHub Actions dependency updates and a pinned Scorecard workflow are included.
