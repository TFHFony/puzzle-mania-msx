"""10 candidate stills of a clip: MSX1 render of every candidate + contact sheet.  usage: cands10.py CLIP_INDEX NAME [START END] (seconds; default: the whole clip) -> work/stills/NAME_cand_k.png, NAME_cand_k_src.png, NAME_sheet.png"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, 'F:/MSX Projects/PMdev26/tools')
import stills as S
I = int(sys.argv[1]); NAME = sys.argv[2]; N = 10
dur = S.duration(I); print(dur)
T0, T1 = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (None, None)
cells = []
for k in range(N):
    t = T0 + (T1 - T0) * k / (N - 1) if T0 is not None else dur * (k + 0.5) / N
    src = S.grab(I, t, 256, 192)
    _, _, im = S.encode(src.astype(np.float32))
    Image.fromarray(im).save(os.path.join(S.OUT, '%s_cand_%d.png' % (NAME, k)))
    Image.fromarray(src).save(os.path.join(S.OUT, '%s_cand_%d_src.png' % (NAME, k)))
    cells.append((im, t))
sheet = Image.new('RGB', (5 * 256, 2 * 212), (30, 30, 30)); d = ImageDraw.Draw(sheet)
for k, (im, t) in enumerate(cells):
    x, y = (k % 5) * 256, (k // 5) * 212
    sheet.paste(Image.fromarray(im), (x, y)); d.text((x + 4, y + 196), 'candidate %d   t=%.1fs' % (k + 1, t), fill=(255, 255, 0))
sheet.save(os.path.join(S.OUT, '%s_sheet.png' % NAME))
