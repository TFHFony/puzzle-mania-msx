"""Simulate how music.mp4 would sound as a sample on the MSX PSG (YM2149 / AY-3-8910 volume DAC), 60 s excerpt per variant.
 1ch : one channel, the 16 volume steps (log, 3 dB per step)
 3ch : the three channels summed (every combination of the three volume registers), nearest level + first order noise shaping
The result is played back with zero-order hold (like the real hardware), written as 44.1 kHz WAV to Music/.
usage: psg_sim.py"""
import os, subprocess, bisect
import numpy as np
from scipy.io import wavfile
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
SRC = os.path.join(PROJ, 'PM.wav')
OUT = os.path.join(PROJ, 'Music'); os.makedirs(OUT, exist_ok=True)
START, LEN = 0.0, 173.15           # PM.wav has no silence at the ends
EXC0, EXCL = 50.0, 60.0            # excerpt that is simulated for listening


def decode(rate, t0, dur):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t0), '-t', str(dur), '-i', SRC, '-vn', '-ac', '1', '-ar', str(rate), '-f', 'f32le', '-'], capture_output=True, check=True)
    x = np.frombuffer(r.stdout, np.float32).astype(np.float64)
    return x / max(1e-9, np.abs(x).max()) * 0.97


YM = np.array([0.0] + [10 ** (-(15 - v) * 3 / 20) for v in range(1, 16)])          # YM2149: 3 dB per step, 0 = off
levels1 = YM / YM.max()
sums = {}
for a in range(16):
    for b in range(a, 16):
        for c in range(b, 16):
            s = YM[a] + YM[b] + YM[c]
            sums.setdefault(round(s, 5), (a, b, c))
levels3_all = np.array(sorted(sums)) / 3.0
grid = np.linspace(0, 1, 256)       # one byte per sample: about 170 usable, evenly spread levels
levels3 = np.unique(levels3_all[np.abs(levels3_all[None, :] - grid[:, None]).argmin(1)])
print('3 channels: %d different levels, %d used as one-byte samples (1 channel: 16)' % (len(levels3_all), len(levels3)))


def quantise(x, levels):
    """x in -1..1 -> nearest PSG level (0..1) with first order noise shaping; returns the played signal in -1..1"""
    lv = list(levels)
    out = np.empty_like(x); e = 0.0
    for i, v in enumerate(x):
        t = (v + 1) / 2 + e
        j = bisect.bisect_left(lv, t)
        if j == 0: q = lv[0]
        elif j == len(lv): q = lv[-1]
        else: q = lv[j] if lv[j] - t < t - lv[j - 1] else lv[j - 1]
        e = max(-0.3, min(0.3, t - q))
        out[i] = q * 2 - 1
    return out


def zoh(y, rate):
    n = int(len(y) / rate * 44100)
    return y[np.minimum((np.arange(n) * rate / 44100).astype(int), len(y) - 1)]


rows = []
for name, levels, rate in (('1ch_16kHz', levels1, 16000), ('1ch_8kHz', levels1, 8000), ('3ch_8kHz', levels3, 8000), ('3ch_11kHz', levels3, 11025), ('3ch_16kHz', levels3, 16000)):
    x = decode(rate, EXC0, EXCL)
    y = quantise(x, levels)
    snr = 10 * np.log10((x ** 2).sum() / ((x - y) ** 2).sum())
    wavfile.write(os.path.join(OUT, 'pm_psg_%s.wav' % name), 44100, (np.clip(zoh(y, rate), -1, 1) * 32000).astype(np.int16))
    rows.append((name, rate, snr))
    print(name, 'SNR %.1f dB' % snr, flush=True)
ref = decode(44100, EXC0, EXCL)
wavfile.write(os.path.join(OUT, 'pm_original_excerpt.wav'), 44100, (ref * 32000).astype(np.int16))
print('done')
