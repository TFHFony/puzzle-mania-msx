"""mock-ups of the S screen with a build number, made from a screenshot of the real screen (glyphs cut out of it): python spec_mock.py"""
from PIL import Image
import numpy as np
SRC = r'F:\MSX Projects\PMdev26\.claude\fony-tools\rec\spec_12.png'
im = Image.open(SRC).convert('RGB')
ROW0, PITCH, X0 = 72, 24, 27.2
CP = 27.4
def xc(c): return int(round(X0 + CP * c))
def yr(r): return ROW0 + PITCH * r
def glyph(r, c, w=24):
    return im.crop((xc(c) - 2, yr(r) - 1, xc(c) - 2 + w, yr(r) + 23))
# glyph sources (row, col) in the real screen
SRCG = {'R': (18, 2), 'O': (18, 3), 'M': (18, 4), ':': (18, 5), 'B': (23, 17), 'U': (0, 8), 'L': (0, 11), 'I': (0, 17), 'D': (6, 4),
        '6': (8, 23), '5': (10, 18), '/': (21, 8), '1': (8, 22), '2': (18, 19)}
def put(canvas, r, c, text):
    for k, ch in enumerate(text):
        if ch == ' ': continue
        canvas.paste(glyph(*SRCG[ch]), (xc(c + k) - 2, yr(r) - 1))
def clear(canvas, r0, r1):
    canvas.paste((0, 0, 0), (0, yr(r0) - 1, 960, yr(r1) + 23))
def colour(canvas, r, c, n, like=None):
    pass
# A: label ROM / BUILD, value 128 MB / 65
A = im.copy()
clear(A, 18, 18)
put(A, 18, 2, 'ROM / BUILD:'); 
# the value: "128 MB" is already there; take the original row crop for "128 MB" and add " / 65" in the same colour
orig_val = im.crop((xc(18) - 2, yr(18) - 1, xc(24) - 2, yr(18) + 23))
A.paste(orig_val, (xc(18) - 2, yr(18) - 1))
put(A, 18, 24, ' / 65')
# B: its own line, BUILD, the lines below it one row down
B = im.copy()
low = im.crop((0, yr(20) - 1, 960, yr(21) + 23))
clear(B, 20, 21)
B.paste(low, (0, yr(21) - 1))
put(B, 20, 2, 'BUILD:')
put(B, 20, 18, '65')
W, H = 960, 720
S = Image.new('RGB', (2 * W + 20, H), (40, 40, 40))
S.paste(A, (0, 0)); S.paste(B, (W + 20, 0))
S.save(r'F:\MSX Projects\PMdev26\work\stills\spec_build_proposal.png')
A.save(r'F:\MSX Projects\PMdev26\work\stills\spec_build_A.png'); B.save(r'F:\MSX Projects\PMdev26\work\stills\spec_build_B.png')
