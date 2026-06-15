# Official EEGLAB Support Matrix

This matrix is the decision surface for MCP support. A topic is "covered" when it has a support level, official claim IDs where applicable, a resource route, and either executable tools or guidance-only wording.

| Support level | Meaning | Allowed MCP behavior | Required report language |
| --- | --- | --- | --- |
| `executable` | A local MCP tool can run the EEGLAB-family operation. | Run only after schema validation, official preflight, and output-path policy. | Include tool name, function family, parameters, gate status, output paths, and limitations. |
| `gated_guidance` | The MCP can guide the method and may expose a partial tool, but interpretation depends on prerequisites. | Run only when method-specific critical gates pass, or return `official_gate_blocked`. | Include missing prerequisites, source claim IDs, and whether results are exploratory. |
| `indexed_only` | The official topic/plugin is known but no dedicated execution workflow is promised. | Use `eeglab_project_plan`, `eeglab_plugin_check`, or `eeglab_method_preflight`; do not execute unsupported plugin logic. | Say guidance-only/indexed-only and list what must be installed or designed before support can be claimed. |
| `out_of_scope` | Relevant to EEG research but outside local EEGLAB MCP execution. | Audit or ask for metadata; do not claim acquisition, clinical, or hardware-control capability. | Record missing acquisition/lab-notebook fields as limitations. |

## Executable Families

- Data and provenance: `eeglab_load_data`, `eeglab_info`, `eeglab_get_events`, `eeglab_history`, `eeglab_qc_report`.
- Core preprocessing: filter, resample, rereference, select channels, edit channels, interpolate channels, clean line noise, clean_rawdata/ASR.
- ICA and components: run ICA, classify/flag/remove components after official gates.
- ERP and time/frequency outputs: epoch, ERP summary, spectral summary, ERSP/ITC, plots.
- Source and STUDY tools: executable only when their official gates pass.

## Guidance-Only or Indexed Families

- BIDS export, plugin-dependent import/export formats, HEDTools event annotation, history-derived batch scripting, scripted event modification, STUDY precompute, STUDY ICA clustering, LIMO, SIFT, groupSIFT, NFT, NSGportal, AMICA, Zapline-Plus, and other advanced plugins are indexed through the plugin matrix and method map.
- The MCP may check functions and write a plan, but it must not claim analysis support unless an explicit tool/workflow and eval coverage exist.
- BIDS/HED sidecars are treated as provenance evidence. Missing sidecars block condition-level event semantics unless a validated lab codebook exists.

## Synchronization Rule

For every `executable` or `gated_guidance` topic, the implementation must keep these in sync:

- official claim ID
- method profile or documented reason no profile exists
- tool registry or guidance-only route
- MCP resource
- skill guidance
- eval coverage
