function [ersp, itc, times, freqs, used_freqs] = eegmcp_b3_newtimef(dataset, chan, freq_range, cycles, baseline)
%EEGMCP_B3_NEWTIMEF ERSP (dB) and ITC (absolute) of one channel of an epoched dataset.
%   Runs newtimef with Morlet wavelets and plotting off. CYCLES is
%   [start end] (or [start step end], whose step is not used by newtimef).
%   BASELINE is [start end] in ms, or [] for newtimef's default (all
%   pre-stimulus times). The upper frequency is clipped to the Nyquist
%   frequency; USED_FREQS is the range actually requested.

if numel(cycles) == 3
    cycles = cycles([1 3]);
end
used_freqs = [freq_range(1), min(freq_range(2), dataset.srate / 2)];
args = {'freqs', used_freqs, 'plotersp', 'off', 'plotitc', 'off', 'plotphase', 'off', 'verbose', 'off'};
if ~isempty(baseline)
    args = [args, {'baseline', baseline}];
end
data = double(dataset.data(chan, :, :));
ersp = [];
itc = [];
times = [];
freqs = [];
evalc(['[ersp, itc, ~, times, freqs] = newtimef(data, dataset.pnts, ' ...
    '[dataset.xmin dataset.xmax] * 1000, dataset.srate, cycles, args{:});']);
itc = abs(itc);
times = times(:)';
freqs = freqs(:)';
end
