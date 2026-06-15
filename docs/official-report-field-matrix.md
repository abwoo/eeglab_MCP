# Official Report Field Matrix

Every reproducible EEG report should be written as a derivative record, not as a loose narrative. This field matrix is aligned with EEGLAB provenance, BIDS-style metadata, and COBIDAS-style reporting expectations.

## Recording And Acquisition

- input path and source format
- set name, file name, and file path
- sampling rate, duration, points, trials, and data shape
- channel count, labels, channel-location coverage, reference, and montage
- hardware, amplifier, cap, acquisition filters, impedance, and power-line frequency when available
- importer plugin/function, original source format, sidecars/header notes, and whether raw files were preserved

## Events And Design

- event labels, counts, latency range, and `urevent` link status
- event roles: condition, trigger, boundary, impedance/QC, segment marker, excluded, or candidate trigger
- source of event semantics: events.json, HED tags, behavioral log, lab codebook, or user confirmation
- HED schema/version or event-codebook version when HED/event annotation is used
- scripted event modification rules, latency units, and urevent preservation/relinking status
- condition definitions, trial counts after rejection, epoch window, and baseline window

## Preprocessing Parameters

- raw preservation and derivative output policy
- filter cutoffs, order/transition if known, and resampling target
- line-noise frequency, method, and plugin status
- bad-channel policy, interpolation policy, ASR thresholds, and epoch rejection criteria
- rereference choice plus rank/reference implications
- ICA algorithm, PCA/rank decisions, ICLabel thresholds, component review, removed components

## Analysis Parameters

- ERP channels/ROIs, time windows, baseline and condition contrasts
- spectral frequency range, band definitions, channels/ROIs, artifact policy
- ERSP/ITC frequency range, cycles/wavelets, baseline, output measures
- connectivity method, channel/ROI selection, model assumptions, validation limits
- source head model/template, channel coordinate assumptions, component list, residual variance
- STUDY design variables, levels, precomputed measure family, precompute parameters, alpha, correction, contrasts, and multiple-comparison policy
- ICA clustering features, clustering algorithm/count, distance metric, outlier policy, and cluster review criteria
- LIMO/SIFT/AMICA/NSG model, compute strategy, validation, remote-job provenance, and guidance-only limits when used
- external export format, exporter plugin/function, and metadata mapping assumptions when export guidance is used

## Outputs And Limits

- output paths for datasets, tables, figures, and protocols
- BIDS export directory, derivative dataset status, sidecar completeness, event metadata source, and software/plugin provenance
- external export directory, export format support, exporter plugin status, and validation limitations
- software versions, EEGLAB path, plugin availability, and missing plugins
- official method profile ID, gate status, source claim IDs, missing requirements
- override status, override reason, and blocked requirements acknowledged
- failed steps, recovery choices, and unresolved limitations
- explicit exclusions: no clinical diagnosis, no anatomical certainty from missing montage/model, no automatic deletion based only on ICLabel probabilities
