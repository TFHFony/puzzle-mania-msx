"""The jigsaw outro of the title screens: when the music is over, the picture in the letters grows into the whole photo, is cut into 5x5 jigsaw pieces and the pieces fall away on black.
Three streams (tools/build_game.py): the photo of the title for the TMS palette (MSX1), for the palette of the photo (MSX2), and the last shot of the title video.
The stream (played by game/jigplay.asm, in the overlay bank) holds only the VRAM bytes that change per frame:
  record:       n (1..250 cells), address low, address high | 0x40, n * 8 bytes      (pattern table at 0, colour table at 2000h, one cell = one character = 8 bytes)
  end of frame: 0, e    the player waits for one vertical blanking and then for e more
  next bank:    255     254: end of the stream
A bank only holds whole frames.  The encoder picks the time step by itself: it estimates the writing time of a frame (26 cycles per byte, the loop of the player), the frame appears when the writing is
done, so the picture of a frame is the picture of the time at which it appears and the animation runs at its true speed whatever the amount of change.
usage: python jigsaw.py   -> a self test with the photo of the title (frames in .claude/jigsaw-tools/preview/stream_*)"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, r'F:\MSX Projects\Dev27\msx1-video-player\tools')

N = 5; W, H = 256, 192; SS = 2
PAD = 4                                        # px around the picture while the pieces are cut (the cuts shrink the pieces, not the border of the picture)
PERIOD = 3579545 / 50.0                        # cycles of a frame at 50 Hz (the estimate; 60 Hz is shorter, the animation is then a little slower)
CELL_C, REC_C, FRAME_C = 221, 150, 600         # cycles: one cell (8 bytes of the loop of jigplay.asm), one record (VDP address + loop set-up), the end of a frame (keys, vertical blanking)
SAFE = 0.88                                    # the share of a frame that the writing may use in the estimate
PMAX = 8
T_HOLD0 = 0.4; T_REVEAL = 0.7; T_HOLD1 = 0.5; T_CUT = 0.3; T_END = 0.4
G = 1000.0                                     # px/s^2


def cuts():
    return [round(i * W / N) for i in range(N + 1)], [round(i * H / N) for i in range(N + 1)]


def piece_masks(rng):
    xs, ys = cuts()
    hz = rng.choice([-1, 1], size=(N, N - 1))      # vertical edge right of piece (r, c): +1 = piece (r, c) has the tab
    vt = rng.choice([-1, 1], size=(N - 1, N))      # edge below piece (r, c)
    S = SS * 4
    P = PAD * S
    big = {}
    for r in range(N):
        for c in range(N):
            im = Image.new('L', ((W + 2 * PAD) * S, (H + 2 * PAD) * S), 0); d = ImageDraw.Draw(im)
            x0, x1, y0, y1 = xs[c] * S, xs[c + 1] * S, ys[r] * S, ys[r + 1] * S
            ex0, ex1, ey0, ey1 = (x0 - P if c == 0 else x0), (x1 + P if c == N - 1 else x1), (y0 - P if r == 0 else y0), (y1 + P if r == N - 1 else y1)
            d.rectangle([ex0 + P, ey0 + P, ex1 + P - 1, ey1 + P - 1], fill=255)
            rad = 0.2 * min(x1 - x0, y1 - y0); neck = 0.09 * min(x1 - x0, y1 - y0)

            def knob(cx, cy, dx, dy, sign):
                col = 255 if sign > 0 else 0
                cx += P; cy += P
                hx, hy = cx + dx * rad * 1.15 * sign, cy + dy * rad * 1.15 * sign
                d.ellipse([hx - rad, hy - rad, hx + rad, hy + rad], fill=col)
                nx = neck if dx == 0 else 0; ny = neck if dy == 0 else 0
                d.rectangle([min(cx, hx) - nx, min(cy, hy) - ny, max(cx, hx) + nx, max(cy, hy) + ny], fill=col)
            my, mx = (y0 + y1) / 2, (x0 + x1) / 2
            if c < N - 1: knob(x1, my, 1, 0, hz[r, c])
            if c > 0: knob(x0, my, -1, 0, -hz[r, c - 1])
            if r < N - 1: knob(mx, y1, 0, 1, vt[r, c])
            if r > 0: knob(mx, y0, 0, -1, -vt[r - 1, c])
            big[(r, c)] = im
    return big


def make_pieces(photo, seed=26):
    """pieces with a gap of 1 px between them (the cuts); the photo is cut at SS times the resolution"""
    rng = np.random.default_rng(seed)
    big = piece_masks(rng)
    ph = Image.fromarray(np.pad(photo, ((PAD, PAD), (PAD, PAD), (0, 0)), mode='edge')).resize(((W + 2 * PAD) * SS, (H + 2 * PAD) * SS), Image.LANCZOS)
    pcs = []
    for (r, c), m in big.items():
        m2 = m.resize(((W + 2 * PAD) * SS, (H + 2 * PAD) * SS), Image.BOX).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MinFilter(3))
        m2 = m2.crop((PAD * SS, PAD * SS, (PAD + W) * SS, (PAD + H) * SS))
        bb = m2.getbbox()
        spr = Image.new('RGBA', (bb[2] - bb[0], bb[3] - bb[1]))
        spr.paste(ph.crop((PAD * SS + bb[0], PAD * SS + bb[1], PAD * SS + bb[2], PAD * SS + bb[3]))); spr.putalpha(m2.crop(bb))
        pcs.append(dict(r=r, c=c, spr=spr, bb=bb,
                        t0=(N - 1 - r) * 0.13 + rng.uniform(0, 0.12),       # the bottom row falls first: nothing holds it
                        w=rng.uniform(-1, 1) * 150, vx=rng.uniform(-1, 1) * 25))
    return pcs


def compose(pcs, t_fall):
    """RGB + coverage at 1x of the pieces t_fall seconds after the first one let go (a piece that has not let go yet lies still: its pixels do not change)"""
    cv = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
    for p in sorted(pcs, key=lambda p: -p['r']):
        spr = p['spr']; bb = p['bb']
        tf = max(0.0, t_fall - p['t0'])
        if tf == 0:
            cv.alpha_composite(spr, (bb[0], bb[1]))
            continue
        cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
        s2 = spr.rotate(p['w'] * tf, resample=Image.BICUBIC, expand=True)
        x = int(round(cx + p['vx'] * tf * SS - s2.width / 2)); y = int(round(cy + 0.5 * G * tf * tf * SS - s2.height / 2))
        if y >= H * SS or x >= W * SS or x + s2.width <= 0 or y + s2.height <= 0: continue
        cv.alpha_composite(s2, (max(x, 0), max(y, 0)), (max(-x, 0), max(-y, 0)))
    a = np.asarray(cv.resize((W, H), Image.BOX), np.float32)
    al = a[..., 3] / 255
    rgb = np.where(al[..., None] > 0.02, a[..., :3] / np.maximum(al[..., None], 0.02), 0)
    return np.clip(rgb, 0, 255), al


def fall_length(pcs):
    return max(p['t0'] for p in pcs) + np.sqrt(2 * (H * 1.3) / G) + 0.25


class Scene:
    def __init__(self, photo, letter_mask):
        self.photo = photo
        self.mask = letter_mask
        self.dist = ndimage.distance_transform_edt(~letter_mask)
        self.pcs = make_pieces(photo)

    def reveal(self, u):                       # the picture grows out of the letters
        vis = self.dist <= u ** 1.3 * (self.dist.max() + 2)
        img = np.zeros((H, W, 3), np.uint8); img[vis] = self.photo[vis]
        return img, vis

    def cut(self):                             # the cuts appear
        return self.fall(0.0)

    def fall(self, t):
        rgb, al = compose(self.pcs, t)
        vis = al > 0.5
        return np.where(vis[..., None], rgb, 0).astype(np.uint8), vis


def _code(args):
    img, vis, pal = args
    import build_game as B
    return B.coded(img, (~vis).astype(np.int8), pal)[0]


def records(prev, cur):
    """the records that turn the 12288 bytes of prev (None = all different) into cur -> list of (addr, n, bytes).
    A run of changed cells is written as its patterns and then its colours, one run after the other: the picture never shows new patterns with old colours for long"""
    cur_a = np.frombuffer(cur, np.uint8).reshape(2, 768, 8)
    if prev is None:
        ch = np.ones(768, bool)
    else:
        ch = (np.frombuffer(prev, np.uint8).reshape(2, 768, 8) != cur_a).any(-1).any(0)
    recs = []
    idx = np.flatnonzero(ch)
    k = 0
    while k < len(idx):
        a = idx[k]; e = a
        while k + 1 < len(idx) and idx[k + 1] - e <= 3:            # a gap of up to 2 unchanged cells is cheaper to write than to skip
            k += 1; e = idx[k]
        k += 1
        while a <= e:
            n = min(120, e - a + 1)                                 # (short runs: the patterns and the colours of a cell are never far apart in time)
            for t in range(2):
                recs.append((t * 0x2000 + a * 8, n, cur_a[t, a:a + n].tobytes()))
            a += n
    return recs


def frame_bytes(recs, extra):
    out = bytearray()
    for addr, n, data in recs:
        out += bytes([n, addr & 255, (addr >> 8) | 0x40]) + data
    out += bytes([0, min(255, max(0, extra))])
    return bytes(out)


def periods(recs):
    cyc = FRAME_C + sum(REC_C + n * CELL_C for _, n, _ in recs)
    return max(1, int(np.ceil(cyc / (PERIOD * SAFE))))


def build(scene, start, pal, ex, full_start=False, log=print):
    """-> (banks, info, shown).  start: the 12288 bytes of the picture that the screen shows when the stream starts (the logo: the letters filled with the photo);
    full_start: the stream writes it first (the last shot of the title video: its exact bytes differ a little between the PSG and the SCC video), else it is there already"""
    frames = []                                # (records, periods, extra)
    cur = start
    recs = records(None, start) if full_start else []
    p0 = periods(recs)
    frames.append((recs, p0, int(round(T_HOLD0 * 50)) - p0))
    shown = []                                 # (name, image data) for the preview

    def phase(img_at, duration, tag):
        nonlocal cur
        t = 0.0
        while t < duration - 1e-6:
            cands = []
            for p in range(1, PMAX + 1):
                tp = min(duration, t + p * 0.02)
                img, vis = img_at(tp)
                cands.append((tp, ex.submit(_code, (img, vis, pal)), bool(vis.any())))
            chosen = None
            for p, (tp, fu, anyvis) in enumerate(cands, 1):
                d = fu.result()
                r = records(cur, d)
                if chosen is None and periods(r) <= p:
                    chosen = (tp, d, r, p, anyvis)
                last = (tp, d, r, p, anyvis)
            tp, d, r, p, anyvis = chosen or last
            q = periods(r)
            frames.append((r, q, max(0, p - q))); shown.append((tag, tp, d))
            cur = d; t = tp
            log('  %s t=%.2f p=%d cells=%d' % (tag, t, p, sum(n for _, n, _ in r)))
            if not anyvis:
                break                          # everything has fallen out of the picture
        return t

    phase(lambda t: scene.reveal(t / T_REVEAL), T_REVEAL, 'reveal')
    r, q, _ = frames[-1]
    frames[-1] = (r, q, int(round(T_HOLD1 * 50)) - q)
    d = ex.submit(_code, (scene.cut()[0], scene.cut()[1], pal)).result()          # the cuts
    r = records(cur, d); cur = d
    frames.append((r, periods(r), int(round(T_CUT * 50)) - periods(r))); shown.append(('cut', 0, d))
    tfall = fall_length(scene.pcs)
    phase(lambda t: scene.fall(t), tfall, 'fall')
    black = ex.submit(_code, (np.zeros((H, W, 3), np.uint8), np.zeros((H, W), bool), pal)).result()
    r = records(cur, black)
    frames.append((r, periods(r), int(round(T_END * 50)) - periods(r))); shown.append(('black', 0, black))
    # pack: a bank holds whole frames
    banks = []; cur_b = bytearray()
    for r, p, extra in frames:
        fb = frame_bytes(r, extra)
        assert len(fb) <= 16384 - 1, len(fb)
        if len(cur_b) + len(fb) > 16384 - 1:
            cur_b.append(255); banks.append(bytes(cur_b).ljust(16384, b'\xff')); cur_b = bytearray()
        cur_b += fb
    cur_b.append(254)
    banks.append(bytes(cur_b).ljust(16384, b'\xff'))
    info = dict(frames=len(frames), bytes=sum(len(frame_bytes(r, 0)) for r, _, _ in frames), banks=len(banks), seconds=sum(p + max(0, e) for _, p, e in frames) / 50.0)
    return banks, info, shown


def start_data(scene, pal, ex):
    """the letters filled with the photo, coded like the title picture"""
    img, vis = scene.reveal(0.0)
    return ex.submit(_code, (img, vis, pal)).result()


if __name__ == '__main__':
    from concurrent.futures import ProcessPoolExecutor
    import json
    import build_game as B, palette_opt as PO, title_video
    from encode_clips import USED
    choices = json.load(open(os.path.join(HERE, 'choices.json')))
    src = Image.open(os.path.join(PROJ, 'work', 'stills', 'clip07_%d_src.png' % choices[7])).convert('RGB')
    photo = np.asarray(B.lift(src))
    sc = Scene(photo, title_video.letter_mask())
    with ProcessPoolExecutor(max_workers=8) as ex:
        base = start_data(sc, None, ex)
        banks, info, shown = build(sc, base, None, ex)
    print(info)
