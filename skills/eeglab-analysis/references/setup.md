# Cloud Execution

Use GitHub Actions → MATLAB cloud request. Select an `eeglab_*` tool and pass a JSON arguments object. Results and derivative files are returned as job artifacts. All MATLAB/EEGLAB provisioning occurs on the GitHub runner; no computer-side package, client registration or setup script is needed.

The workflow uses MathWorks MATLAB MCP Server v0.14.0 and the reviewed extension in `matlab/eeglab-mcp-tools.json`. Read the repository README and `matlab/README.md` for tool options and cloud placeholders.
