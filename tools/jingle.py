"""The FONY jingle for the jingle player (game/sndplay.asm): a constant sample clock of SND_T cycles per sample, no frames, no gaps, no silence in front.
 PSG: 2 banks (32 KB), 3 channels summed, one byte per sample = an index into the volume tables (the same levels as tools/music.py), 17.2 kHz at SND_T = 208
 SCC: 4 banks (64 KB), signed 8 bit, 34.4 kHz at SND_TS = 104
The source is assets/fony_jingle_win.wav (the FM-PAC recording of the disk jingle, 44.1 kHz, 1.9 s); T0 = the seconds that are cut off in front.
usage: python jingle.py [T] [TS]   -> prints the sizes (the tracks are cached in work/)"""
import os, re, sys
import numpy as np
import music
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
CPU = 3579545
WAV = os.path.join(PROJ, 'assets', 'fony_jingle_win.wav')
T0 = 0.03                                       # (the recording starts with 37 ms of silence)
PSG_BANKS, SCC_BANKS = 2, 4
FILM = r'F:\MSX Projects\Dev27\FONY.mp4'
BOOM_T0 = 5.95                                  # s: the dreun of the film (the sound jumps to full at 6.0 s) up to its end: the XXXL screen plays it (the end of the sound of FONY.mp4)


def cycles():
    """-> (SND_T, SND_TS) from game/sndcfg.inc"""
    d = dict(re.findall(r'(\w+) equ (\d+)', open(os.path.join(PROJ, 'game', 'sndcfg.inc')).read()))
    return int(d['SND_T']), int(d['SND_TS'])


def _cut(path, rate, banks):
    x = music.decode(path, rate=rate)[int(T0 * rate):]
    n = banks * music.BANK
    assert len(x) <= n, 'the jingle is %d samples at %d Hz: %d banks hold %d' % (len(x), rate, banks, n)
    return x


def psg(t=None):
    """-> bytes, PSG_BANKS banks"""
    t = t or cycles()[0]
    rate = round(CPU / t)
    cache = os.path.join(PROJ, 'work', 'jingle_psg_%d_%s_%s.npy' % (t, music.CURVE, music.SCALE))
    if os.path.exists(cache) and os.path.getmtime(cache) > max(os.path.getmtime(WAV), os.path.getmtime(music.__file__), os.path.getmtime(__file__)):
        return np.load(cache).tobytes()
    lv, _ = music.levels()
    silence = int(np.abs(lv - 0.5).argmin())
    q = music.quantise(_cut(WAV, rate, PSG_BANKS), lv)
    q = np.concatenate([q, np.full(PSG_BANKS * music.BANK - len(q), silence, np.uint8)])
    np.save(cache, q)
    return q.tobytes()


def scc(ts=None):
    """-> bytes, SCC_BANKS banks"""
    ts = ts or cycles()[1]
    rate = round(CPU / ts)
    cache = os.path.join(PROJ, 'work', 'jingle_scc_%d.npy' % ts)
    if os.path.exists(cache) and os.path.getmtime(cache) > max(os.path.getmtime(WAV), os.path.getmtime(music.__file__), os.path.getmtime(__file__)):
        return np.load(cache).tobytes()
    q = music.quantise(_cut(WAV, rate, SCC_BANKS), np.linspace(0, 1, 256))
    q = np.concatenate([q, np.full(SCC_BANKS * music.BANK - len(q), 128, np.uint8)])
    q = (q ^ 0x80).astype(np.uint8)             # index 0..255 -> signed byte (index 128 = silence = 0)
    np.save(cache, q)
    return q.tobytes()


if __name__ == '__main__':
    t, ts = cycles()
    if len(sys.argv) > 1: t = int(sys.argv[1])
    if len(sys.argv) > 2: ts = int(sys.argv[2])
    p, s = psg(t), scc(ts)
    print('PSG', t, 'cycles =', round(CPU / t), 'Hz,', len(p), 'bytes;  SCC', ts, 'cycles =', round(CPU / ts), 'Hz,', len(s), 'bytes')
    for name, d, ref in (('psg', p, None), ('scc', s, None)):
        print(name, 'first/last 8:', list(d[:8]), list(d[-8:]))


def boom(scc_mode, t=None):
    """the dreun of the film from BOOM_T0 to its end for the jingle player (bit 7 of C): original pitch, same sample clocks as the jingle -> bytes, a whole number of banks"""
    ts = cycles()[1] if scc_mode else cycles()[0]
    rate = round(CPU / ts)
    cache = os.path.join(PROJ, 'work', 'boom_%s_%d_%s.npy' % ('scc' if scc_mode else 'psg', ts, BOOM_T0))
    if os.path.exists(cache) and os.path.getmtime(cache) > max(os.path.getmtime(FILM), os.path.getmtime(music.__file__), os.path.getmtime(__file__)):
        return np.load(cache).tobytes()
    tmp = os.path.join(PROJ, 'work', 'boom_src.wav')
    import subprocess
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '%.3f' % BOOM_T0, '-i', FILM, '-vn', '-ac', '1', '-ar', '44100', tmp], check=True)
    x = music.decode(tmp, rate=rate)
    if scc_mode:
        q = music.quantise(x, np.linspace(0, 1, 256)); fill = 128
    else:
        lv, _ = music.levels(); q = music.quantise(x, lv); fill = int(np.abs(lv - 0.5).argmin())
    nb = -(-len(q) // music.BANK)
    q = np.concatenate([q, np.full(nb * music.BANK - len(q), fill, np.uint8)])
    if scc_mode:
        q = (q ^ 0x80).astype(np.uint8)
    np.save(cache, q)
    return q.tobytes()
