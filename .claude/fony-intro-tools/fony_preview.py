"""Preview of FONY.mp4 as an intro of Puzzle Mania: a 128x72 window in the SCREEN 2 picture (2 colours per 8x1), MSX1 (TMS9918A palette) next to MSX2 (one optimised
16 colour palette for the whole clip), PAL 25 fps / NTSC 30 fps, the sound as the PSG would play it (8 kHz, the volume levels of the player).
The player writes whole cells (16 bytes: 8 pattern + 8 colour) of the window every frame:  PAL 25 fps: 160 cells fit, the window has 144 (all of them, every frame);
NTSC 30 fps: 134 cells fit (PSG 8 kHz), so the 10 cells with the smallest change stay as they are (the preview does that too).
usage: python fony_preview.py [OUTDIR]   -> OUTDIR/FONY_PAL25.mp4, FONY_NTSC30.mp4, stills"""
import os, sys, subprocess, json
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(PROJ, 'tools')); sys.path.insert(0, r'F:\MSX Projects\Dev27\msx1-video-player\tools')
SRC = r'F:\MSX Projects\Dev27\FONY.mp4'
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'preview')
WW, WH = 128, 72                 # the window (16 x 9 cells)
WX, WY = 64, 56                  # its place on the 256x192 screen (cell aligned)
NTSC_CELLS = 134                 # cells per frame that fit at 30 fps (PSG 8 kHz)
SAT, GAMMA = 1.25, 0.85          # the look (a little more colour, a bit brighter: the clip is dark)


def frames():
    cmd = ['ffmpeg', '-v', 'error', '-i', SRC, '-vf', 'scale=%d:%d:flags=lanczos' % (WW, WH), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.uint8).reshape(-1, WH, WW, 3)


def grade(fr, lo, hi):
    from PIL import ImageEnhance
    a = np.clip((fr.astype(np.float32) - lo) / (hi - lo), 0, 1)
    im = ImageEnhance.Color(Image.fromarray((a * 255 + 0.5).astype(np.uint8))).enhance(SAT)
    return (np.clip(np.asarray(im).astype(np.float32) / 255, 0, 1) ** GAMMA * 255 + 0.5).astype(np.uint8)


def canvas(win):
    img = np.zeros((192, 256, 3), np.uint8)
    img[WY:WY + WH, WX:WX + WW] = win
    fix = np.ones((192, 256), np.int8)
    fix[WY:WY + WH, WX:WX + WW] = 0
    return img, fix


def _enc(args):
    import build_game as B
    win, pal = args
    img, fix = canvas(win)
    data, rend = B.coded(img, fix, pal)
    return data, rend


def optimise_palette(gr):
    """one 16 colour palette (colour 0 stays black) for the whole clip: k-means on a mosaic of frames, then the coordinate search of tools/palette_opt.py"""
    import palette_opt as PO
    sel = gr[np.linspace(0, len(gr) - 1, 12).astype(int)]
    mos = np.concatenate([np.concatenate(list(sel[r * 4:(r + 1) * 4]), axis=1) for r in range(3)], axis=0)
    pal = PO.TMS.copy()
    pal[1:] = PO.kmeans_pal(mos, 15)
    pal[0] = (0, 0, 0)
    pal = PO.refine(PO.half(mos), pal, list(range(1, 16)), 4, lambda t: print('  half', t, flush=True))
    pal, best = PO.refine(mos, pal, list(range(1, 16)), 1, lambda t: print('  full', t, flush=True), want_score=True)
    return pal


def cells_of(img):
    return img.reshape(24, 8, 32, 8, 3)


def limit(rends, datas, n):
    """what the screen shows when at most n cells are written per frame: the cells that differ most are written (every cell is 16 bytes: pattern + colour)"""
    shown = rends[0].copy(); sdata = datas[0]
    out = [shown.copy()]
    for k in range(1, len(rends)):
        new = rends[k]; nd = datas[k]
        diff = np.zeros((24, 32))
        for cy in range(7, 16):
            for cx in range(8, 24):
                u = cy * 32 + cx
                if nd[u * 8:u * 8 + 8] != sdata[u * 8:u * 8 + 8] or nd[6144 + u * 8:6144 + u * 8 + 8] != sdata[6144 + u * 8:6144 + u * 8 + 8]:
                    diff[cy, cx] = np.abs(cells_of(new)[cy, :, cx].astype(int) - cells_of(shown)[cy, :, cx].astype(int)).sum() + 1
        order = np.argsort(-diff, axis=None)[:n]
        bd = bytearray(sdata)
        for idx in order:
            cy, cx = divmod(int(idx), 32)
            if diff[cy, cx] == 0: break
            u = cy * 32 + cx
            bd[u * 8:u * 8 + 8] = nd[u * 8:u * 8 + 8]; bd[6144 + u * 8:6144 + u * 8 + 8] = nd[6144 + u * 8:6144 + u * 8 + 8]
            shown[cy * 8:cy * 8 + 8, cx * 8:cx * 8 + 8] = new[cy * 8:cy * 8 + 8, cx * 8:cx * 8 + 8]
        sdata = bytes(bd)
        out.append(shown.copy())
    return out


def audio(tempo, path):
    """the sound of the clip as the 8 kHz PSG player plays it (3 channels summed: the 170 volume levels of tools/music.py), the length of the picture (tempo: 1.0417 PAL, 1.25 NTSC, pitch kept)"""
    import music
    tmp = path + '.tmp.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', SRC, '-vn', '-ac', '1', '-af', 'atempo=%.5f' % tempo, '-ar', '44100', tmp], check=True)
    x = music.decode(tmp)
    lv, _ = music.levels()
    q = music.quantise(x, lv)
    y = (lv[q] * 2 - 1).astype(np.float32)
    raw = path + '.raw'
    y.tofile(raw)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', '8000', '-ac', '1', '-i', raw, '-ar', '44100', '-c:a', 'pcm_s16le', path], check=True)
    os.remove(raw); os.remove(tmp)


def movie(l, r, fps, wav, out):
    d = os.path.join(OUT, 'frames_' + os.path.basename(out)[:-4])
    os.makedirs(d, exist_ok=True)
    for k in range(len(l)):
        im = Image.new('RGB', (256 * 2 * 3, 192 * 3))
        im.paste(Image.fromarray(l[k]).resize((768, 576), Image.NEAREST), (0, 0))
        im.paste(Image.fromarray(r[k]).resize((768, 576), Image.NEAREST), (768, 0))
        im.save(os.path.join(d, '%03d.png' % k))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(fps), '-i', os.path.join(d, '%03d.png'), '-i', wav, '-c:v', 'libx264', '-crf', '14', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest', out], check=True)


if __name__ == '__main__':
    from concurrent.futures import ProcessPoolExecutor
    os.makedirs(OUT, exist_ok=True)
    fr = frames()
    print(len(fr), 'frames', flush=True)
    lum = fr[::3].astype(np.float32).mean(-1)
    lo, hi = float(np.percentile(lum, 1)), float(np.percentile(lum, 99.5))
    print('stretch', lo, hi, flush=True)
    gr = np.stack([grade(f, lo, hi) for f in fr])
    pal = optimise_palette(gr)
    json.dump(pal.tolist(), open(os.path.join(OUT, 'palette.json'), 'w'))
    with ProcessPoolExecutor(max_workers=8) as ex:
        r1 = list(ex.map(_enc, [(g, None) for g in gr], chunksize=2)); print('msx1 coded', flush=True)
        r2 = list(ex.map(_enc, [(g, pal) for g in gr], chunksize=2)); print('msx2 coded', flush=True)
    d1, n1 = [bytes(x[0]) for x in r1], [x[1] for x in r1]
    d2, n2 = [bytes(x[0]) for x in r2], [x[1] for x in r2]
    Image.fromarray(np.concatenate([n1[120], n2[120]], axis=1)).resize((1536, 384), Image.NEAREST).save(os.path.join(OUT, 'still.png'))
    audio(25 / 24, os.path.join(OUT, 'a_pal.wav'))
    audio(1.25, os.path.join(OUT, 'a_ntsc.wav'))
    movie(n1, n2, 25, os.path.join(OUT, 'a_pal.wav'), os.path.join(OUT, 'FONY_PAL25.mp4'))
    l, r = limit(n1, d1, NTSC_CELLS), limit(n2, d2, NTSC_CELLS)
    movie(l, r, 30, os.path.join(OUT, 'a_ntsc.wav'), os.path.join(OUT, 'FONY_NTSC30.mp4'))
    print('done')
