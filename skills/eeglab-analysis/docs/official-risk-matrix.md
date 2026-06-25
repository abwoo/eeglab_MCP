# Official Method Risk Matrix

This matrix explains how method gates are applied. It is intentionally conservative: missing scientific prerequisites block high-risk execution even when MATLAB could technically run a command.

| Method profile | Risk | Blocking conditions | Recovery |
| --- | --- | --- | --- |
| `epoch` | High | no confirmed condition events; only boundary/impedance/excluded/segment markers | run event semantics audit; provide event-code map or behavioral log |
| `timefreq` | High | unconfirmed event locking; missing baseline; missing frequency/cycle settings | confirm triggers and report baseline/frequency settings |
| `derivative_processing` | High | raw input not preserved; no derivative output plan; parameters absent | choose output path and record cutoffs/reference/rejection parameters |
| `line_noise` | High | no 50/60 Hz frequency or method parameters; no derivative output | confirm local mains frequency and plugin/method path |
| `clean_rawdata` | High | epoched-only data; clean_rawdata unavailable; thresholds absent; no derivative output | use continuous raw data, plugin check, thresholds, output path |
| `run_ica` | High | unsuitable data shape; rank/reference not reviewed; bad-channel policy missing | inspect data, define rank/reference and bad-channel policy |
| `iclabel` | High | no ICA weights; ICLabel unavailable | compute ICA after gates; install/check ICLabel |
| `remove_components` | High | no ICA weights; no component review; no derivative output | review components and record thresholds/rationale |
| `channel_locations` | High for interpretation | no usable channel coordinates or repair/interpolation plan | load montage, rename channels, or provide interpolation reference |
| `topography` | High for interpretation | no channel locations; no plotted time/frequency selection | repair montage and record plotting window |
| `spectral` | Medium/high | no frequency range; no artifact policy | record frequency range, channels/ROIs, and cleaning/rejection policy |
| `connectivity` | Medium/high | no frequency range/method; artifact policy missing; model limits absent | record method, frequency, channels, and sensor/source interpretation limits |
| `source` | High | no ICA/source model; no channel locations; DIPFIT unavailable; head model undefined | satisfy ICA/montage/DIPFIT/model gates or report exploratory override |
| `bids_import` | High | no BIDS root/sidecars; EEG-BIDS import support unavailable | verify BIDS path, sidecars, event timing, and plugin availability |
| `bids_export` | Guidance-only | EEG-BIDS export unavailable; sidecars/event descriptions incomplete; derivative output/provenance missing | keep to planning/reporting until export tool support and BIDS metadata are complete |
| `import_plugins` | Guidance-only/import-readiness | source format unknown; importer plugin unavailable; event/channel mapping missing; raw files not preserved | run plugin check, record source format and mapping policy, preserve originals |
| `data_export` | Guidance-only except `.set` save | target format unsupported; metadata incomplete; derivative output/provenance missing | use `.set` save or add a dedicated exporter workflow with validation |
| `hed_event_annotation` | Guidance-only/event metadata | event descriptions or HED schema/version missing; condition-code map unvalidated | add HED/events.json/codebook records before event-locked claims |
| `history_scripting` | Guidance-only/protocol recovery | EEG.history absent; history-derived script not reviewed; hidden defaults or output policy unclear | inspect history, parameterize script, record outputs and limitations |
| `event_script_modification` | Guidance-only | recode/deletion/latency rule missing; latency units missing; urevent links not preserved or relinked | document event rules, units, urevent policy, and semantic evidence before changes support analysis |
| `study_create` | High | no BIDS/multi-subject structure | organize subject/session datasets; lock protocol before statistics-ready claims |
| `study_design` | High | no BIDS/multi-subject structure; design variables missing | define subject/session/design variables and levels |
| `study_precompute` | Guidance-only | protocol not locked; measure family/parameters absent; derivative precompute output missing | define design, lock single-subject protocol, record measure precompute settings |
| `study_statistics` | High | no BIDS/multi-subject structure; single-subject protocol not locked; design variables, measure, or alpha/correction missing | lock protocol, define design/measure, and record correction policy |
| `ica_clustering` | Guidance-only | subject ICA missing; clustering features/algorithm/outlier policy absent; review criteria missing | compute ICA after gates, define features and cluster review protocol |
| `study` | High | combined ready-check fails for BIDS/STUDY/group analysis | use staged `bids_import`, `study_create`, `study_design`, and `study_statistics` gates |
| `limo_statistics` | Guidance-only | LIMO unavailable; statistical design/correction undefined | keep to planning until plugin, model, contrasts, and correction are documented |
| `amica_ica` | Guidance-only | AMICA unavailable; rank/PCA/reference or compute strategy missing; derivative output absent | keep to planning or use supported runica/Picard path after ICA gates |
| `sift_connectivity` | Guidance-only | SIFT unavailable; model validation/stationarity/correction missing | keep to planning until MVAR/source workflow and validation are documented |
| `nsg_remote` | Out-of-local-scope/guidance-only | NSG unavailable; remote upload/credential approval or job provenance missing | keep local-first; add secure dedicated integration before remote execution |
| `pipeline` | High | raw not preserved; derivative output missing; user has not accepted bundled defaults | use explicit low-level tools or record accepted defaults and output policy |

Hard-blocked gates return `official_gate_blocked`. Overrides require a user-approved `override_reason` and must record blocked requirements, source claim IDs, and scientific limitations.
