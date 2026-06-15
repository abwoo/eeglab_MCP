# MCP Client Config Templates

These templates register the local EEGLAB MCP server as `eeglab`. They are for manual setup or for clients not covered by `scripts\setup_eeglab_agent.ps1`.

## Files

- `codex.config.toml`: block for `C:\Users\<USER>\.codex\config.toml`.
- `claude_desktop_config.json`: merge into Claude Desktop MCP config.
- `cursor.mcp.json`: Cursor MCP config template.
- `vscode.mcp.json`: VS Code MCP config template.
- `openclaw.mcp.json`: generic OpenClaw/OpenClaude-style MCP JSON template.

## Values To Adjust

- `args`: absolute path to `eeglab_mcp_server\server.py`.
- `EEGLAB_PATH`: local EEGLAB installation directory.
- `MATLAB_ROOT`: local MATLAB root.
- `MATLAB_EXEC`: `matlab` or an absolute path to `matlab.exe`.
- `EEGLAB_WORK_DIR`: dedicated EEGLAB MCP work directory.
- `MATLAB_TIMEOUT`: per-call timeout in seconds.

## MATLAB MCP Pairing

This server can coexist with a separate general MATLAB MCP registered as `matlab`. Do not rename this server to `matlab`; the skill and prompts rely on `eeglab` for EEG/EEGLAB workflows and `matlab` for generic MATLAB scripts.

Treat the two MCP servers as workspace-isolated sessions. Pass data between them by explicit file handoff rather than shared MATLAB variables.

## Skill

For clients that support skills, install `skills/eeglab-analysis/`. Clients without skills can still use the MCP prompts/resources exposed by the server.

## Verify Template Changes

After editing any template, run the unified verifier from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 verify
```

Then run the doctor for the client environment you actually use:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\eeglab_agent.ps1 doctor
```
