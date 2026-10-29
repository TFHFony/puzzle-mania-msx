"""Examples for the look of the MSX2 photos: the current palettes against a few variants (more saturation, deeper blacks).
python tools/palette_examples.py [photo ...]  -> work/shots/pal_examples.png"""
import os, sys, json, time
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import palette_opt as O

VARIANTS = {
    'current': None,
    'V1 sat 1.2, black 0.03': dict(sat=1.2, floor=0.03, contrast=1.0),
    'V2 sat 1.4, black 0.0, contrast': dict(sat=1.4, floor=0.0, contrast=1.15),
}


def adjust(src, sat, floor, contrast):
    a = np.asarray(src, np.float32) / 255
    lum = float((0.3 * a[..., 0] + 0.55 * a[..., 1] + 0.15 * a[..., 2]).mean())
    g = min(1.0, max(0.55, np.log(0.45) / np.log(max(lum, 0.05))))
    a = floor + (1 - floor) * a ** g                      # the same adaptive gamma as lift(), a lower floor
    im = Image.fromarray(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8))
    im = ImageEnhance.Color(im).enhance(sat)
    if contrast != 1.0:
        b = np.asarray(im, np.float32) / 255
        b = np.clip((b - 0.5) * contrast + 0.5, 0, 1)
        im = Image.fromarray((b * 255 + 0.5).astype(np.uint8))
    return im


if __name__ == '__main__':
    from build_game import lift
    from encode_clips import USED
    choices = json.load(open(os.path.join(HERE, 'choices.json')))
    pj = O.load()
    rows = []
    for p in [int(a) for a in sys.argv[1:]] or [0, 4, 7]:
        c = USED[p]
        raw = Image.open(os.path.join(PROJ, 'work', 'stills', 'clip%02d_%d_src.png' % (c, choices[c]))).convert('RGB')
        cells = []
        for name, kw in VARIANTS.items():
            t0 = time.time()
            if kw is None:
                src = np.asarray(lift(raw)); pal = np.array(pj['photo'][p], np.float32)
            else:
                src = np.asarray(adjust(raw, **kw))
                free = [i for i in range(16) if i not in O.FIXED and i not in O.BRIGHT]
                pal = O.TMS.copy(); pal[free] = O.kmeans_pal(src, len(free))
                pal = O.refine(O.half(src), pal, free + list(O.BRIGHT), 3, lambda s: None)
            img = np.clip(O.render(src, pal), 0, 255).astype(np.uint8)
            cell = Image.fromarray(img)
            ImageDraw.Draw(cell).text((4, 4), name, fill=(255, 255, 0))
            cells.append(cell)
            print(p, name, '%.0f s' % (time.time() - t0), flush=True)
        rows.append(np.concatenate([np.asarray(c) for c in cells], 1))
    sheet = np.concatenate(rows, 0)
    Image.fromarray(sheet).save(os.path.join(PROJ, 'work', 'shots', 'pal_examples.png'))
    print('saved')
