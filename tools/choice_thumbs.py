"""The thumbnails of the choice screen for an MSX2 (104 x 80 pixels, a black border of 2 pixels, like the thumbnails of the menu) coded for a palette of their own: the palette of the menu
(tools/palette_opt.py 'menu') in which ONE colour is blue, so that the card of the memory game can be a real blue card (the menu palette has no blue).  The colour that is replaced is
one that the logo and the footer of the menu do not use (they use 1, 3, 8, 9, 10, 11, 13, 14, 15) and that costs the thumbnails the least.
  build() -> dict(banks = 12 banks (the thumbnail of photo p at the start of bank p: pattern bytes 1040, then colour bytes 1040), pal = 32 bytes V9938, x = the blue colour)"""
import os, sys, json, pickle
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, r'F:\MSX Projects\Dev27\msx1-video-player\tools')
CAND = (2, 4, 5, 6, 7, 12)
CACHE = os.path.join(PROJ, 'work', 'choice_thumbs.pkl')


def sources():
    import palette_opt as PO
    from encode_clips import USED
    choices = json.load(open(os.path.join(HERE, 'choices.json')))
    out = []
    for c in USED:
        src = Image.open(os.path.join(PROJ, 'work', 'stills', 'clip%02d_%d_src.png' % (c, choices[c]))).convert('RGB')
        out.append(PO.adjust(src, **PO.LOOK_CLIP.get(c, PO.LOOK)))
    return out


def thumb(src):
    import build_game as B
    th = Image.new('RGB', (104, 80)); th.paste(B.thumbnail(src, 100, 76), (2, 2))
    tf = np.ones((80, 104), np.int8); tf[2:78, 2:102] = 0
    return th, tf


def build():
    import build_game as B, palette_opt as PO, stills
    key = (os.path.getmtime(__file__), os.path.getmtime(PO.PJSON), os.path.getmtime(os.path.join(HERE, 'stills.py')))
    if os.path.exists(CACHE):
        k, res = pickle.load(open(CACHE, 'rb'))
        if k == key:
            return res
    pj = PO.load()
    menu = np.array(pj['menu'], np.float32)
    srcs = [thumb(s) for s in sources()]
    best = None
    for x in CAND:
        pal = menu.copy(); pal[x] = PO.TMS[4]
        sc = 0.0
        for th, tf in srcs:
            _, _, rend = stills.encode(np.asarray(th, np.float32), tf, pal)
            sc += PO.P.blurred_psnr(np.asarray(th, np.float32), np.clip(rend, 0, 255))
        print('blue = colour', x, 'mean PSNR %.2f dB' % (sc / len(srcs)), flush=True)
        if best is None or sc > best[0]:
            best = (sc, x, pal)
    _, x, pal = best
    banks = []
    for th, tf in srcs:
        data, rend = B.coded(th, tf, pal)
        banks.append(data + bytes([0xFF]) * (16384 - len(data)))
    res = dict(banks=banks, pal=PO.to_v9938(pal), x=x)
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    pickle.dump((key, res), open(CACHE, 'wb'))
    return res


if __name__ == '__main__':
    r = build()
    print('blue colour', r['x'], len(r['banks']), 'banks', r['pal'].hex())
