"""Attract mode idea: after the music the title photo becomes a 5x5 jigsaw that falls apart on black (preview of the animation, MSX1 and MSX2 coding).
usage: python jigsaw.py [FPS]   (default 25)  -> preview/frames_{src,msx1,msx2}/NNN.png (then make_mp4.py)
The photo is the one of the title (clip 7, choices.json), prepared like tools/build_game.py: MSX1 lift(), MSX2 palette_opt.adjust(LOOK) + the palette of that photo.
Frames are coded with stills.encode (2 colours per 8x1 pixels), black background = fixed black (fix=1)."""
import os, sys, json, shutil
import numpy as np
from PIL import Image, ImageDraw
from multiprocessing import Pool
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(PROJ, 'tools')); sys.path.insert(0, r'F:\MSX Projects\Dev27\msx1-video-player\tools')
FPS = float(sys.argv[1]) if len(sys.argv) > 1 else 25.0
OUT = os.path.join(HERE, 'preview')
N = 5; W, H = 256, 192; SS = 2

# timeline (s)
T_HOLD0 = 0.4      # the logo as it is (letters filled with the photo)
T_REVEAL = 0.7     # the photo grows out of the letters
T_HOLD1 = 0.5      # the whole photo
T_LOOSE = 0.35     # the cuts open, the pieces wobble
G = 1000.0         # px/s^2
T_END = 0.3        # black at the end


def cuts():
    return [round(i * W / N) for i in range(N + 1)], [round(i * H / N) for i in range(N + 1)]


def piece_masks(rng):
    """one mask per piece over the whole picture (at 4*SS), with a tab or a notch on every inner edge"""
    xs, ys = cuts()
    hz = rng.choice([-1, 1], size=(N, N - 1))      # vertical edge right of piece (r, c): +1 = piece (r, c) has the tab
    vt = rng.choice([-1, 1], size=(N - 1, N))      # edge below piece (r, c)
    S = SS * 4
    big = {}
    for r in range(N):
        for c in range(N):
            im = Image.new('L', (W * S, H * S), 0); d = ImageDraw.Draw(im)
            x0, x1, y0, y1 = xs[c] * S, xs[c + 1] * S, ys[r] * S, ys[r + 1] * S
            d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=255)
            rad = 0.2 * min(x1 - x0, y1 - y0); neck = 0.09 * min(x1 - x0, y1 - y0)

            def knob(cx, cy, dx, dy, sign):
                col = 255 if sign > 0 else 0
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
    """list of dicts: sprite (RGBA at SS scale, bbox of the mask), its bbox and the movement parameters (the same for every photo version: same seed)"""
    rng = np.random.default_rng(seed)
    big = piece_masks(rng)
    ph = Image.fromarray(photo).resize((W * SS, H * SS), Image.LANCZOS)
    pcs = []
    for (r, c), m in big.items():
        m2 = m.resize((W * SS, H * SS), Image.BOX)
        bb = m2.getbbox()
        spr = Image.new('RGBA', (bb[2] - bb[0], bb[3] - bb[1]))
        spr.paste(ph.crop(bb)); spr.putalpha(m2.crop(bb))
        pcs.append(dict(r=r, c=c, spr=spr, bb=bb,
                        t0=(N - 1 - r) * 0.13 + rng.uniform(0, 0.12),       # the bottom row falls first: nothing holds it
                        w=rng.uniform(-1, 1) * 150, vx=rng.uniform(-1, 1) * 25, tilt=rng.uniform(-1, 1) * 3, jit=rng.uniform(-1, 1, 2) * 1.2))
    return pcs


def compose(pcs, t_fall, loose):
    """RGB + coverage at 1x; loose 0..1 = how far the cuts are open, t_fall = seconds since the start of the fall"""
    cv = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
    for p in sorted(pcs, key=lambda p: -p['r']):
        spr = p['spr']; bb = p['bb']
        cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
        tf = max(0.0, t_fall - p['t0'])
        ang = p['tilt'] * loose + p['w'] * tf
        dx = p['jit'][0] * loose * SS + p['vx'] * tf * SS
        dy = p['jit'][1] * loose * SS + 0.5 * G * tf * tf * SS
        sc = 1 - 0.035 * loose
        s2 = spr.resize((max(1, round(spr.width * sc)), max(1, round(spr.height * sc))), Image.BICUBIC) if sc != 1 else spr
        s2 = s2.rotate(ang, resample=Image.BICUBIC, expand=True)
        x, y = int(round(cx + dx - s2.width / 2)), int(round(cy + dy - s2.height / 2))
        if y >= H * SS or x >= W * SS or x + s2.width <= 0 or y + s2.height <= 0: continue          # outside the picture
        cv.alpha_composite(s2, (max(x, 0), max(y, 0)), (max(-x, 0), max(-y, 0)))
    a = np.asarray(cv.resize((W, H), Image.BOX), np.float32)
    al = a[..., 3] / 255
    rgb = np.where(al[..., None] > 0.02, a[..., :3] / np.maximum(al[..., None], 0.02), 0)
    return np.clip(rgb, 0, 255), al


def timeline(pcs):
    dt = 1 / FPS
    fall_dur = max(p['t0'] for p in pcs) + np.sqrt(2 * (H * 1.3) / G) + 0.25
    seq = [('logo',)] * int(T_HOLD0 * FPS)
    nr = int(T_REVEAL * FPS); seq += [('reveal', (k + 1) / nr) for k in range(nr)]
    seq += [('full',)] * int(T_HOLD1 * FPS)
    nl = int(T_LOOSE * FPS); seq += [('loose', (k + 1) / nl) for k in range(nl)]
    seq += [('fall', (k + 1) * dt) for k in range(int(fall_dur * FPS))]
    seq += [('black',)] * int(T_END * FPS)
    return seq


def frame_rgb(item, photo, pcs, mask_logo, dist):
    kind = item[0]
    if kind == 'logo':
        img = np.zeros((H, W, 3), np.uint8); img[mask_logo] = photo[mask_logo]; return img, mask_logo
    if kind == 'reveal':
        vis = dist <= item[1] ** 1.3 * (dist.max() + 2)
        img = np.zeros((H, W, 3), np.uint8); img[vis] = photo[vis]; return img, vis
    if kind == 'full':
        return photo, np.ones((H, W), bool)
    if kind == 'black':
        return np.zeros((H, W, 3), np.uint8), np.zeros((H, W), bool)
    rgb, al = compose(pcs, 0, item[1]) if kind == 'loose' else compose(pcs, item[1], 1.0)
    vis = al > 0.5
    return np.where(vis[..., None], rgb, 0).astype(np.uint8), vis


def code1(args):
    i, img, vis, pal = args
    from stills import encode
    return i, encode(img.astype(np.float32), (~vis).astype(np.int8), pal)[2]


if __name__ == '__main__':
    from build_game import lift
    import palette_opt as PO
    import title_video
    from encode_clips import USED
    choices = json.load(open(os.path.join(PROJ, 'tools', 'choices.json')))
    src = Image.open(os.path.join(PROJ, 'work', 'stills', 'clip07_%d_src.png' % choices[7])).convert('RGB')
    pj = PO.load(); pal2 = np.array(pj['photo'][USED.index(7)], np.float32)
    ph1 = np.asarray(lift(src)); ph2 = np.asarray(PO.adjust(src, **PO.LOOK))
    mask = title_video.letter_mask()
    dist = ndimage.distance_transform_edt(~mask)
    pcs1 = make_pieces(ph1); pcs2 = make_pieces(ph2)
    seq = timeline(pcs1)
    print('frames', len(seq), 'at', FPS, 'fps =', round(len(seq) / FPS, 2), 's', flush=True)
    for d in ('src', 'msx1', 'msx2'):
        shutil.rmtree(os.path.join(OUT, 'frames_' + d), ignore_errors=True); os.makedirs(os.path.join(OUT, 'frames_' + d))
    j1, j2 = [], []
    for i, it in enumerate(seq):
        img1, vis1 = frame_rgb(it, ph1, pcs1, mask, dist)
        img2, vis2 = frame_rgb(it, ph2, pcs2, mask, dist)
        Image.fromarray(img2).save(os.path.join(OUT, 'frames_src', '%03d.png' % i))
        j1.append((i, img1, vis1, None)); j2.append((i, img2, vis2, pal2))
    with Pool(8) as pool:
        for tag, jobs in (('msx1', j1), ('msx2', j2)):
            for i, im in pool.imap_unordered(code1, jobs, chunksize=2):
                Image.fromarray(im).save(os.path.join(OUT, 'frames_' + tag, '%03d.png' % i))
            print('coded', tag, flush=True)
