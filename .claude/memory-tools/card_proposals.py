"""Proposals for the back of a memory card: the profile of a lady, a nicer question mark, XXXL (under each other / 2 x 2) in red and white.
Every design is a two colour picture (a field colour and white), drawn at 8x and cut to the pixels, so that it can be coded exactly (no dither, no colour spill).
usage: python card_proposals.py [OUTDIR]  -> OUTDIR/proposals.png (the board card 40x40 and the card of the choice screen 104x80, blue and red, MSX1 colours)"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'proposals')
os.makedirs(OUT, exist_ok=True)
SS = 8
RED, BLUE, WHITE, BLACK = (255, 73, 73), (84, 85, 237), (255, 255, 255), (0, 0, 0)
IMPACT = 'C:/Windows/Fonts/impact.ttf'


def canvas(w, h):
    im = Image.new('L', (w * SS, h * SS), 0)
    return im, ImageDraw.Draw(im)


def frame(d, w, h, border=3, inset=0):
    d.rectangle([inset * SS, inset * SS, (w - inset) * SS - 1, (h - inset) * SS - 1], outline=255, width=border * SS)


def cut(im, w, h):
    return np.asarray(im.resize((w, h), Image.BOX)) >= 128


def question_mark(w, h, inset):
    """a rounded question mark: a thick hook, a stem and a round dot, with round ends"""
    im, d = canvas(w, h)
    frame(d, w, h, 2 if w < 60 else 3, inset)
    cx = w / 2
    r = min(w, h) * 0.22
    t = min(w, h) * 0.12                          # the thickness of the stroke
    top = h * 0.2
    # the hook: an arc from the left, over the top, to the right and down to the middle
    cy = top + r
    box = [(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS]
    d.arc(box, 180, 360 + 70, fill=255, width=int(t * SS))
    # the stem down to the dot
    import math
    ex = cx + r * math.cos(math.radians(70)); ey = cy + r * math.sin(math.radians(70))
    sx = cx; sy = cy + r + h * 0.1
    d.line([ex * SS, ey * SS, cx * SS, (cy + r + h * 0.02) * SS], fill=255, width=int(t * SS))
    d.line([cx * SS, (cy + r + h * 0.02) * SS, sx * SS, sy * SS], fill=255, width=int(t * SS))
    for (x, y) in ((ex, ey), (cx, sy)):
        d.ellipse([(x - t / 2) * SS, (y - t / 2) * SS, (x + t / 2) * SS, (y + t / 2) * SS], fill=255)
    d.ellipse([(cx - t * 0.8) * SS, (h * 0.82 - t * 0.8) * SS, (cx + t * 0.8) * SS, (h * 0.82 + t * 0.8) * SS], fill=255)
    d.ellipse([(cx - r - t / 2) * SS, (cy - t / 2) * SS, (cx - r + t / 2) * SS, (cy + t / 2) * SS], fill=255)
    return cut(im, w, h)


def profile(w, h, inset):
    """the profile of a lady looking to the right: hair in a bun, forehead, nose, lips, chin, a long neck, a bare shoulder: a silhouette with a few cut-outs (eye, lashes, mouth, the line of the hair)"""
    im, d = canvas(w, h)
    frame(d, w, h, 2 if w < 60 else 3, inset)
    s = min(w, h) / 100.0 * 0.96
    ox = (w - 100 * s) / 2 + 2 * s
    oy = (h - 100 * s) / 2 + 3 * s

    def P(pts):
        return [((ox + x * s) * SS, (oy + y * s) * SS) for x, y in pts]

    def E(x0, y0, x1, y1, fill):
        (a, b), (c, e) = P([(x0, y0), (x1, y1)])
        d.ellipse([a, b, c, e], fill=fill)
    face = [(52, 14), (63, 19), (67, 27), (68, 34), (66, 38), (74, 45), (72, 49), (70, 50), (71, 53), (68, 56), (70, 58), (68, 62), (67, 69), (62, 73), (58, 76), (58, 88),
            (74, 94), (90, 100), (14, 100), (30, 94), (38, 88), (38, 74), (30, 62), (22, 48), (20, 32), (26, 20), (38, 13)]
    d.polygon(P(face), fill=255)
    E(10, 4, 34, 28, 255)                                                   # the bun
    d.polygon(P([(36, 62), (30, 74), (34, 86), (40, 84), (40, 70)]), fill=255)   # a lock of hair on the neck
    E(58, 34, 64, 38, 0)                                                    # the eye
    d.line(P([(55, 32), (65, 31)]), fill=0, width=max(1, int(1.5 * s * SS)))        # the lashes
    d.line(P([(66, 55), (71, 55)]), fill=0, width=max(1, int(1.2 * s * SS)))        # the mouth
    d.line(P([(40, 20), (48, 12)]), fill=0, width=max(1, int(1.3 * s * SS)))       # the hair, a wave
    d.line(P([(44, 24), (47, 54)]), fill=0, width=max(1, int(1.3 * s * SS)))       # the hairline behind the ear
    return cut(im, w, h)


def xxxl_stack(w, h, inset):
    """XXXL under each other: four wide letters"""
    im, d = canvas(w, h)
    frame(d, w, h, 2 if w < 60 else 3, inset)
    f = ImageFont.truetype(IMPACT, 400)
    m = int((3 if w < 60 else 5) + inset)
    area_w, area_h = w - 2 * (m + 2), h - 2 * (m + 1)
    gap = 2 if w < 60 else 4
    rh = (area_h - 3 * gap) / 4.0
    for i, ch in enumerate('XXXL'):
        g = Image.new('L', (800, 700), 0)
        ImageDraw.Draw(g).text((50, 20), ch, font=f, fill=255)
        g = g.crop(g.getbbox()).resize((int(area_w * SS), int(rh * SS)), Image.LANCZOS)
        im.paste(g, (int((m + 2) * SS), int((m + 1 + i * (rh + gap)) * SS)), g)
    return cut(im, w, h)


def xxxl_block(w, h, inset):
    """XX over XL: a block of four big letters"""
    im, d = canvas(w, h)
    frame(d, w, h, 2 if w < 60 else 3, inset)
    f = ImageFont.truetype(IMPACT, 400)
    m = int((3 if w < 60 else 5) + inset)
    gap = 2 if w < 60 else 5
    cw, ch_ = (w - 2 * (m + 2) - gap) / 2.0, (h - 2 * (m + 2) - gap) / 2.0
    for i, c in enumerate('XXXL'):
        g = Image.new('L', (800, 700), 0)
        ImageDraw.Draw(g).text((50, 20), c, font=f, fill=255)
        g = g.crop(g.getbbox()).resize((int(cw * SS), int(ch_ * SS)), Image.LANCZOS)
        im.paste(g, (int((m + 2 + (i % 2) * (cw + gap)) * SS), int((m + 2 + (i // 2) * (ch_ + gap)) * SS)), g)
    return cut(im, w, h)


def render(mask, field):
    img = np.zeros(mask.shape + (3,), np.uint8)
    img[:] = field
    img[mask] = WHITE
    return img


DESIGNS = [('A  profile of a lady', profile), ('B  a nicer question mark', question_mark), ('C  XXXL under each other', xxxl_stack), ('D  XXXL in a block (XX / XL)', xxxl_block)]

if __name__ == '__main__':
    pad = 12
    zoom_small, zoom_big = 4, 2
    cell_w = 40 * zoom_small + pad
    big_w = 104 * zoom_big + pad
    row_h = max(40 * zoom_small, 80 * zoom_big) + 28
    cols = [('board card, blue', 40, 40, BLUE, zoom_small), ('board card, red', 40, 40, RED, zoom_small), ('choice screen, blue', 104, 80, BLUE, zoom_big), ('choice screen, red', 104, 80, RED, zoom_big)]
    W = sum((c[1] * c[4] + pad) for c in cols) + pad
    sheet = Image.new('RGB', (W, row_h * len(DESIGNS) + 30), (30, 30, 30))
    d = ImageDraw.Draw(sheet)
    x = pad
    for name, w, h, fld, z in cols:
        d.text((x, 6), name, fill=(220, 220, 220))
        x += w * z + pad
    for r, (title, fn) in enumerate(DESIGNS):
        x = pad
        y = 30 + r * row_h
        d.text((x, y), title, fill=(255, 230, 120))
        for name, w, h, fld, z in cols:
            inset = 0 if w == 40 else 2
            im = Image.fromarray(render(fn(w, h, inset), fld)).resize((w * z, h * z), Image.NEAREST)
            sheet.paste(im, (x, y + 14))
            x += w * z + pad
    sheet.save(os.path.join(OUT, 'proposals.png'))
    print('ok')
