"""The XXXL screen after the jigsaw outro of the title: only the four letters XXXL, as high as the screen, filled with the photo of the Oops clip (clip 6, the puzzle photo), black around them.
The same drawing and coding as the title (build_game.welcome_image).  banks(choices, msx2) -> (bank for the TMS palette, bank for the palette of the photo)"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, r'F:\MSX Projects\Dev27\msx1-video-player\tools')
PHOTO_CLIP = 6


def letters_mask(word='XXXL', box=(5, 5, 251, 187), gap=45):
    """256x192 bool: the letters of the word in Impact, stretched to the box (one height and baseline for all letters)"""
    font = ImageFont.truetype(r'C:\Windows\Fonts\impact.ttf', 400)
    full = []
    for ch in word:
        g = Image.new('L', (800, 700), 0)
        ImageDraw.Draw(g).text((50, 20), ch, font=font, fill=255)
        full.append(g)
    ytop = min(g.getbbox()[1] for g in full); ybot = max(g.getbbox()[3] for g in full)
    glyphs = [g.crop((g.getbbox()[0], ytop, g.getbbox()[2], ybot)) for g in full]
    big = Image.new('L', (sum(g.width for g in glyphs) + gap * (len(glyphs) - 1), ybot - ytop), 0)
    x = 0
    for g in glyphs:
        big.paste(g, (x, 0)); x += g.width + gap
    mask = Image.new('L', (256, 192), 0)
    mask.paste(big.resize((box[2] - box[0], box[3] - box[1]), Image.LANCZOS), (box[0], box[1]))
    return np.asarray(mask) >= 128


def banks(choices, msx2):
    import build_game as B, palette_opt as PO
    from encode_clips import USED
    src = Image.open(os.path.join(PROJ, 'work', 'stills', 'clip%02d_%d_src.png' % (PHOTO_CLIP, choices[PHOTO_CLIP]))).convert('RGB')
    m = letters_mask()
    out = []
    for ph, pal in ((B.lift(src), None), (PO.adjust(src, **PO.LOOK_CLIP.get(PHOTO_CLIP, PO.LOOK)), np.array(PO.load()['photo'][USED.index(PHOTO_CLIP)], np.float32) if msx2 else None)):
        photo = np.asarray(ph)
        img = np.zeros((192, 256, 3), np.uint8)
        img[m] = photo[m]
        data, _ = B.coded(img, (~m).astype(np.int8), pal)
        out.append(B.pad(data))
    return out[0], out[1]
