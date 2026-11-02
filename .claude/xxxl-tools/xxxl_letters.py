"""The XXXL screen like the PUZZLE MANIA title: only the four letters XXXL, as big as the screen allows, filled with the photo of the Oops clip (clip 6, the puzzle photo), black around them.
Same drawing and coding as tools/build_game.py welcome_image (the letters of tools/title_video.py letter_mask).
usage: python xxxl_letters.py [x0,y0,x1,y1 [name]]   -> proposals/letters_{msx1,msx2}.png (coded), letters_src.png"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(PROJ, 'tools')); sys.path.insert(0, r'F:\MSX Projects\Dev27\msx1-video-player\tools')
OUT = os.path.join(HERE, 'proposals')


def letters_mask(word='XXXL', box=(5, 5, 251, 187), gap=45):
    """256x192 bool: the letters of the word in Impact, stretched to the box (the baseline and the height are the same for every letter)"""
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


if __name__ == '__main__':
    import build_game as B, palette_opt as PO
    from encode_clips import USED
    choices = json.load(open(os.path.join(PROJ, 'tools', 'choices.json')))
    src = Image.open(os.path.join(PROJ, 'work', 'stills', 'clip06_%d_src.png' % choices[6])).convert('RGB')
    pj = PO.load()
    pal2 = np.array(pj['photo'][USED.index(6)], np.float32)
    box = tuple(int(v) for v in sys.argv[1].split(',')) if len(sys.argv) > 1 else (5, 5, 251, 187)
    name = sys.argv[2] if len(sys.argv) > 2 else 'letters'
    m = letters_mask(box=box)
    for tag, ph, pal in (('msx1', B.lift(src), None), ('msx2', PO.adjust(src, **PO.LOOK_CLIP.get(6, PO.LOOK)), pal2)):
        photo = np.asarray(ph)
        img = np.zeros((192, 256, 3), np.uint8)
        img[m] = photo[m]
        if tag == 'msx1':
            Image.fromarray(img).save(os.path.join(OUT, name + '_src.png'))
        data, rend = B.coded(img, (~m).astype(np.int8), pal)
        Image.fromarray(rend).save(os.path.join(OUT, name + '_%s.png' % tag))
        print(tag, flush=True)
    sh = Image.new('RGB', (1024, 384))
    for j, tag in enumerate(('msx1', 'msx2')):
        sh.paste(Image.open(os.path.join(OUT, name + '_%s.png' % tag)).resize((512, 384), Image.NEAREST), (j * 512, 0))
    sh.save(os.path.join(OUT, name + '_sheet.png'))
