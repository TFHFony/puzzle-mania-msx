"""5 versions of one frame, the 4:3 crop window shifted to the right: shift5.py CLIP_INDEX NAME T -> work/stills/NAME_shift_k_src.png + NAME_shift_sheet.png"""
import os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, 'F:/MSX Projects/PMdev26/tools')
import stills as S
I = int(sys.argv[1]); NAME = sys.argv[2]; T = float(sys.argv[3])
FS = (0.5, 0.625, 0.75, 0.875, 1.0)
cells = []
for k, f in enumerate(FS):
    vf = "crop=w='min(iw,ih*4/3)':h='min(ih,iw*3/4)':x='(iw-out_w)*%.3f':y='(ih-out_h)/2',scale=256:192:flags=area" % f
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', '%.2f' % T, '-i', os.path.join(S.PROJ, 'Videos', S.CLIPS[I]), '-frames:v', '1', '-vf', vf, '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'], capture_output=True, check=True)
    src = np.frombuffer(r.stdout, np.uint8).reshape(192, 256, 3)
    _, _, im = S.encode(src.astype(np.float32))
    Image.fromarray(src).save(os.path.join(S.OUT, '%s_shift_%d_src.png' % (NAME, k)))
    cells.append((im, f))
sheet = Image.new('RGB', (5 * 256, 212), (30, 30, 30)); d = ImageDraw.Draw(sheet)
for k, (im, f) in enumerate(cells):
    sheet.paste(Image.fromarray(im), (k * 256, 0)); d.text((k * 256 + 4, 196), 'version %d   shift %.0f%%' % (k + 1, f * 100), fill=(255, 255, 0))
sheet.save(os.path.join(S.OUT, '%s_shift_sheet.png' % NAME))
