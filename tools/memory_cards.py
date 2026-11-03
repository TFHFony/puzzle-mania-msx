"""The cards of the memory game (game/memplay.asm): 12 photo cards and the back of a card, 40 x 40 pixels = 5 x 5 characters, coded for SCREEN 2 (2 colours per 8x1):
a card = 5 rows of 40 pattern bytes, then 5 rows of 40 colour bytes (400 bytes; one character row of the card is 5 characters = 40 contiguous bytes in the VRAM).
 MSX1: the photos for the TMS9918A palette; MSX2: for one palette of 16 colours for all the cards (colours 0 and 1 black, 4 = the blue of the card back, 3 / 9 (cursor), 14 / 15 (text) as in the TMS9918A; the other 9 are
 optimised on the mosaic of the photos).  The back of the card is drawn with exactly two colours (blue 4 and white 15), not coded: no dither, no colour spill.
  build() -> dict(data = 2 x 13 cards (MSX1 photos 0..11 + back, MSX2 photos 0..11 + back), pal = 32 bytes V9938 of the MSX2 palette, previews in work/preview/memory_*.png)"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, r'F:\MSX Projects\Dev27\msx1-video-player\tools')
CW = CH = 40
BLUE, WHITE = 4, 15
KEEP = (3, 9, 14, 15)                            # the colours of the cursor (flashing, as everywhere in the game) and of the bold text (grey, white): as the TMS9918A has them
FREE = [2, 5, 6, 7, 8, 10, 11, 12, 13]
PALJ = os.path.join(HERE, 'memory_palette.json')


def cover(im, w, h):
    W, H = im.size
    if W / H > w / h:
        nw = int(H * w / h); x = (W - nw) // 2; im = im.crop((x, 0, x + nw, H))
    else:
        nh = int(W * h / w); y = (H - nh) // 2; im = im.crop((0, y, W, y + nh))
    return im


def sources():
    from encode_clips import USED
    choices = json.load(open(os.path.join(HERE, 'choices.json')))
    return [Image.open(os.path.join(PROJ, 'work', 'stills', 'clip%02d_%d_src.png' % (c, choices[c]))).convert('RGB') for c in USED]


def thumbs(kind):
    """the 12 photos as 40 x 40 images: kind 1 = for the TMS9918A (lifted), 2 = for the MSX2 (the look of the MSX2 photos)"""
    import build_game as B, palette_opt as PO
    from encode_clips import USED
    out = []
    for c, src in zip(USED, sources()):
        s = B.lift(src) if kind == 1 else PO.adjust(src, **PO.LOOK_CLIP.get(c, PO.LOOK))
        out.append(B.thumbnail(cover(s, CW, CH), CW, CH))
    return out


def palette(tl):
    import palette_opt as PO
    mos = np.concatenate([np.concatenate([np.asarray(t) for t in tl[r * 4:(r + 1) * 4]], axis=1) for r in range(3)], axis=0)         # 4 x 3 photos
    mos = np.pad(mos, ((0, 0), (0, -mos.shape[1] % 16), (0, 0)))
    pal = PO.TMS.copy()
    pal[0] = pal[1] = (0, 0, 0)
    pal[FREE] = PO.kmeans_pal(mos, len(FREE))
    pal = PO.refine(PO.half(mos), pal, FREE, 4, lambda s: None)
    pal = PO.refine(mos, pal, FREE, 1, lambda s: None)
    pal[0] = pal[1] = (0, 0, 0); pal[BLUE] = PO.TMS[BLUE]
    for k in KEEP:
        pal[k] = PO.TMS[k]
    return pal


def back_mask():
    """the back of a card: a white frame and a white question mark on blue (two colours only); the question mark is centred on its ink"""
    im = Image.new('L', (CW, CH), 0)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, CW - 1, CH - 1], outline=255, width=2)
    f = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 40)
    x0, y0, x1, y1 = d.textbbox((0, 0), '?', font=f)
    d.text(((CW - (x1 - x0)) // 2 - x0, (CH - (y1 - y0)) // 2 - y0), '?', font=f, fill=255)
    return np.asarray(im) >= 128


BIGW, BIGH = 104, 80
BIG_BLUE = (4, 5)                                # the blue of the big card: MSX1 colour 4 (the blue of the cards), MSX2 colour 5 of the menu palette (steel blue; the menu palette has no other blue)


def big_card(blue):
    """the card of the memory game on the choice screen (104 x 80 pixels = 13 x 10 characters, 2080 bytes), as big as the photo next to it (100 x 76 with a black margin of two pixels):
    a blue card with a white frame and a white question mark; the characters at the edge hold black and blue only, the others blue and white"""
    import build_game as B
    im = Image.new('L', (BIGW, BIGH), 0)
    d = ImageDraw.Draw(im)
    d.rectangle([8, 8, BIGW - 9, BIGH - 9], outline=255, width=3)
    f = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 58)
    x0, y0, x1, y1 = d.textbbox((0, 0), '?', font=f)
    d.text(((BIGW - (x1 - x0)) // 2 - x0, (BIGH - (y1 - y0)) // 2 - y0), '?', font=f, fill=255)
    white = np.asarray(im) >= 128
    card = np.zeros((BIGH, BIGW), bool)
    card[2:BIGH - 2, 2:BIGW - 2] = True                      # the blue card (100 x 76)
    pat = np.zeros((BIGH, BIGW // 8), np.uint8)
    col = np.zeros((BIGH, BIGW // 8), np.uint8)
    for y in range(BIGH):
        for cx in range(BIGW // 8):
            sl = slice(cx * 8, cx * 8 + 8)
            w, c = white[y, sl] & card[y, sl], card[y, sl]
            if w.any():                                      # white on blue (a white pixel can sit in a character at the edge only inside the card)
                assert c.all(), (y, cx)
                fg, bg, bits = WHITE, blue, w
            elif c.all():
                fg, bg, bits = blue, blue, np.zeros(8, bool)
            elif c.any():                                    # the edge: blue on black
                fg, bg, bits = blue, 1, c
            else:
                fg, bg, bits = 1, 1, np.zeros(8, bool)
            pat[y, cx] = int(sum(1 << (7 - i) for i in range(8) if bits[i]))
            col[y, cx] = (fg << 4) | bg
    return B.chars(pat) + B.chars(col)


def card_bytes(pat, col):
    import build_game as B
    return B.chars(pat) + B.chars(col)


def back_card():
    m = back_mask()
    pat = (m.reshape(CH, CW // 8, 8).astype(np.uint8) << (7 - np.arange(8, dtype=np.uint8))).sum(-1).astype(np.uint8)
    col = np.full(pat.shape, (WHITE << 4) | BLUE, np.uint8)
    rend = np.zeros((CH, CW, 3), np.uint8)
    return card_bytes(pat, col), m


def build(blue_msx2=5):
    import palette_opt as PO, stills
    t1 = thumbs(1); t2 = thumbs(2)
    if os.path.exists(PALJ) and os.path.getmtime(PALJ) > os.path.getmtime(__file__):
        pal = np.array(json.load(open(PALJ)), np.float32)
    else:
        pal = palette(t2)
        json.dump(pal.tolist(), open(PALJ, 'w'))
    bk, m = back_card()
    data = b''
    prev = os.path.join(PROJ, 'work', 'preview'); os.makedirs(prev, exist_ok=True)
    rends = {}
    for kind, tl, pl in ((1, t1, None), (2, t2, pal)):
        rs = []
        for t in tl:
            pat, col, rend = stills.encode(np.asarray(t, np.float32), None, pl)
            data += card_bytes(pat, col); rs.append(rend)
        data += bk
        rends[kind] = rs
    for kind in (1, 2):
        pl = pal if kind == 2 else PO.TMS
        sh = Image.new('RGB', (4 * 44 * 3, 4 * 44 * 3))
        for k, r in enumerate(rends[kind] + [np.where(m[..., None], pl[WHITE], pl[BLUE]).astype(np.uint8)]):
            sh.paste(Image.fromarray(np.asarray(r, np.uint8)).resize((120, 120), Image.NEAREST), ((k % 4) * 132, (k // 4) * 132))
        sh.save(os.path.join(prev, 'memory_cards_msx%d.png' % kind))
    data += big_card(BIG_BLUE[0]) + big_card(blue_msx2)         # the cards of the choice screen: MSX1, MSX2
    assert len(data) == 2 * 13 * 400 + 2 * 2080
    return dict(data=data, pal=PO.to_v9938(pal))


if __name__ == '__main__':
    r = build()
    print(len(r['data']), 'bytes', r['pal'].hex())
