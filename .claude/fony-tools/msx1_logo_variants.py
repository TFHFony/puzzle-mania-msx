"""Proposals for the MSX1 FONY logo in purple only (not in the ROM): python msx1_logo_variants.py -> work/stills/fony_msx1_variants.png"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
PROJ = r'F:\MSX Projects\PMdev26'
sys.path.insert(0, os.path.join(PROJ, 'tools')); sys.path.insert(0, r'F:\MSX Projects\Dev27\msx1-video-player\tools')
import fony_intro as F, msx1_preview as P
T = P.TMS
img, pal = F.load()
H, W = img.shape
yy, xx = np.mgrid[0:H, 0:W]
chk = ((xx + yy) & 1).astype(bool)
# classes of the 16 disk colours: K black, W wine (the core of the lines), M grey, L light (the edges)
CLS = F.CLS
def render(m, dither=None):
    """m: class -> TMS colour; dither: class -> (colour, colour) checkerboard"""
    cl = np.ones((192, 256), np.uint8)
    cls = np.array(CLS)[img]
    sub = np.ones((H, W), np.uint8)
    for k, c in m.items():
        sub[cls == k] = c
    for k, (c1, c2) in (dither or {}).items():
        mk = cls == k
        sub[mk & chk] = c1; sub[mk & ~chk] = c2
    cl[F.Y0:F.Y0 + H, F.X0:F.X0 + W] = sub
    cols = sorted(set(np.unique(cl).tolist()) | {1})
    pairs = [(a, b) for a in cols for b in cols if a < b]
    dist = np.array([[np.abs(T[i] - T[j]).sum() for j in range(16)] for i in range(16)])
    rend = np.zeros((192, 256, 3), np.uint8)
    for y in range(192):
        for c in range(32):
            px = cl[y, c * 8:c * 8 + 8]
            best = None
            for a, b in pairs:
                e = sum(min(dist[p, a], dist[p, b]) for p in px) + (0 if a == 1 else 1)
                if best is None or e < best[0]: best = (e, a, b)
            _, a, b = best
            for k, p in enumerate(px):
                rend[y, c * 8 + k] = T[b if dist[p, b] < dist[p, a] else a]
    return rend
V = [('A  alles paars (nu in het spel)', dict(K=1, W=13, M=13, L=13), None),
     ('B  alleen de kern paars, randen zwart', dict(K=1, W=13, M=1, L=1), None),
     ('C  kern paars, randen half paars (raster)', dict(K=1, W=13), dict(M=(13, 1), L=(13, 1))),
     ('D  kern paars, randen donkerblauw', dict(K=1, W=13, M=4, L=4), None),
     ('E  kern donkerrood+paars raster, rand paars', dict(K=1, W=13, M=13, L=13), dict(W=(13, 6))),
     ('F  kern paars, randen donkerrood', dict(K=1, W=13, M=6, L=6), None)]
if __name__ == '__main__':
    out = []
    for n, m, d in V:
        out.append((n, render(m, d)))
    cw, ch = 256 * 2, 70 * 2
    sheet = Image.new('RGB', (cw * 2, (ch + 14) * 3))
    for k, (n, r) in enumerate(out):
        im = Image.fromarray(r[14:84]).resize((cw, ch), Image.NEAREST)
        x, y = (k % 2) * cw, (k // 2) * (ch + 14)
        sheet.paste(im, (x, y + 14)); ImageDraw.Draw(sheet).text((x + 3, y + 1), n, fill=(255, 255, 0))
    p = os.path.join(PROJ, 'work', 'stills', 'fony_msx1_variants.png'); sheet.save(p); print(p)
