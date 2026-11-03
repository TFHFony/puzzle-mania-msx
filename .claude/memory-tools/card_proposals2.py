"""Finer proposals for the back of a memory card (like the back of a playing card): a lattice in two shades in the ring of characters, an emblem of thin lines (white on the dark field) in the middle.
The ring cells hold only the dark field and the light shade, the middle cells only the dark field and white: every 8x1 segment has two colours, so the cards can be coded exactly (no dither, no colour spill).
  1  a question mark of thin lines with a dot, in a ring of lattice
  2  the profile of a lady in thin lines (a cameo), in a ring of lattice
  3  XXXL in thin outline letters (2 x 2), in a ring of lattice
usage: python card_proposals2.py [OUTDIR]  -> OUTDIR/proposals2.png"""
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'proposals')
os.makedirs(OUT, exist_ok=True)
SS = 8
WHITE = (255, 255, 255)
BLUE = ((84, 85, 237), (125, 118, 252))            # the dark field and its light shade: the TMS9918A blues 4 and 5
RED = ((212, 82, 77), (255, 121, 120))             # the TMS9918A dark red (6) and light red (9)
IMPACT = 'C:/Windows/Fonts/impact.ttf'


def lattice(w, h):
    y, x = np.mgrid[0:h, 0:w]
    return ((x + y) % 4 == 0) | ((x - y) % 4 == 0)


def ring_masks(w, h):
    """the ring (one character thick) and the middle, as masks over the pixels"""
    cy, cx = np.mgrid[0:h, 0:w]
    ring = (cx < 8) | (cx >= w - 8) | (cy < 8) | (cy >= h - 8)
    return ring, ~ring


def canvas(w, h):
    im = Image.new('L', (w * SS, h * SS), 0)
    return im, ImageDraw.Draw(im)


def stroke(d, pts, width, closed=False):
    pts = [(x * SS, y * SS) for x, y in pts]
    if closed:
        pts = pts + pts[:1]
    d.line(pts, fill=255, width=int(width * SS), joint='curve')
    r = width * SS / 2
    for x, y in pts:
        d.ellipse([x - r, y - r, x + r, y + r], fill=255)


def arc_points(cx, cy, r, a0, a1, n=40):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def emblem_question(w, h, m):
    """a question mark of thin lines, in the middle (the box x0, y0, x1, y1)"""
    x0, y0, x1, y1 = m
    im, d = canvas(w, h)
    bw, bh = x1 - x0, y1 - y0
    cx = (x0 + x1) / 2
    wd = max(1.5, min(bw, bh) * 0.055)
    r = min(bw, bh) * 0.25
    cy = y0 + bh * 0.12 + r
    pts = arc_points(cx, cy, r, 195, 400) + [(cx, cy + r * 1.0), (cx, y0 + bh * 0.70)]
    stroke(d, pts, wd)
    dr = wd * 0.8
    d.ellipse([(cx - dr) * SS, (y0 + bh * 0.84 - dr) * SS, (cx + dr) * SS, (y0 + bh * 0.84 + dr) * SS], fill=255)
    if bw > 40:
        stroke(d, arc_points(cx, (y0 + y1) / 2, min(bw, bh) * 0.47, 0, 360, 80), max(1.0, wd * 0.45), closed=False)       # a thin circle around it (not on the small card)
    return np.asarray(im.resize((w, h), Image.BOX)) >= 110


def emblem_profile(w, h, m):
    """the profile of a lady in thin lines in a thin circle (a cameo)"""
    x0, y0, x1, y1 = m
    im, d = canvas(w, h)
    bw, bh = x1 - x0, y1 - y0
    s = min(bw, bh) / 100.0
    ox = (x0 + x1) / 2 - 50 * s
    oy = (y0 + y1) / 2 - 50 * s
    P = lambda pts: [(ox + x * s, oy + y * s) for x, y in pts]
    lw = max(1.1, s * 3.2)
    face = [(55, 13), (62, 17), (66, 24), (67, 31), (66, 36), (73, 43), (71, 47), (69, 48), (70, 51), (67, 54), (69, 57), (67, 61), (66, 67), (62, 71), (58, 74), (58, 84), (70, 90), (84, 98)]
    stroke(d, P(face), lw)
    stroke(d, P([(38, 84), (38, 70), (31, 62)]), lw)                                     # the back of the neck
    stroke(d, P([(36, 13), (27, 18), (22, 28), (22, 42), (28, 55), (34, 62)]), lw)       # the hair, the back of the head
    stroke(d, P([(36, 13), (46, 10), (55, 13)]), lw)
    stroke(d, P(arc_points(24, 17, 10, 0, 360, 36)), lw * 0.9)                           # the bun
    stroke(d, P([(40, 16), (45, 30), (46, 46)]), lw * 0.8)                               # a wave in the hair
    stroke(d, P([(33, 22), (36, 34), (34, 46)]), lw * 0.8)
    stroke(d, P([(58, 33), (64, 32)]), lw * 0.9)                                         # the eye and the lashes
    stroke(d, P([(66, 55), (70, 55)]), lw * 0.8)                                         # the mouth
    stroke(d, P(arc_points(50, 50, 49, 0, 360, 90)), max(1.0, lw * 0.6))                 # the cameo
    return np.asarray(im.resize((w, h), Image.BOX)) >= 110


def emblem_xxxl(w, h, m):
    """XXXL as thin outline letters, two over two"""
    x0, y0, x1, y1 = m
    im, d = canvas(w, h)
    f = ImageFont.truetype(IMPACT, 600)
    gap = max(2, (x1 - x0) * 0.06)
    cw, ch = ((x1 - x0) - gap) / 2.0, ((y1 - y0) - gap) / 2.0
    for i, c in enumerate('XXXL'):
        g = Image.new('L', (900, 800), 0)
        ImageDraw.Draw(g).text((50, 20), c, font=f, fill=255)
        g = g.crop(g.getbbox()).resize((int(cw * SS), int(ch * SS)), Image.LANCZOS)
        # an outline: the letter minus the letter shrunk
        a = np.asarray(g) >= 128
        from scipy import ndimage
        inner = ndimage.binary_erosion(a, iterations=max(1, int(0.075 * min(cw, ch) * SS)))
        edge = Image.fromarray(((a & ~inner) * 255).astype(np.uint8))
        im.paste(edge, (int((x0 + (i % 2) * (cw + gap)) * SS), int((y0 + (i // 2) * (ch + gap)) * SS)), edge)
    return np.asarray(im.resize((w, h), Image.BOX)) >= 110


def render(emblem, w, h, colours):
    dark, light = colours
    ring, mid = ring_masks(w, h)
    img = np.zeros((h, w, 3), np.uint8)
    img[:] = dark
    lat = lattice(w, h) & ring
    # a light line round the edge of the card, one pixel in
    cy, cx = np.mgrid[0:h, 0:w]
    border = ((cx == 1) | (cx == w - 2) | (cy == 1) | (cy == h - 2)) & ring & (cx > 0) & (cx < w - 1) & (cy > 0) & (cy < h - 1)
    img[(lat | border) & ring] = light
    m = (9, 9, w - 9, h - 9)
    e = emblem(w, h, m) & mid
    img[e] = WHITE
    # two colours per 8x1 segment?
    bad = 0
    for yy in range(h):
        for xx in range(0, w, 8):
            if len({tuple(p) for p in img[yy, xx:xx + 8]}) > 2:
                bad += 1
    return img, bad


DESIGNS = [('1  a question mark in thin lines', emblem_question), ('3  XXXL as outline letters', emblem_xxxl)]

if __name__ == '__main__':
    pad = 12
    cols = [('board card, blue', 40, 40, BLUE, 4), ('board card, red', 40, 40, RED, 4), ('choice screen, blue', 104, 80, BLUE, 3), ('choice screen, red', 104, 80, RED, 3)]
    row_h = 80 * 3 + 30
    W = sum(c[1] * c[4] + pad for c in cols) + pad
    sheet = Image.new('RGB', (W, 30 + row_h * len(DESIGNS)), (30, 30, 30))
    d = ImageDraw.Draw(sheet)
    x = pad
    for name, w, h, col, z in cols:
        d.text((x, 6), name, fill=(220, 220, 220)); x += w * z + pad
    for r, (title, fn) in enumerate(DESIGNS):
        x = pad; y = 30 + r * row_h
        d.text((x, y), title, fill=(255, 230, 120))
        for name, w, h, col, z in cols:
            img, bad = render(fn, w, h, col)
            sheet.paste(Image.fromarray(img).resize((w * z, h * z), Image.NEAREST), (x, y + 14))
            if bad:
                d.text((x, y + 14 + h * z + 2), '%d segments with 3 colours' % bad, fill=(255, 120, 120))
            x += w * z + pad
    sheet.save(os.path.join(OUT, 'proposals2.png'))
    print('ok')
