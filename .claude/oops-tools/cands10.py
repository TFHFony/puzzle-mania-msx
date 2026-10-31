"""10 candidate stills of Videos/Oops2.mp4 (clip index 6): MSX1 render of every candidate + contact sheet -> work/stills/oops_cand_k.png, oops_sheet.png"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, 'F:/MSX Projects/PMdev26/tools')
import stills as S
I = 6; N = 10
dur = S.duration(I); print(dur)
cells = []
for k in range(N):
    t = dur * (k + 0.5) / N
    src = S.grab(I, t, 256, 192)
    _, _, im = S.encode(src.astype(np.float32))
    Image.fromarray(im).save(os.path.join(S.OUT, 'oops_cand_%d.png' % k))
    Image.fromarray(src).save(os.path.join(S.OUT, 'oops_cand_%d_src.png' % k))
    cells.append((im, t))
sheet = Image.new('RGB', (5 * 256, 2 * 212), (30, 30, 30)); d = ImageDraw.Draw(sheet)
for k, (im, t) in enumerate(cells):
    x, y = (k % 5) * 256, (k // 5) * 212
    sheet.paste(Image.fromarray(im), (x, y)); d.text((x + 4, y + 196), 'candidate %d   t=%.1fs' % (k + 1, t), fill=(255, 255, 0))
sheet.save(os.path.join(S.OUT, 'oops_sheet.png'))
