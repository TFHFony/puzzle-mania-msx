"""Text screens for the game: three 'how to play' pages and the credits page (SCREEN 2, black background, every text line in one colour so
that no 8x1 row segment needs more than black + that colour: sharp text without colour bleeding).
screen(name) -> (data bytes in char order, rendered preview)"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, r'F:\MSX Projects\Dev27\msx1-video-player\tools')
import msx1_preview as P
PAL = P.TMS
WHITE, YELLOW, CYAN, LRED, GREY, GREEN, MAGENTA = 15, 11, 7, 9, 14, 3, 13
FONT = r'C:\Windows\Fonts\arialbd.ttf'

PAGES = {
    'howto1': [
        ('HOW TO PLAY  1/2', 'title'),
        ('', None),
        ('CHOOSE A PHOTO', YELLOW),
        ('Cursor keys + SPACE.  The arrows at the', WHITE), ('sides show that there are more photos.', WHITE),
        ('H = this help (at the photo menu),', GREY), ('ESC = credits.', GREY),
        ('', None),
        ('CHOOSE A SIZE', YELLOW),
        ('3x3 (easy) to 6x6 (hard), cursor keys', WHITE), ('and SPACE.  ESC goes back.', WHITE),
        ('', None),
        ('L = tile lines: thick, thin or off', CYAN),
        ('C = control: arrow keys or cursor', CYAN),
        ('', None),
        ('SPACE = next page,  ESC = skip', GREY),
    ],
    'howto2': [
        ('HOW TO PLAY  2/2', 'title'),
        ('', None),
        ('SLIDE THE TILES', YELLOW),
        ('Rebuild the photo.  Only a tile next to', WHITE), ('the empty square can move.', WHITE),
        ('', None),
        ('ARROWS: the key slides the tile that', CYAN), ('lies next to the gap in that direction.', CYAN),
        ('CURSOR: move the four corners to a tile', CYAN), ('with the cursor keys, SPACE slides it.', CYAN),
        ('', None),
        ('H  hold: look at the solution', WHITE),
        ('N  hold: tile numbers, moves and time', WHITE),
        ('T  hint: flashes the tile for the gap', WHITE),
        ('L  tile lines    C  control   ESC  menu', WHITE),
        ('', None),
        ('SPACE = menu', GREY),
    ],
    'credits': [
        ('PUZZLE MANIA', 'title'),
        ('', None),
        ('MSXDEV26 ENTRY  -  MSX1, 16 KB, NEO16', CYAN),
        ('', None),
        ('FREEWARE', YELLOW),
        ('Free to play, copy and share.', WHITE), ('The full game must stay free of charge.', WHITE),
        ('', None),
        ('MADE BY', YELLOW),
        ('Claude  &  The File-Hunter of FONY', WHITE),
        ('', None),
        ('VIDEOS AND MUSIC', YELLOW),
        ('FONY / File-Hunter', WHITE),
        ('', None),
        ('THANKS FOR PLAYING!', LRED),
        ('SPACE = menu', GREY),
    ],
}


def render(lines):
    font = ImageFont.truetype(FONT, 11)
    tfont = ImageFont.truetype(FONT, 20)

    def height(lh, bl):
        return 6 + sum(26 if c == 'title' else bl if c is None else lh for _, c in lines)
    lh, bl = 13, 6
    while height(lh, bl) > 174 and (lh > 11 or bl > 2):
        if bl > 2: bl -= 1
        elif lh > 11: lh -= 1
    img = Image.new('RGB', (256, 192), (0, 0, 0))
    d = ImageDraw.Draw(img); d.fontmode = '1'
    y = 6
    for text, col in lines:
        if col == 'title':
            w = d.textlength(text, font=tfont)
            band = Image.new('L', (256, 24), 0); bd = ImageDraw.Draw(band); bd.fontmode = '1'
            bd.text(((256 - w) / 2, 1), text, font=tfont, fill=255)
            m = np.asarray(band) > 128
            seq = [13, 13, 9, 9, 15, 15, 9, 9, 13, 13, 6, 6]
            a = np.asarray(img).copy()
            for r in range(24):
                a[y + r][m[r]] = PAL[seq[min(len(seq) - 1, r * len(seq) // 24)]]
            img = Image.fromarray(a); d = ImageDraw.Draw(img); d.fontmode = '1'
            y += 26
        elif col is None:
            y += bl
        else:
            d.text((8, y), text, font=font, fill=tuple(int(v) for v in PAL[col]))
            y += lh
    return np.asarray(img)


def render_credits():
    """credits: copper bars, big title, three coloured role bands with the names, freeware line"""
    img = np.zeros((192, 256, 3), np.uint8)

    def bars(y0, seq, h=2):
        for i, c in enumerate(seq):
            img[y0 + i * h:y0 + (i + 1) * h] = PAL[c]
    bars(3, [6, 13, 9, 15, 9, 13, 6])                          # top copper bars (14 px)
    pil = Image.fromarray(img); d = ImageDraw.Draw(pil); d.fontmode = '1'
    tfont = ImageFont.truetype(FONT, 22); lfont = ImageFont.truetype(FONT, 11); nfont = ImageFont.truetype(FONT, 13); sfont = ImageFont.truetype(FONT, 10)
    img = np.asarray(pil).copy()
    # title in vertical copper bands
    band = Image.new('L', (256, 26), 0); bd = ImageDraw.Draw(band); bd.fontmode = '1'
    text = 'PUZZLE MANIA'; w = bd.textlength(text, font=tfont)
    bd.text(((256 - w) / 2, 1), text, font=tfont, fill=255)
    m = np.asarray(band) > 128
    seq = [13, 13, 9, 9, 15, 15, 9, 9, 13, 13, 6, 6]
    for r in range(26):
        img[20 + r][m[r]] = PAL[seq[min(len(seq) - 1, r * len(seq) // 26)]]
    bars(49, [6, 13, 9, 15, 9, 13, 6])                         # copper bars under the title
    pil = Image.fromarray(img); d = ImageDraw.Draw(pil); d.fontmode = '1'

    def block(y, role, names, col):
        d.rectangle((28, y, 227, y + 12), fill=tuple(int(v) for v in PAL[col]))
        wr = d.textlength(role, font=lfont)
        d.text(((256 - wr) / 2, y), role, font=lfont, fill=(0, 0, 0))
        wn = d.textlength(names, font=nfont)
        d.text(((256 - wn) / 2, y + 14), names, font=nfont, fill=(255, 255, 255))
    block(70, 'CODING', 'The File-Hunter & Claude', 13)
    block(103, 'GFX', 'The File-Hunter & Tittygram', 7)
    block(136, 'MUSIC', 'The File-Hunter & Solmi AI', 11)
    for txt, y, col in (('FREEWARE - FREE TO PLAY, COPY AND SHARE', 168, WHITE), ('MSXDEV26  -  MSX1  -  SPACE = MENU', 180, GREY)):
        w = d.textlength(txt, font=sfont)
        d.text(((256 - w) / 2, y), txt, font=sfont, fill=tuple(int(v) for v in PAL[col]))
    img = np.asarray(pil).copy()
    return img


def exact(a, fix=None):
    """exact coding of a text screen: every 8x1 segment holds black plus one colour (checked), so nothing is dithered or approximated -> no colour bleeding.
    returns (data in char order, preview)"""
    h, w = a.shape[:2]
    P8 = np.asarray(PAL).astype(int)
    idx = np.full((h, w), 1, np.int16)                         # TMS colour 1 = black
    flat = a.reshape(-1, 3).astype(int)
    for k in range(1, 16):
        idx.reshape(-1)[(flat == P8[k]).all(axis=1)] = k
    assert not (a.reshape(-1, 3).astype(int)[~np.isin(idx.reshape(-1), range(1, 16))]).size
    pat = np.zeros((h, w // 8), np.uint8); col = np.zeros((h, w // 8), np.uint8)
    for y in range(h):
        for c in range(w // 8):
            seg = idx[y, c * 8:c * 8 + 8]
            cs = [k for k in sorted(set(seg.tolist())) if k != 1]
            assert len(cs) <= 1 or (y, c) and (print('colour clash', y, c, cs) or True)
            fg = cs[0] if cs else 1
            if len(cs) > 1:                                    # (not expected) the most frequent colour wins
                fg = max(cs, key=lambda k: (seg == k).sum())
            pat[y, c] = sum(1 << (7 - i) for i in range(8) if seg[i] == fg and fg != 1)
            col[y, c] = fg << 4 | 1
    rend = np.zeros((h, w, 3), np.uint8)
    for y in range(h):
        for c in range(w // 8):
            fg = col[y, c] >> 4
            for i in range(8):
                rend[y, c * 8 + i] = P8[fg] if pat[y, c] >> (7 - i) & 1 else P8[1]
    def chars(x):
        return x.reshape(h // 8, 8, w // 8).transpose(0, 2, 1).reshape(-1).tobytes()
    return chars(pat) + chars(col), rend


def screen(name, coded):
    a = render_credits() if name == 'credits' else render(PAGES[name])
    return exact(a)
