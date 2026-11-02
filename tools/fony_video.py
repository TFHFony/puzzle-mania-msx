"""The FONY intro film (F:\\MSX Projects\\Dev27\\FONY.mp4, 24 fps, 10 s) for the players of tools/gen_fony.py (PSG) and tools/gen_fony16.py (SCC).
A window of 128 x 72 pixels (16 x 9 characters) in the SCREEN 2 picture: the cells (8 pattern + 8 colour bytes) are coded with the encoder of the game (tools/build_game.py coded),
MSX1 for the TMS9918A palette, MSX2 for one palette of 16 colours for the whole film (tools/fony_palette.json: tools/palette_opt.py on a mosaic of frames).
One frame = 320 iterations of 446 cycles (25.08 fps, PAL and NTSC alike); the sound is time-compressed (pitch kept) to the length of the picture:
  PSG: 8026 Hz, one byte per iteration (index into the volume tables of the player, 3 channels summed), 2624 bytes per frame, 6 frames per bank
  SCC: 16052 Hz, two signed bytes per iteration, 2944 bytes per frame, 5 frames per bank
  build(msx2, scc, nframes) -> dict(p1, p2, s1, s2: lists of 16 KB banks, tab: asm text of the frame tables, pal: 32 bytes V9938, n: frames)
usage: python fony_video.py [nframes]   (encodes / caches, prints the sizes)"""
import os, sys, json, pickle, subprocess
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, r'F:\MSX Projects\Dev27\msx1-video-player\tools')
SRC = r'F:\MSX Projects\Dev27\FONY.mp4'
WW, WH = 128, 72
WX, WY = 64, 56                                  # the window: characters 8..23 x 7..15
CX0, CY0, CW, CH = WX // 8, WY // 8, WW // 8, WH // 8
SAT, GAMMA = 1.25, 0.85                          # the look (see .claude/fony-intro-tools/fony_preview.py)
ITER = 320                                       # iterations per frame
PERIOD = 446
CPU = 3579545
RATE_PSG = int(round(CPU / PERIOD))              # 8026 Hz
RATE_SCC = 2 * RATE_PSG                          # 16052 Hz
FPS = CPU / (PERIOD * ITER)                      # 25.08
PSG_BYTES = ITER + CW * CH * 16                  # 2624
SCC_BYTES = 2 * ITER + CW * CH * 16              # 2944
PALJ = os.path.join(HERE, 'fony_palette.json')
CACHE = os.path.join(PROJ, 'work', 'fony_coded.pkl')


def frames():
    cmd = ['ffmpeg', '-v', 'error', '-i', SRC, '-vf', 'scale=%d:%d:flags=lanczos' % (WW, WH), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.uint8).reshape(-1, WH, WW, 3)


def grade(fr, lo, hi):
    from PIL import ImageEnhance
    a = np.clip((fr.astype(np.float32) - lo) / (hi - lo), 0, 1)
    im = ImageEnhance.Color(Image.fromarray((a * 255 + 0.5).astype(np.uint8))).enhance(SAT)
    return (np.clip(np.asarray(im).astype(np.float32) / 255, 0, 1) ** GAMMA * 255 + 0.5).astype(np.uint8)


def graded():
    fr = frames()
    lum = fr[::3].astype(np.float32).mean(-1)
    lo, hi = float(np.percentile(lum, 1)), float(np.percentile(lum, 99.5))
    return np.stack([grade(f, lo, hi) for f in fr])


def optimise_palette(gr):
    """one 16 colour palette (colours 0 and 1 stay black) for the whole film: k-means on a mosaic of frames, then the coordinate search of tools/palette_opt.py"""
    import palette_opt as PO
    sel = gr[np.linspace(0, len(gr) - 1, 12).astype(int)]
    mos = np.concatenate([np.concatenate(list(sel[r * 4:(r + 1) * 4]), axis=1) for r in range(3)], axis=0)
    pal = PO.TMS.copy()
    pal[2:] = PO.kmeans_pal(mos, 14)
    pal[0] = pal[1] = (0, 0, 0)                      # (colour 1 is the black of the game: the screen and the cells around the window are filled with it)
    pal = PO.refine(PO.half(mos), pal, list(range(2, 16)), 4, lambda t: print('  half', t, flush=True))
    pal, best = PO.refine(mos, pal, list(range(2, 16)), 1, lambda t: print('  full', t, flush=True), want_score=True)
    return pal


def _enc(args):
    import build_game as B
    win, pal = args
    img = np.zeros((192, 256, 3), np.uint8)
    img[WY:WY + WH, WX:WX + WW] = win
    fix = np.ones((192, 256), np.int8)
    fix[WY:WY + WH, WX:WX + WW] = 0
    return bytes(B.coded(img, fix, pal)[0])


def coded():
    """-> (palette (16 x 3), [MSX1 frame data], [MSX2 frame data]) of all frames (12288 bytes each: 6144 pattern + 6144 colour, cell order); cached"""
    key = (os.path.getmtime(__file__), os.path.getmtime(SRC), os.path.getmtime(PALJ) if os.path.exists(PALJ) else 0, os.path.getmtime(os.path.join(HERE, 'stills.py')))
    if os.path.exists(CACHE):
        k, res = pickle.load(open(CACHE, 'rb'))
        if k == key:
            return res
    from concurrent.futures import ProcessPoolExecutor
    gr = graded()
    if os.path.exists(PALJ):
        pal = np.array(json.load(open(PALJ)), np.float32)
    else:
        pal = optimise_palette(gr)
        json.dump(pal.tolist(), open(PALJ, 'w'))
        key = key[:2] + (os.path.getmtime(PALJ),) + key[3:]
    with ProcessPoolExecutor(max_workers=8) as ex:                    # (8 processes, not os.cpu_count())
        d1 = list(ex.map(_enc, [(g, None) for g in gr], chunksize=2))
        d2 = list(ex.map(_enc, [(g, pal) for g in gr], chunksize=2))
    res = (pal, d1, d2)
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    pickle.dump((key, res), open(CACHE, 'wb'))
    return res


def window(data):
    """-> (pattern rows, colour rows): 9 rows of 128 bytes each"""
    pat, col = [], []
    for cy in range(CY0, CY0 + CH):
        a = (cy * 32 + CX0) * 8
        pat.append(data[a:a + CW * 8])
        col.append(data[6144 + a:6144 + a + CW * 8])
    return pat, col


def audio(n, rate, scc):
    """the sound of the film for n frames, time-compressed to the speed of the picture (pitch kept): PSG volume indexes or SCC signed bytes"""
    import music
    tmp = os.path.join(PROJ, 'work', 'fony_audio.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', SRC, '-vn', '-ac', '1', '-af', 'atempo=%.6f' % (FPS / 24), '-ar', '44100', tmp], check=True)
    x = music.decode(tmp, rate=rate)
    need = n * (2 * ITER if scc else ITER)
    x = np.concatenate([x[:need], np.zeros(max(0, need - len(x)))])
    if scc:
        q = music.quantise(x, np.linspace(0, 1, 256))
        return (q ^ 0x80).astype(np.uint8)
    lv, _ = music.levels()
    return music.quantise(x, lv)


def frame_psg(pat, col, s):
    """one frame of the PSG stream: the iterations in the order of the player (H1, H2, rows, P1..P3, PAD): a sample byte, and 8 video bytes in the iterations of the rows"""
    out = bytearray(); k = 0

    def smp():
        nonlocal k
        v = int(s[k]); k += 1
        return v
    out.append(smp()); out.append(smp())
    for r in range(CH):
        for rows in (pat, col):
            for i in range(CW):
                out.append(smp()); out += rows[r][i * 8:i * 8 + 8]
        out.append(smp())
    while k < ITER:
        out.append(smp())
    assert len(out) == PSG_BYTES, len(out)
    return bytes(out)


def frame_scc(pat, col, s):
    """one frame of the SCC stream: two sample bytes per iteration (H1, H2, rows: address iteration + 16 iterations, ..., P1..P3, PAD); the 8 video bytes follow the samples"""
    out = bytearray(); k = 0

    def smp2():
        nonlocal k
        out.append(int(s[k])); out.append(int(s[k + 1])); k += 2
    smp2(); smp2()
    for r in range(CH):
        for rows in (pat, col):
            smp2()                                                  # the address iteration
            for i in range(CW):
                smp2(); out += rows[r][i * 8:i * 8 + 8]
        smp2()
    while k < 2 * ITER:
        smp2()
    assert len(out) == SCC_BYTES, len(out)
    return bytes(out)


def pack(frs, per_bank):
    banks, tab = [], []
    size = len(frs[0])
    for i in range(0, len(frs), per_bank):
        b = b''.join(frs[i:i + per_bank])
        banks.append(b + bytes([0xFF]) * (16384 - len(b)))
    for f in range(len(frs)):
        a = 0x8000 + (f % per_bank) * size
        tab.append((f // per_bank, a & 255, a >> 8))
    return banks, tab


def table(name, tab):
    return name + ':\n' + ''.join('        db %d,%d,%d\n' % t for t in tab)


def build(msx2, scc, nframes=None):
    from palette_opt import to_v9938
    pal, d1, d2 = coded()
    n = len(d1) if not nframes else min(nframes, len(d1))
    res = dict(n=n, pal=to_v9938(pal), p1=[], p2=[], s1=[], s2=[])
    tabs = ''
    ap = audio(n, RATE_PSG, False)
    for key, ds in (('p1', d1), ('p2', d2)):
        if key == 'p2' and not msx2:
            continue
        frs = [frame_psg(*window(ds[f]), ap[f * ITER:(f + 1) * ITER]) for f in range(n)]
        res[key], tp = pack(frs, 16384 // PSG_BYTES)
    tabs += table('fyp_tab', tp)
    if scc:
        asc = audio(n, RATE_SCC, True)
        for key, ds in (('s1', d1), ('s2', d2)):
            if key == 's2' and not msx2:
                continue
            frs = [frame_scc(*window(ds[f]), asc[f * 2 * ITER:(f + 1) * 2 * ITER]) for f in range(n)]
            res[key], ts = pack(frs, 16384 // SCC_BYTES)
        tabs += table('fys_tab', ts)
    res['tab'] = tabs
    return res


if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else None
    r = build(True, True, n)
    print('frames', r['n'], 'fps %.2f' % FPS, 'PSG banks', len(r['p1']), len(r['p2']), 'SCC banks', len(r['s1']), len(r['s2']), 'palette', r['pal'].hex())
