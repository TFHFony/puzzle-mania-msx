"""Preview of a memory game (5 x 4 cards = 10 pairs) with the photos of Puzzle Mania in SCREEN 2 (2 colours per 8x1): MSX1 (TMS9918A palette) and MSX2 (one 16 colour
palette for all the photos).  Two layouts:  A = cards of 40 x 32 pixels on the character grid (5 x 4 characters), gaps of 8 pixels;
B = cards of 48 x 40 pixels (6 x 5 characters), gaps of 4 pixels (the card edges are not on the character grid: the colours of the cells at the edges are shared with the black gap).
Every layout is drawn with all cards face up and as a game in progress (some cards face down).
usage: python memory_preview.py [OUTDIR]"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(PROJ, 'tools')); sys.path.insert(0, r'F:\MSX Projects\Dev27\msx1-video-player\tools')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'preview')
PHOTOS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]                      # photo numbers (the 12 photos of the game: USED), 10 of them
LAYOUT = {'A': dict(cw=40, ch=32, gx=8, gy=16, x0=8, y0=16), 'B': dict(cw=48, ch=40, gx=4, gy=4, x0=0, y0=16)}
# a game in progress: which of the 20 cards are face up (the others show the back)
UP = {0, 1, 2, 7, 8, 13, 14, 16}
ORDER = [0, 5, 3, 8, 1, 7, 2, 9, 4, 6, 5, 2, 9, 0, 3, 6, 8, 1, 4, 7]      # a shuffle of the pairs over the 20 places


def cover(im, w, h):
    """the photo cut to the aspect of the card (the middle), then scaled"""
    W, H = im.size
    if W / H > w / h:
        nw = int(H * w / h); x = (W - nw) // 2; im = im.crop((x, 0, x + nw, H))
    else:
        nh = int(W * h / w); y = (H - nh) // 2; im = im.crop((0, y, W, y + nh))
    return im


def card_back(w, h):
    im = Image.new('RGB', (w, h), (40, 60, 200))
    d = ImageDraw.Draw(im)
    d.rectangle([1, 1, w - 2, h - 2], outline=(255, 255, 255), width=2)
    d.rectangle([5, 5, w - 6, h - 6], outline=(120, 150, 255), width=1)
    f = ImageFont.truetype(r'C:\Windows\Fonts\impact.ttf', int(h * 0.75))
    d.text((w // 2, h // 2 + 1), '?', font=f, fill=(255, 255, 255), anchor='mm')
    return im


def tiles(kind, lay):
    import build_game as B, palette_opt as PO
    from encode_clips import USED
    choices = json.load(open(os.path.join(PROJ, 'tools', 'choices.json')))
    res = []
    for p in PHOTOS:
        c = USED[p]
        src = Image.open(os.path.join(PROJ, 'work', 'stills', 'clip%02d_%d_src.png' % (c, choices[c]))).convert('RGB')
        src = B.lift(src) if kind == 1 else PO.adjust(src, **PO.LOOK_CLIP.get(c, PO.LOOK))
        res.append(B.thumbnail(cover(src, lay['cw'], lay['ch']), lay['cw'], lay['ch']))
    return res


def palette(tl, back):
    """one palette (colours 0 and 1 black) for the ten photos and the card back: k-means, then the search of tools/palette_opt.py on the mosaic"""
    import palette_opt as PO
    mos = np.concatenate([np.concatenate([np.asarray(t) for t in tl[:5]], axis=1), np.concatenate([np.asarray(t) for t in tl[5:]], axis=1)], axis=0)
    mos = np.concatenate([mos, np.concatenate([np.asarray(back)] * 5, axis=1)], axis=0)
    mos = np.pad(mos, ((0, -mos.shape[0] % 2), (0, -mos.shape[1] % 16), (0, 0)))         # (the search wants a width of 8 characters at half size)
    pal = PO.TMS.copy()
    pal[2:] = PO.kmeans_pal(mos, 14)
    pal[0] = pal[1] = (0, 0, 0)
    pal = PO.refine(PO.half(mos), pal, list(range(2, 16)), 4, lambda s: None)
    return PO.refine(mos, pal, list(range(2, 16)), 1, lambda s: None)


def screen(tl, back, lay, up_all, kind, pal):
    import build_game as B
    img = np.zeros((192, 256, 3), np.uint8)
    fix = np.ones((192, 256), np.int8)
    for k in range(20):
        r, c = divmod(k, 5)
        x = lay['x0'] + c * (lay['cw'] + lay['gx']); y = lay['y0'] + r * (lay['ch'] + lay['gy'])
        face = up_all or k in UP
        t = tl[ORDER[k]] if face else back
        img[y:y + lay['ch'], x:x + lay['cw']] = np.asarray(t)
        fix[y:y + lay['ch'], x:x + lay['cw']] = 0
    # the header: a line of text in white (the real game would draw it with its font)
    im = Image.fromarray(img); d = ImageDraw.Draw(im)
    d.text((8, 3), 'MEMORY    PAIRS 3/10   MOVES 17', fill=(255, 255, 255), font=ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 9))
    img = np.asarray(im)
    data, rend = B.coded(img, fix, pal)
    return rend


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for name, lay in LAYOUT.items():
        outs = {}
        for kind in (1, 2):                                  # 1 = MSX1, 2 = MSX2
            tl = tiles(kind, lay)
            back = card_back(lay['cw'], lay['ch'])
            pal = palette(tl, back) if kind == 2 else None
            outs[kind] = (screen(tl, back, lay, True, kind, pal), screen(tl, back, lay, False, kind, pal))
        for j, tag in enumerate(('faceup', 'game')):
            sh = Image.new('RGB', (768 * 2 + 16, 576), (30, 30, 30))
            sh.paste(Image.fromarray(outs[1][j]).resize((768, 576), Image.NEAREST), (0, 0))
            sh.paste(Image.fromarray(outs[2][j]).resize((768, 576), Image.NEAREST), (784, 0))
            sh.save(os.path.join(OUT, 'memory_%s_%s.png' % (name, tag)))
        print('layout', name, flush=True)
