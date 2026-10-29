"""The PUZZLE MANIA XXXL logo above the photo menu: 256 x 16 pixels (tile rows 0..1, the free space above the thumbnails), at most two colours per 8 pixel cell (no colour bleed).
python tools/menu_logo.py  writes assets/menu_logo.png (needs Arial Black); logo_bytes() turns the picture into pattern + colour bytes for build_game.py."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
PNG = os.path.join(PROJ, 'assets', 'menu_logo.png')
BLK, CRM, RED, WHT = (0, 7, 0), (225, 212, 140), (211, 92, 84), (247, 255, 248)
IDX = {BLK: 1, CRM: 11, RED: 8, WHT: 15}                     # TMS9918 colour numbers
X0, XP, PW, Y = 23, 176, 56, 2                                 # text start, red plate (on a cell edge), plate width, top of the letters


def make():
    f = None
    for sz in range(6, 40):
        ft = ImageFont.truetype('C:/Windows/Fonts/ariblk.ttf', sz)
        b = ft.getbbox('H')
        if b[3] - b[1] > 12:
            break
        f = ft
    a = np.zeros((16, 256, 3), 'uint8'); a[:] = BLK
    a[Y - 2:Y + 14, XP:XP + PW] = RED
    for t, x, col in (('PUZZLE MANIA', X0, CRM), ('XXXL', XP + (PW - int(f.getlength('XXXL'))) // 2, WHT)):
        m = Image.new('1', (256, 16), 0); d = ImageDraw.Draw(m); d.fontmode = '1'
        d.text((x, Y - f.getbbox('H')[1]), t, font=f, fill=1)
        a[np.array(m)] = col
    Image.fromarray(a).save(PNG)


def logo_bytes():
    """-> (pattern, colour): two halves (tile columns 2..15 and 16..29), each 2 rows of 14 tiles; per half the pattern bytes, then the colour bytes"""
    a = np.array(Image.open(PNG).convert('RGB'))
    out = []
    for c0 in (2, 16):
        pat = bytearray(); col = bytearray()
        for r in range(2):
            for c in range(c0, c0 + 14):
                for y in range(8):
                    px = [IDX[tuple(p)] for p in a[r * 8 + y, c * 8:c * 8 + 8]]
                    cs = sorted(set(px), key=lambda k: (k == 1, -k))   # the foreground first: black is the background
                    assert len(cs) <= 2, (r, c, y, cs)
                    fg = cs[0]; bg = cs[1] if len(cs) > 1 else 1
                    if len(cs) == 1 and fg == 1:
                        fg = 1
                    pat.append(sum(1 << (7 - i) for i, v in enumerate(px) if v == fg and fg != bg))
                    col.append(fg << 4 | bg)
        out.append(bytes(pat) + bytes(col))
    return b''.join(out)


if __name__ == '__main__':
    make()
    print(len(logo_bytes()), 'bytes')
