"""Music for the PSG sample player: 8 kHz, 3 channels summed (one byte per sample = index into a table of PSG volume triples).
 menu track  = PM-Menu.mp3  (loops, cut to whole 16 KB banks with a short fade-out)
 puzzle track = PM.wav       (loops, padded with silence to whole banks)
levels(): the ~170 usable levels and the volume triples of the three channels; track(): quantised sample bytes (cached in work/)."""
import os, subprocess, bisect
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
RATE = 8000
BANK = 16384
YM = np.array([0.0] + [10 ** (-(15 - v) * 3 / 20) for v in range(1, 16)])           # YM2149: 3 dB per step, 0 = off
AY = np.array([0, 0.0100, 0.0145, 0.0211, 0.0307, 0.0455, 0.0644, 0.1073, 0.1266, 0.2050, 0.2922, 0.3728, 0.4986, 0.6353, 0.8056, 1.0])   # AY-3-8910 (as modelled by MAME / openMSX)
SCALE = float(os.environ.get('PSG_SCALE', '0'))     # 0 = all three channels at full volume are the top level; else the top level is this sum of the three channel DACs (1.328 = the MAP player of marmsx's article)
CURVE = os.environ.get('PSG_CURVE', 'ym')          # ay | ym | joint (compromise that stays within about 5 % on both chips)


def levels(curve=None):
    """-> (levels 0..1 sorted, triples of channel volumes) : at most 256 entries, one per sample byte value"""
    curve = curve or CURVE
    tr = [(a, b, c) for a in range(16) for b in range(a, 16) for c in range(b, 16)]
    LA = np.array([(AY[a] + AY[b] + AY[c]) / 3 / AY.max() for a, b, c in tr])
    LY = np.array([(YM[a] + YM[b] + YM[c]) / 3 / YM.max() for a, b, c in tr])
    grid = np.linspace(0, 1, 256)
    if curve == 'joint':
        idx = [int(np.maximum(abs(LA - t), abs(LY - t)).argmin()) for t in grid]
        return grid, [tr[i] for i in idx]
    L = LA if curve == 'ay' else LY
    order = np.argsort(L, kind='stable')
    seen, vals, trips = set(), [], []
    for i in order:
        k = round(float(L[i]), 5)
        if k not in seen:
            seen.add(k); vals.append(float(L[i])); trips.append(tr[i])
    vals = np.array(vals)
    if SCALE:                                       # only the dense lower part of the level distribution: up to 256 unique levels
        keep = vals <= SCALE / 3 / (YM.max() if curve != 'ay' else AY.max()) + 1e-9
        vals = vals[keep]; trips = [t for t, k in zip(trips, keep) if k]
        vals = vals / vals[-1]
    sel = sorted(set(int(np.abs(vals - t).argmin()) for t in grid))             # about 170 evenly spread levels
    return vals[sel], [trips[i] for i in sel]


def decode(path, seconds=None, fade=0.0, rate=None):
    af = 'acompressor=threshold=0.12:ratio=3:attack=5:release=120:makeup=2,alimiter=limit=0.97'
    if seconds and fade:
        af += ',afade=t=out:st=%.3f:d=%.3f' % (seconds - fade, fade)
    cmd = ['ffmpeg', '-v', 'error', '-i', path, '-vn', '-ac', '1', '-ar', str(rate or RATE)]
    if seconds:
        cmd += ['-t', '%.4f' % seconds]
    r = subprocess.run(cmd + ['-af', af, '-f', 'f32le', '-'], capture_output=True, check=True)
    x = np.frombuffer(r.stdout, np.float32).astype(np.float64)
    return x / max(1e-9, np.abs(x).max()) * 0.97


def gapshape(x, gapk, fl=160):
    """the player plays fl-gapk samples of every frame and holds the last one over the rest: make that one the mean of the frame's tail"""
    if not gapk: return x
    x = x.copy(); n = fl - gapk
    for s in range(0, len(x) - fl + 1, fl):
        x[s + n - 1] = x[s + n - 1:s + fl].mean()
    return x


def quantise(x, lv):
    """x -1..1 -> index into lv with first order noise shaping"""
    lvl = list(lv); n = len(lvl)
    out = np.empty(len(x), np.uint8); e = 0.0
    for i, v in enumerate(x):
        t = (v + 1) / 2 + e
        j = bisect.bisect_left(lvl, t)
        if j == 0: k = 0
        elif j == n: k = n - 1
        else: k = j if lvl[j] - t < t - lvl[j - 1] else j - 1
        e = max(-0.3, min(0.3, t - lvl[k]))
        out[i] = k
    return out


def track(name, path, banks=None, fade=0.8, gapk=0):
    """-> bytes, a whole number of banks.  banks=None: pad with silence to the next whole bank; banks=n: cut to n banks with a fade-out"""
    lv, _ = levels()
    cache = os.path.join(PROJ, 'work', 'music_%s_%s_%s_%s_%s.npy' % (name, banks, CURVE, SCALE, gapk))
    if os.path.exists(cache) and os.path.getmtime(cache) > os.path.getmtime(path):
        return np.load(cache).tobytes()
    silence = int(np.abs(lv - 0.5).argmin())
    if banks:
        x = decode(path, banks * BANK / RATE, fade)
    else:
        x = decode(path)
    q = quantise(gapshape(x, gapk), lv)
    if banks:
        q = q[:banks * BANK]
    nb = -(-len(q) // BANK)
    q = np.concatenate([q, np.full(nb * BANK - len(q), silence, np.uint8)])
    np.save(cache, q)
    return q.tobytes()


RATE16 = 16000                                  # the SCC player: two samples per iteration, 16 kHz, 8 bit linear, signed bytes (silence = 0)


def track16(name, path, banks=None, fade=0.8, gapk=0):
    """the music for the SCC player (game/scc16): 16 kHz, 256 linear levels (signed bytes), the gap of gapk iterations = 2 * gapk samples.
    -> bytes, a whole number of banks.  banks=n: cut to n banks with a fade-out (the same duration as the 8 kHz track of n / 2 banks)"""
    cache = os.path.join(PROJ, 'work', 'music16_%s_%s_%s_v1.npy' % (name, banks, gapk))
    if os.path.exists(cache) and os.path.getmtime(cache) > max(os.path.getmtime(path), os.path.getmtime(__file__)):
        return np.load(cache).tobytes()
    lv = np.linspace(0, 1, 256)
    if banks:
        x = decode(path, banks * BANK / RATE16, fade, RATE16)
    else:
        x = decode(path, rate=RATE16)
    q = quantise(gapshape(x, 2 * gapk, 320), lv)
    if banks:
        q = q[:banks * BANK]
    nb = -(-len(q) // BANK)
    q = np.concatenate([q, np.full(nb * BANK - len(q), 128, np.uint8)])
    q = (q ^ 0x80).astype(np.uint8)                       # index 0..255 -> signed byte (index 128 = silence = 0)
    np.save(cache, q)
    return q.tobytes()


def fade_sets(curve=None, steps=(1.0, 0.75, 0.5, 0.25, 0.0)):
    """table sets for the gain steps of the fades: for every sample value the volume triple whose level is nearest to the scaled level"""
    lv, trip = levels(curve)
    lv = np.asarray(lv)
    sets = []
    for g in steps:
        t = []
        for L in lv:
            target = 0.5 + (L - 0.5) * g
            t.append(trip[int(np.abs(lv - target).argmin())])
        t += [t[-1]] * (256 - len(t))
        sets.append(t)
    return sets


def array_track(name, x, banks, curve=None):
    """quantise a float signal (-1..1, 8 kHz) to sample bytes, padded with silence to `banks` banks"""
    lv, _ = levels(curve)
    silence = int(np.abs(np.asarray(lv) - 0.5).argmin())
    q = quantise(x, lv)[:banks * BANK]
    q = np.concatenate([q, np.full(banks * BANK - len(q), silence, np.uint8)])
    return q.tobytes()
