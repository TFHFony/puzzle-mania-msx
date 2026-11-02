"""Proposals for the full-screen XXXL logo (shown after the jigsaw outro, a few seconds, no sound): the photo of the Oops clip (the puzzle photo, clip 6) and big letters.
usage: python xxxl.py [A B C D]   -> proposals/{A,B,C,D}_{src,msx1,msx2}.png and proposals/sheet.png
Each design is drawn at 4x, text layers keep their own masks: white / black text pixels are fixed in the coding (crisp edges), the photo is coded freely (2 colours per 8x1)."""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(PROJ, 'tools')); sys.path.insert(0, r'F:\MSX Projects\Dev27\msx1-video-player\tools')
OUT = os.path.join(HERE, 'proposals')
os.makedirs(OUT, exist_ok=True)
W, H, S = 256, 192, 4
IMPACT = r'C:\Windows\Fonts\impact.ttf'
RED = (211, 92, 84); YEL = (225, 212, 140); WHT = (255, 255, 255); BLK = (0, 0, 0); BLU = (83, 102, 215)


def font(size):
    return ImageFont.truetype(IMPACT, int(size))


def fit(text, w, h):
    """the Impact size at which the text is at most w x h (in 4x pixels)"""
    lo, hi = 8, 900
    while lo < hi:
        mid = (lo + hi + 1) // 2
        b = ImageDraw.Draw(Image.new('L', (4, 4))).textbbox((0, 0), text, font=font(mid))
        if b[2] - b[0] <= w and b[3] - b[1] <= h:
            lo = mid
        else:
            hi = mid - 1
    return lo


class Canvas:
    def __init__(self, base=None):
        self.im = Image.new('RGB', (W * S, H * S), BLK) if base is None else base.resize((W * S, H * S), Image.LANCZOS)
        self.wm = Image.new('L', (W * S, H * S), 0)       # pixels that must be white
        self.bm = Image.new('L', (W * S, H * S), 0)       # pixels that must be black

    def text(self, txt, box, fill=WHT, outline=4, shadow=None, photo=None, angle=0):
        """text fitted into box = (x0, y0, x1, y1) in 1x pixels; outline in 1x pixels (black, fixed); shadow = (dx, dy, colour); photo = an image the letters are filled with"""
        x0, y0, x1, y1 = [v * S for v in box]
        size = fit(txt, x1 - x0 - 2 * outline * S, y1 - y0 - 2 * outline * S)
        f = font(size)
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        bb = ImageDraw.Draw(Image.new('L', (4, 4))).textbbox((0, 0), txt, font=f, anchor='mm')      # the middle of the ink, not of the line
        cx -= (bb[0] + bb[2]) // 2
        cy -= (bb[1] + bb[3]) // 2
        d = ImageDraw.Draw(self.im)
        if shadow:
            d.text((cx + shadow[0] * S, cy + shadow[1] * S), txt, font=f, fill=shadow[2], anchor='mm', stroke_width=outline * S, stroke_fill=shadow[2])
        d.text((cx, cy), txt, font=f, fill=BLK, anchor='mm', stroke_width=outline * S, stroke_fill=BLK)
        ImageDraw.Draw(self.bm).text((cx, cy), txt, font=f, fill=255, anchor='mm', stroke_width=outline * S, stroke_fill=255)
        m = Image.new('L', self.im.size, 0)
        ImageDraw.Draw(m).text((cx, cy), txt, font=f, fill=255, anchor='mm')
        if photo is not None:
            self.im.paste(photo.resize(self.im.size, Image.LANCZOS), (0, 0), m)
            self.bm.paste(0, (0, 0), m)                   # (the letters themselves are free: the photo)
        else:
            self.im.paste(Image.new('RGB', self.im.size, fill), (0, 0), m)
            self.bm.paste(0, (0, 0), m)
            if fill == WHT:
                self.wm.paste(255, (0, 0), m)

    def flat(self):
        """-> (rgb 1x, fix 1x): fix 1 = black, 2 = white"""
        rgb = np.asarray(self.im.resize((W, H), Image.BOX))
        wm = np.asarray(self.wm.resize((W, H), Image.BOX)) > 240
        bm = np.asarray(self.bm.resize((W, H), Image.BOX)) > 240
        fix = np.zeros((H, W), np.int8)
        fix[bm] = 1
        fix[wm] = 2
        return rgb, fix


def cover(photo, dark_top=0.0, dark_bottom=0.0):
    ph = photo.resize((W * S, H * S), Image.LANCZOS)
    a = np.asarray(ph, np.float32)
    y = np.linspace(0, 1, H * S)[:, None, None]
    g = 1 - dark_top * np.clip(1 - y / 0.35, 0, 1) - dark_bottom * np.clip((y - 0.55) / 0.45, 0, 1)
    return Image.fromarray(np.clip(a * g, 0, 255).astype(np.uint8))


def design_A(photo):                           # poster: the whole photo, PUZZLE MANIA on top, a huge XXXL at the bottom
    c = Canvas(cover(photo, 0.55, 0.65))
    c.text('PUZZLE MANIA', (8, 6, 248, 46), WHT, outline=3)
    c.text('XXXL', (6, 96, 250, 186), WHT, outline=4, shadow=(3, 3, RED))
    return c


def design_B(photo):                           # the photo inside giant letters, like the title: black background
    c = Canvas()
    c.text('PUZZLE MANIA', (10, 4, 246, 36), WHT, outline=2)
    c.text('XXXL', (4, 40, 252, 188), WHT, outline=3, shadow=(4, 4, RED), photo=photo)
    return c


def design_C(photo):                           # four jigsaw tiles, one letter each, on the dimmed photo
    c = Canvas(cover(photo, 0.0, 0.0))
    c.im = Image.fromarray((np.asarray(c.im, np.float32) * 0.45).astype(np.uint8))
    d = ImageDraw.Draw(c.im)
    cols = [RED, YEL, BLU, RED]
    for k, ch in enumerate('XXXL'):
        x0 = 8 + k * 61
        y0 = 96
        d.rectangle([x0 * S, y0 * S, (x0 + 52) * S, (y0 + 80) * S], fill=cols[k], outline=WHT, width=2 * S)
        if k < 3:
            d.ellipse([(x0 + 48) * S, (y0 + 28) * S, (x0 + 66) * S, (y0 + 46) * S], fill=cols[k], outline=WHT, width=2 * S)
            d.rectangle([(x0 + 46) * S, (y0 + 31) * S, (x0 + 54) * S, (y0 + 43) * S], fill=cols[k])
        c.text(ch, (x0 + 6, y0 + 8, x0 + 46, y0 + 72), WHT, outline=2)
    c.text('PUZZLE MANIA', (8, 8, 248, 48), WHT, outline=3)
    return c


def design_D(photo):                           # magazine cover: the photo in a white frame, PUZZLE MANIA above it, a red XXXL below
    c = Canvas()
    c.text('PUZZLE MANIA', (8, 2, 248, 36), WHT, outline=2)
    x0, y0, x1, y1 = 40, 40, 216, 126
    ph = photo.resize(((x1 - x0) * S, (y1 - y0) * S), Image.LANCZOS)
    c.im.paste(Image.new('RGB', ((x1 - x0 + 8) * S, (y1 - y0 + 8) * S), WHT), ((x0 - 4) * S, (y0 - 4) * S))
    c.wm.paste(255, ((x0 - 4) * S, (y0 - 4) * S, (x1 + 4) * S, (y1 + 4) * S))
    c.im.paste(ph, (x0 * S, y0 * S))
    c.wm.paste(0, (x0 * S, y0 * S, x1 * S, y1 * S))
    c.text("XXXL", (8, 132, 248, 190), RED, outline=2, shadow=(2, 2, WHT))
    return c


def code(img, fix, pal):
    import build_game as B
    return B.coded(img, fix, pal)[1]


if __name__ == '__main__':
    import build_game as B, palette_opt as PO
    from encode_clips import USED
    choices = json.load(open(os.path.join(PROJ, 'tools', 'choices.json')))
    src = Image.open(os.path.join(PROJ, 'work', 'stills', 'clip06_%d_src.png' % choices[6])).convert('RGB')
    pj = PO.load()
    pal2 = np.array(pj['photo'][USED.index(6)], np.float32)
    ph1 = B.lift(src)
    ph2 = PO.adjust(src, **PO.LOOK_CLIP.get(6, PO.LOOK))
    names = sys.argv[1:] or ['A', 'B', 'C', 'D']
    for n in names:
        fn = globals()['design_' + n]
        for tag, ph, pal in (('msx1', ph1, None), ('msx2', ph2, pal2)):
            rgb, fix = fn(ph).flat()
            Image.fromarray(rgb).save(os.path.join(OUT, '%s_src_%s.png' % (n, tag)))
            Image.fromarray(code(rgb, fix, pal)).save(os.path.join(OUT, '%s_%s.png' % (n, tag)))
        print('design', n, flush=True)
    sh = Image.new('RGB', (W * 2 * 2, H * 2 * len(names)))
    for k, n in enumerate(names):
        for j, tag in enumerate(('msx1', 'msx2')):
            sh.paste(Image.open(os.path.join(OUT, '%s_%s.png' % (n, tag))).resize((W * 2, H * 2), Image.NEAREST), (j * W * 2, k * H * 2))
    sh.save(os.path.join(OUT, 'sheet.png'))
