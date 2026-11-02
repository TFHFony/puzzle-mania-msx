"""usage: montage.py DIR OUT.png N...   -> contact sheet of the screenshots fNNN.png of DIR (4 columns)"""
import sys
from PIL import Image
d, out = sys.argv[1:3]; idx = [int(a) for a in sys.argv[3:]]
ims = [Image.open('%s/f%03d.png' % (d, i)).convert('RGB') for i in idx]
w, h = ims[0].size; w2, h2 = w // 2, h // 2
cols = 4; rows = (len(ims) + cols - 1) // cols
sh = Image.new('RGB', (cols * w2, rows * h2))
for k, im in enumerate(ims): sh.paste(im.resize((w2, h2), Image.BOX), ((k % cols) * w2, (k // cols) * h2))
sh.save(out)
