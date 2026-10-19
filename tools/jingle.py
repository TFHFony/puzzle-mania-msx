"""The solve jingle: a short chiptune fanfare, 8 kHz, exactly 32 KB (2 banks) of samples.  make() -> float array (-1..1)."""
import numpy as np
RATE = 8000
N = 32768                      # 2 banks


def osc(freq, t, kind):
    """band limited square / triangle (harmonics below 3.8 kHz)"""
    out = np.zeros_like(t)
    k = 1
    while freq * k < 3800:
        if kind == 'sq':
            out += np.sin(2 * np.pi * freq * k * t) / k
        else:
            out += (-1) ** ((k - 1) // 2) * np.sin(2 * np.pi * freq * k * t) / (k * k)
        k += 2
    return out


def note(x, start, dur, freq, vol, kind='sq', vib=0.0):
    i0 = int(start * RATE); n = int(dur * RATE)
    if i0 >= N:
        return
    n = min(n, N - i0)
    t = np.arange(n) / RATE
    f = freq * (1 + vib * np.sin(2 * np.pi * 5.5 * t))
    ph = np.cumsum(f) / RATE
    wave = np.zeros(n)
    k = 1
    while freq * k < 3800:
        if kind == 'sq':
            wave += np.sin(2 * np.pi * ph * k) / k
        else:
            wave += (-1) ** ((k - 1) // 2) * np.sin(2 * np.pi * ph * k) / (k * k)
        k += 2
    a = int(0.006 * RATE); r = int(0.06 * RATE)
    env = np.ones(n) * np.exp(-t * 1.2)
    env[:a] *= np.linspace(0, 1, a)
    env[-r:] *= np.linspace(1, 0, min(r, n))
    x[i0:i0 + n] += wave * env * vol


def make():
    b = 0.24                                    # one beat
    x = np.zeros(N)
    mel = [  # (beat, length, frequency)
        (0.0, .5, 523.25), (0.5, .5, 659.25), (1.0, .5, 783.99), (1.5, .5, 1046.5),
        (2.0, .5, 783.99), (2.5, .5, 1046.5), (3.0, .5, 1318.5), (3.5, 2.5, 1568.0),
        (6.0, .5, 698.46), (6.5, .5, 880.0), (7.0, .5, 1046.5),
        (7.5, .5, 783.99), (8.0, .5, 987.77), (8.5, .5, 1174.7),
        (9.0, 4.0, 1046.5),
    ]
    for s, l, f in mel:
        note(x, s * b, l * b * 0.96, f, 0.55, 'sq', vib=0.006 if l > 2 else 0.0)
    # second voice a third below, quieter
    for s, l, f in [(3.5, 2.5, 1318.5), (9.0, 4.0, 784.0), (2.0, 1.5, 659.25), (6.0, 1.5, 587.33), (7.5, 1.5, 659.25)]:
        note(x, s * b, l * b * 0.96, f, 0.28, 'sq')
    bass = [(2.0, 4.0, 130.81), (6.0, 1.5, 174.61), (7.5, 1.5, 196.0), (9.0, 4.5, 130.81), (0.0, 2.0, 130.81)]
    for s, l, f in bass:
        note(x, s * b, l * b, f, 0.5, 'tri')
    for s, f in [(11.2, 2093.0), (11.45, 2637.0), (11.7, 3136.0)]:        # sparkle on the last chord
        note(x, s * b, 0.5 * b, f, 0.22, 'sq')
    # echo
    d = int(0.19 * RATE)
    y = x.copy()
    for k in range(1, 4):
        y[k * d:] += x[:N - k * d] * (0.3 ** k)
    # fade out the last 0.6 s, silence at the end (the player repeats the last 256 samples)
    f = int(0.6 * RATE)
    end = N - 600
    y[end - f:end] *= np.linspace(1, 0, f)
    y[end:] = 0
    y /= max(1e-9, np.abs(y).max()) / 0.92
    return y


if __name__ == '__main__':
    import os, sys
    from scipy.io import wavfile
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Music', 'jingle.wav')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    y = make()
    wavfile.write(out, RATE, (y * 30000).astype(np.int16))
    print('written', out, len(y) / RATE, 's')
