"""The FONY logo of the old disk (Puzzle Mania v1.04, assets/fony_disk: FONY.PZL = BASIC COPY file, 237 x 66 pixels at 4 bit, FONY.COL = 16 x R,G,B 0..7) for the intro of the game.
 MSX2: work/fony5.bin = bank with the image as bytes of a SCREEN 5 line (66 lines of 119 bytes, the line starts at x = 8: 4 bytes in the VRAM line), game/fonyov.inc = the palette
 MSX1: work/fony_disk.bin = SCREEN 2 patterns + colours (12288 bytes) of the same picture at the same place (8, 20), 15 TMS9918A colours
 jingle: assets/fony_jingle.wav (the FM jingle of the disk, openMSX recording: 0.7 s of silence, then the tune; the first colour of the logo appears at 0 s)
  python fony_intro.py        -> the files above + Screenshots/fony2/fony_disk_msx1.png / _msx2.png (x3 preview)"""
import os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
PROJ = os.path.dirname(HERE)
D = os.path.join(PROJ, 'assets', 'fony_disk')
X0, Y0 = 8, 20                                  # the place of the logo on the disk (COPY "FONY.PZL" TO (8,20))


def load():
    d = open(os.path.join(D, 'FONY.PZL'), 'rb').read()
    w = d[0] | d[1] << 8; h = d[2] | d[3] << 8
    raw = np.frombuffer(d[4:], np.uint8)
    nib = np.empty(raw.size * 2, np.uint8); nib[0::2] = raw >> 4; nib[1::2] = raw & 15
    img = nib[:w * h].reshape(h, w)                                  # the pixels are packed one after the other (no padding at the end of a line)
    v = [int(x) for x in open(os.path.join(D, 'FONY.COL'), 'rb').read().decode().replace('\r', '').split('\n') if x.strip().isdigit()]
    pal = np.array(v).reshape(16, 3)                                 # 0..7 per colour
    return img, pal


def msx2_bank():
    """-> 16 KB bank: 66 lines x 119 bytes (237 pixels + one black pixel), then nothing"""
    img, pal = load()
    h, w = img.shape
    rows = np.zeros((h, 238), np.uint8); rows[:, :w] = img
    b = (rows[:, 0::2] << 4 | rows[:, 1::2]).astype(np.uint8)         # 119 bytes per line
    data = b.tobytes()
    return data + bytes([0xFF]) * (16384 - len(data))


def v9938(pal):
    return b''.join(bytes([r << 4 | b, g]) for r, g, b in pal.tolist())


def inc():
    img, pal = load()
    t = v9938(pal)
    s = 'fony_pal:' + chr(10) + ''.join('        db ' + ','.join(str(x) for x in t[i:i + 2]) + chr(10) for i in range(0, 32, 2))
    return s


CLS = ['K', 'K', 'K', 'K', 'W', 'W', 'M', 'W', 'M', 'M', 'W', 'L', 'L', 'L', 'L', 'L']       # class of the 16 colours of the disk: black, wine, grey, light
TMS_OF = {'K': 1, 'W': 13, 'M': 13, 'L': 13}                                                    # the TMS9918A colours: black, magenta, light grey, white


def msx1_bank():
    """every 8 x 1 cell of the logo gets the two TMS colours that fit its pixels best (the classes above, black wins a tie): no stray colours"""
    import build_game as B, msx1_preview as P
    img, pal = load()
    h, w = img.shape
    cl = np.ones((192, 256), np.uint8)
    cl[Y0:Y0 + h, X0:X0 + w] = np.array([TMS_OF[c] for c in CLS], np.uint8)[img]
    T = P.TMS
    cols = [1, 13, 14, 15]
    pairs = [(a, b) for a in cols for b in cols if a < b]
    dist = np.array([[np.abs(T[i] - T[j]).sum() for j in range(16)] for i in range(16)])
    pat = np.zeros((192, 32), np.uint8); col = np.zeros((192, 32), np.uint8)
    rend = np.zeros((192, 256, 3), np.uint8)
    for y in range(192):
        for c in range(32):
            px = cl[y, c * 8:c * 8 + 8]
            best = None
            for a, b in pairs:
                e = sum(min(dist[p, a], dist[p, b]) for p in px) + (0 if a == 1 else 1)
                if best is None or e < best[0]:
                    best = (e, a, b)
            _, a, b = best
            bits = [1 if dist[p, b] < dist[p, a] else 0 for p in px]
            pat[y, c] = sum(v << (7 - k) for k, v in enumerate(bits))
            col[y, c] = b << 4 | a
            rend[y, c * 8:c * 8 + 8] = [T[b if v else a] for v in bits]
    return B.chars(pat) + B.chars(col), rend


if __name__ == '__main__':
    out = os.path.join(PROJ, 'Screenshots', 'fony2'); os.makedirs(out, exist_ok=True)
    open(os.path.join(PROJ, 'work', 'fony5.bin'), 'wb').write(msx2_bank())
    open(os.path.join(PROJ, 'game', 'fonyov.inc'), 'w').write(inc())
    data, rend = msx1_bank()
    open(os.path.join(PROJ, 'work', 'fony_disk.bin'), 'wb').write(data)
    Image.fromarray(rend).resize((768, 576), Image.NEAREST).save(os.path.join(out, 'fony_disk_msx1.png'))
    img, pal = load()
    full = np.zeros((192, 256, 3), np.uint8); full[Y0:Y0 + img.shape[0], X0:X0 + img.shape[1]] = (pal[img] * 255 // 7)
    Image.fromarray(full).resize((768, 576), Image.NEAREST).save(os.path.join(out, 'fony_disk_msx2.png'))
    print('done')
