"""FONY logo -> SCREEN 2 (15 colours, 2 per 8x1 row), background exactly black (no colour bleeding at the edges).
The logo is an outline-only lettering (black body); every row of the outline gets ONE colour (horizontal colour bands), so a row segment
never needs more than black + one colour.  Centred on the screen.
usage: fony_logo.py [logo.png = assets/fony_logo.png]   -> Screenshots/fony/fony_<variant>.png (x3 preview), work/fony_<variant>.bin (12288 bytes: patterns, colours in char order)"""
import os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_game as B
import msx1_preview as P
PAL = P.TMS
src = Image.open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(B.PROJ, 'assets', 'fony_logo.png')).convert('RGB')
a = np.asarray(src)
ys, xs = np.nonzero(a.max(-1) > 24)
logo = src.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
out = os.path.join(B.PROJ, 'Screenshots', 'fony2'); os.makedirs(out, exist_ok=True)


def make(name, seq, width=248):
    h = round(logo.height * width / logo.width)
    m = np.asarray(logo.resize((width, h), Image.LANCZOS)).max(-1) > 70          # outline pixels
    img = np.zeros((192, 256, 3), np.uint8)
    x0 = (256 - width) // 2
    top = (192 - h) // 2
    for y in range(h):
        k = min(len(seq) - 1, y * len(seq) // h)
        img[top + y, x0:x0 + width][m[y]] = PAL[seq[k]]
    fix = (img.max(-1) == 0).astype(np.int8)
    data, rend = B.coded(img, fix)
    Image.fromarray(rend).resize((768, 576), Image.NEAREST).save(os.path.join(out, 'fony_%s.png' % name))
    open(os.path.join(B.PROJ, 'work', 'fony_%s.bin' % name), 'wb').write(data)
    print(name, 'logo', width, 'x', h, flush=True)


make('copper', [13, 13, 13, 9, 9, 9, 15, 15, 9, 9, 13, 13, 6, 6, 6])
