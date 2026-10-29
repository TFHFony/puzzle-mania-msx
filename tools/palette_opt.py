"""Palette per photo for MSX2 and later (V9938: 16 of 512 colours, 3 bits per channel).
The colours that the game itself uses stay as they are (FIXED, TMS9918A values on the 3-bit grid), the others are fitted to the photo:
k-means in linear light, then a local search on the 3-bit grid that minimises the error of the SCREEN 2 coding (blurred PSNR).
  python tools/palette_opt.py            -> tools/palettes.json: 'tms', 'menu' (one palette for the four thumbnails of the menu), 'photo' (one per photo, in USED order)
  python tools/palette_opt.py test 0     -> only photo 0, prints the gain over the TMS palette
palette entries are RGB 0..255 on the 3-bit grid;  to_v9938(pal) -> 32 bytes (R<<4 | B, G) per colour"""
import os, sys, time, json
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, r'F:\MSX Projects\Dev27\msx1-video-player\tools')
import s4_lab as L, msx1_preview as P
from stills import code_rows
FIXED = (0, 1, 3, 9, 11, 14, 15)      # black, hint green, the two cursor colours, bright yellow of the arrows, grey of the labels, white
BRIGHT = (10, 13)                     # text colours of the menu footer: free, but they must stay readable on black
MINLUMA = 90.0
LV = np.round(np.arange(8) * 255 / 7).astype(np.float32)      # the 8 levels of a V9938 colour channel
STEP = 255 / 7
LOOK = dict(sat=1.4, floor=0.0, contrast=1.15)       # the look of the MSX2 photos (chosen from tools/palette_examples.py): saturated, deep blacks
LOOK_CLIP = {10: dict(sat=1.2, floor=0.03, contrast=1.05)}   # a look of its own per clip (the STEF-1 photo)
PJSON = os.environ.get('PAL_JSON', os.path.join(HERE, 'palettes.json'))


def snap(c):
    return LV[np.abs(np.asarray(c, np.float32)[..., None] - LV).argmin(-1)]


def luma(c):
    return 0.3 * c[0] + 0.55 * c[1] + 0.15 * c[2]


TMS = snap(P.TMS)


def to_v9938(pal):
    out = bytearray()
    for r, g, b in np.round(np.asarray(pal) * 7 / 255).astype(int):
        out += bytes([(int(r) << 4) | int(b), int(g)])
    return bytes(out)


def render(src, pal):
    A, B, bits = code_rows(src.astype(np.float32), pal=pal)
    return np.where(bits[..., None], pal[B][:, :, None, :], pal[A][:, :, None, :]).reshape(src.shape[0], src.shape[1], 3)


def score(src, pal):
    return P.blurred_psnr(src, np.clip(render(src, pal), 0, 255))


def kmeans_pal(src, k, seed=0):
    lin = L.to_lin(src.reshape(-1, 3).astype(np.float32))
    rng = np.random.default_rng(seed)
    X = lin[rng.choice(len(lin), min(20000, len(lin)), replace=False)]
    C = X[rng.choice(len(X), k, replace=False)]
    w = np.array([0.3, 0.55, 0.15], np.float32) * 3
    for _ in range(15):
        a = ((X[:, None] - C[None]) ** 2 * w).sum(-1).argmin(1)
        for j in range(k):
            if (a == j).any():
                C[j] = X[a == j].mean(0)
    return snap(L.to_gam(C))


def half(src):
    h, w = src.shape[:2]
    return src.reshape(h // 2, 2, w // 2, 2, 3).astype(np.float32).mean((1, 3))


def optimise(src, sweeps=4, log=print):
    """stage 1 on the half size picture (4 times faster), stage 2 on the full picture"""
    pal = TMS.copy()
    free = [i for i in range(16) if i not in FIXED and i not in BRIGHT]
    pal[free] = kmeans_pal(src, len(free))
    movable = free + list(BRIGHT)
    pal = refine(half(src), pal, movable, sweeps, lambda t: log('  half ' + t))
    pal, best = refine(src, pal, movable, 1, lambda t: log('  full ' + t), want_score=True)
    return pal, best


def refine(src, pal, movable, sweeps, log, want_score=False):
    best = score(src, pal)
    log('start %.2f dB' % best)
    for sw in range(sweeps):
        gained = False
        for i in movable:
            for ch in range(3):
                for dl in (-STEP, STEP):
                    t = pal.copy(); t[i, ch] = np.clip(t[i, ch] + dl, 0, 255)
                    if i in BRIGHT and luma(t[i]) < MINLUMA:
                        continue
                    s = score(src, t)
                    if s > best + 1e-3:
                        best, pal, gained = s, t, True
        log('sweep %d: %.2f dB' % (sw, best))
        if not gained:
            break
    return (pal, best) if want_score else pal


def adjust(src, sat, floor, contrast):
    """the adaptive gamma of lift() with a lower floor for the blacks, then saturation and contrast"""
    from PIL import ImageEnhance
    a = np.asarray(src, np.float32) / 255
    lum = float((0.3 * a[..., 0] + 0.55 * a[..., 1] + 0.15 * a[..., 2]).mean())
    g = min(1.0, max(0.55, np.log(0.45) / np.log(max(lum, 0.05))))
    a = floor + (1 - floor) * a ** g
    im = Image.fromarray(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8))
    im = ImageEnhance.Color(im).enhance(sat)
    if contrast != 1.0:
        b = np.asarray(im, np.float32) / 255
        b = np.clip((b - 0.5) * contrast + 0.5, 0, 1)
        im = Image.fromarray((b * 255 + 0.5).astype(np.uint8))
    return im


def photo_sources():
    from encode_clips import USED
    choices = json.load(open(os.path.join(HERE, 'choices.json')))
    return [adjust(Image.open(os.path.join(PROJ, 'work', 'stills', 'clip%02d_%d_src.png' % (c, choices[c]))).convert('RGB'), **LOOK_CLIP.get(c, LOOK)) for c in USED]


def menu_mosaic(srcs):
    from build_game import thumbnail
    m = np.zeros((240, 320, 3), np.uint8)
    for i, s in enumerate(srcs):
        th = np.asarray(thumbnail(s, 100, 76))
        y, x = (i // 3) * 80 + 2, (i % 3) * 104 + 2
        m[y:y + 76, x:x + 100] = th
    return m


FIXED_SIZE = (0, 1, 9, 11, 14, 15)      # the size menu needs less: white and grey text, the cursor colours


def size_mosaic(src):
    """the four size buttons of a photo (96 x 72 each, thumbnail 92 x 68 with the grid lines), as one picture"""
    from build_game import thumbnail
    m = np.zeros((144, 192, 3), np.uint8)
    for k, N in enumerate((3, 4, 5, 6)):
        a = np.zeros((72, 96, 3), np.uint8)
        a[2:70, 2:94] = np.asarray(thumbnail(src, 92, 68))
        for j in range(1, N):
            xx = 2 + round(j * 92 / N); yy = 2 + round(j * 68 / N)
            a[2:70, xx] = 255; a[yy, 2:94] = 255
        y, x = (k // 2) * 72, (k % 2) * 96
        m[y:y + 72, x:x + 96] = a
    return m


def optimise_size(src):
    global FIXED, BRIGHT
    old = (FIXED, BRIGHT)
    FIXED, BRIGHT = FIXED_SIZE, ()
    try:
        return optimise(size_mosaic(src), log=lambda t: None)
    finally:
        FIXED, BRIGHT = old


def load():
    return json.load(open(PJSON))


if __name__ == '__main__':
    srcs = photo_sources()
    if sys.argv[1:2] == ['test']:
        for p in [int(a) for a in sys.argv[2:]] or [0]:
            src = np.asarray(srcs[p]); t0 = time.time()
            base = score(src, P.TMS)
            print('photo', p, 'TMS palette %.2f dB (%.1f s per coding)' % (base, time.time() - t0), flush=True)
            pal, best = optimise(src, log=lambda s: print(s, flush=True))
            print('  gain %.2f dB' % (best - base))
        sys.exit()
    if sys.argv[1:2] == ['size']:
        res = json.load(open(PJSON))
        res.setdefault('size', [None] * len(srcs))
        from concurrent.futures import ProcessPoolExecutor
        todo = [p for p in range(len(srcs)) if not res['size'][p]]
        with ProcessPoolExecutor(max_workers=min(8, len(todo)) or 1) as ex:            # one process per photo (the photos are independent)
            for p, (pal, best) in zip(todo, ex.map(optimise_size, [srcs[p] for p in todo])):
                print('size palette photo', p, '%.2f dB' % best, flush=True)
                res['size'][p] = np.asarray(pal).astype(int).tolist()
                json.dump(res, open(PJSON, 'w'))
        print('done'); sys.exit()
    res = json.load(open(PJSON)) if os.path.exists(PJSON) else {}
    res['tms'] = TMS.astype(int).tolist()
    res.setdefault('photo', [None] * len(srcs))
    for p, s in enumerate(srcs):
        if res['photo'][p]:
            continue
        print('photo', p, flush=True)
        pal, best = optimise(np.asarray(s), log=lambda t: print(t, flush=True))
        res['photo'][p] = np.asarray(pal).astype(int).tolist()
        json.dump(res, open(PJSON, 'w'))
    if 'menu' not in res:
        print('menu', flush=True)
        pal, best = optimise(menu_mosaic(srcs), log=lambda t: print(t, flush=True))
        res['menu'] = np.asarray(pal).astype(int).tolist()
        json.dump(res, open(PJSON, 'w'))
    print('done')
