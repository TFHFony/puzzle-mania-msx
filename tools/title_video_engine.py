"""Title screen with a video in the letters (test): pattern data only, the colours are fixed.
The letters PUZZLE / MANIA are the same as in the normal title (build_game.welcome_image).  A video frame is a 1 bit picture inside the letters: lit pixels
have the colour of their character row (a gradient per band), everything else is black.  The two bands are 12 character rows = 3072 bytes each of the
pattern table; a frame is sent to the VRAM by the job engine as 4 entries (band 1 left half, band 1 right half, band 2 left half, band 2 right half:
12 rows of 128 bytes, contiguous in the ROM).  Two frames (2 x 6144 bytes) per 16 KB bank.
  build(video, start, seconds, fps) -> (welcome bank data, frame banks, number of frames, preview)"""
import os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)

GRAD1 = [11, 11, 11, 11, 10, 10, 10, 9, 9, 9, 8, 8]          # PUZZLE: light yellow -> orange -> red (MSX colour numbers)
GRAD2 = [7, 7, 7, 7, 5, 5, 5, 5, 13, 13, 13, 13]             # MANIA: cyan -> light blue -> magenta
TMS = [(0, 0, 0), (0, 0, 0), (33, 200, 66), (94, 220, 120), (84, 85, 237), (125, 118, 252), (212, 82, 77), (66, 235, 245),
       (252, 85, 84), (255, 121, 120), (212, 193, 84), (230, 206, 128), (33, 176, 59), (201, 91, 186), (204, 204, 204), (255, 255, 255)]


def letter_mask():
    """256x192 bool: the pixels of the letters (the same drawing as the normal title)"""
    mask = Image.new('L', (256, 192), 0)
    font = ImageFont.truetype(r'C:\Windows\Fonts\impact.ttf', 400)
    for word, (x0, y0, x1, y1) in (('PUZZLE', (5, 5, 251, 91)), ('MANIA', (5, 101, 251, 187))):
        glyphs = []
        for ch in word:
            g = Image.new('L', (800, 700), 0)
            ImageDraw.Draw(g).text((50, 20), ch, font=font, fill=255)
            glyphs.append(g.crop(g.getbbox()))
        gap = 45
        H = max(g.height for g in glyphs)
        big = Image.new('L', (sum(g.width for g in glyphs) + gap * (len(glyphs) - 1), H), 0)
        x = 0
        for g in glyphs:
            big.paste(g, (x, H - g.height)); x += g.width + gap
        mask.paste(big.resize((x1 - x0, y1 - y0), Image.LANCZOS), (x0, y0))
    return np.asarray(mask) >= 128


def vram_order(a):
    out = np.zeros(6144, np.uint8)
    y = np.arange(192)[:, None]; c = np.arange(32)[None, :]
    idx = (y // 64) * 2048 + (((y % 64) // 8) * 32 + c) * 8 + (y % 8)
    out[idx.ravel()] = a.ravel()
    return out


def colour_table(mask):
    """(192, 32) colour bytes: fg << 4 | black in the cells that touch a letter, black on black elsewhere"""
    col = np.full((192, 32), 0x11, np.uint8)
    for cy in range(24):
        fg = (GRAD1 if cy < 12 else GRAD2)[cy % 12]
        for cx in range(32):
            if mask[cy * 8:cy * 8 + 8, cx * 8:cx * 8 + 8].any():
                col[cy * 8:cy * 8 + 8, cx] = (fg << 4) | 1
    return col


def extract(video, start, seconds, fps):
    vf = "crop=w='min(iw,ih*4/3)':h='min(ih,iw*3/4)':x='(iw-out_w)*0.5':y='(ih-out_h)/2',scale=256:192:flags=area,fps=%g,format=gray" % fps
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(start), '-t', str(seconds), '-i', video, '-an', '-vf', vf, '-f', 'rawvideo', '-'], capture_output=True, check=True)
    a = np.frombuffer(r.stdout, np.uint8)
    n = len(a) // (192 * 256)
    return a[:n * 192 * 256].reshape(n, 192, 256).astype(np.float32)


def dither(g, mask):
    """Floyd-Steinberg inside the letters (g 0..1); returns bool lit"""
    g = g.copy()
    out = np.zeros((192, 256), bool)
    for y in range(192):
        for x in range(256):
            if not mask[y, x]:
                continue
            v = g[y, x]
            o = 1.0 if v >= 0.5 else 0.0
            out[y, x] = o > 0
            e = v - o
            if x + 1 < 256 and mask[y, x + 1]: g[y, x + 1] += e * 7 / 16
            if y + 1 < 192:
                if x > 0 and mask[y + 1, x - 1]: g[y + 1, x - 1] += e * 3 / 16
                if mask[y + 1, x]: g[y + 1, x] += e * 5 / 16
                if x + 1 < 256 and mask[y + 1, x + 1]: g[y + 1, x + 1] += e * 1 / 16
    return out


def build(video, start=7.0, seconds=4.0, fps=3.15):
    mask = letter_mask()
    col = colour_table(mask)
    frames = extract(video, start, seconds, fps)
    lo, hi = np.percentile(frames[:, mask], 3), np.percentile(frames[:, mask], 97)
    pats = []; prev = []
    for f in frames:
        g = np.clip((f - lo) / max(1.0, hi - lo), 0, 1) ** 0.6 * 0.9 + 0.1      # a little lift: the letters stay readable
        lit = dither(g, mask)
        prev.append(lit)
        pats.append(np.packbits(lit, axis=1))                    # (192, 32), bit 7 = leftmost pixel
    n = len(pats)
    welcome = vram_order(pats[0]).tobytes() + vram_order(col).tobytes()
    blocks = []
    for p in pats:
        v = vram_order(p)
        e = []
        for r0 in (0, 12):
            for h in (0, 128):
                e.append(b''.join(v[r * 256 + h:r * 256 + h + 128].tobytes() for r in range(r0, r0 + 12)))
        b = b''.join(e)
        assert len(b) == 6144
        blocks.append(b)
    banks = []
    for i in range(0, n, 2):
        d = blocks[i] + (blocks[i + 1] if i + 1 < n else b'')
        banks.append(d + bytes([0xFF]) * (16384 - len(d)))
    # preview
    c = np.zeros((n, 192, 256, 3), np.uint8)
    for k in range(n):
        for y in range(192):
            fg = TMS[col[y, 0]] if False else None
        colrgb = np.zeros((192, 256, 3), np.uint8)
        for y in range(192):
            for cx in range(32):
                fgc = col[y, cx] >> 4
                colrgb[y, cx * 8:cx * 8 + 8] = TMS[fgc]
        c[k] = colrgb * prev[k][..., None]
    return (welcome + bytes([0xFF]) * (16384 - len(welcome))), banks, n, c


if __name__ == '__main__':
    w, banks, n, prev = build(os.path.join(PROJ, 'Videos', 'Puzzle.mp4'))
    print(len(w), len(banks), n)
    sheet = np.concatenate([np.concatenate(list(prev[i:i + 5]), 1) for i in range(0, n - n % 5, 5)], 0)
    out = os.path.join(PROJ, 'work', 'tv'); os.makedirs(out, exist_ok=True)
    Image.fromarray(sheet).save(os.path.join(out, 'title_video_preview.png'))
