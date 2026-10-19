"""Candidate stills per clip: 8 frames -> PNG (256x192 source, SCREEN 2 render, 64x48 SCREEN 2 thumbnail render) + contact sheets.
usage: stills.py [clip index ...]   -> work/stills/clipNN_k.{png,rgb} , work/stills/sheet_clipNN.png"""
import os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
sys.path.insert(0, r'F:\MSX Projects\Dev27\msx1-video-player\tools'); sys.path.insert(0, HERE)
import s4_lab as L, msx1_preview as P
from screen4_sim import PI, PJ
from encode_clips import CLIPS
OUT = os.path.join(PROJ, 'work', 'stills'); os.makedirs(OUT, exist_ok=True)
NCAND = 8


def code_rows(src, pal=P.TMS, kcon=0.06, K=8, clampe=0.3, fix=None):
    """same as msx1_video.code_rows but for any width (multiple of 8).
    fix: optional (h, w) int array, 0 = free pixel, 1 = must be black, 2 = must be white.  A row segment that contains fixed pixels may only use
    a colour pair that contains those colours, so edges (border, outline, lines) are exact and never bleed into the photo colours."""
    h, w = src.shape[:2]; nc = w // 8
    GAM = L.GAM; CW = L.CW
    R = L.to_lin(src.reshape(h, nc, 8, 3).astype(np.float32))
    Pl = L.to_lin(pal); Al, Bl = Pl[PI], Pl[PJ]
    ts = np.linspace(0, 1, K, dtype=np.float32)
    Mlin = Al[:, None, :] + ts[None, :, None] * (Bl - Al)[:, None, :]
    Mg = (np.clip(Mlin, 0, 1) ** (1 / GAM)) * 255.0
    contrast = (((np.clip(Al, 0, 1) ** (1 / GAM) - np.clip(Bl, 0, 1) ** (1 / GAM)) * 255.0) ** 2 * CW).sum(-1)
    Ag = pal[PI]; Bg = pal[PJ]
    if fix is not None:
        fixs = fix.reshape(h, nc, 8)
        need_b = (fixs == 1).any(-1); need_w = (fixs == 2).any(-1)
        has_b = (PI <= 1) | (PJ <= 1); has_w = (PI == 15) | (PJ == 15)
        fl = np.where(fix == 2, 1.0, 0.0).astype(np.float32)
        fixmask = (fix > 0).reshape(h, nc, 8)
    A_idx = np.zeros((h, nc), np.int64); B_idx = np.zeros((h, nc), np.int64); bits = np.zeros((h, nc, 8), bool)
    err_next = np.zeros((nc, 8, 3), np.float32)
    for r in range(h):
        cur = np.clip(R[r] + err_next, 0, 1)
        if fix is not None:
            cur = np.where(fixmask[r][..., None], fl[r].reshape(nc, 8)[..., None], cur)
        cg = (cur ** (1 / GAM)) * 255.0
        d = (((cg[:, :, None, None, :] - Mg[None, None]) ** 2) * CW).sum(-1)
        cost = d.min(-1).sum(1) + kcon * 8 * contrast
        if fix is not None:
            bad = (need_b[r][:, None] & ~has_b[None, :]) | (need_w[r][:, None] & ~has_w[None, :])
            cost = np.where(bad, 1e12, cost)
        sel = cost.argmin(-1)
        a = Al[sel]; b = Bl[sel]; ag = Ag[sel]; bg = Bg[sel]
        A_idx[r] = PI[sel]; B_idx[r] = PJ[sel]
        err_next[:] = 0; e_row = np.zeros((nc, 3), np.float32)
        fwd = r % 2 == 0; dr = 1 if fwd else -1
        for px in (range(8) if fwd else range(7, -1, -1)):
            cc = cur[:, px] + e_row
            ccg = (np.clip(cc, 0, 1) ** (1 / GAM)) * 255.0
            dA = (((ccg - ag) ** 2) * CW).sum(-1); dB = (((ccg - bg) ** 2) * CW).sum(-1)
            pick = dB < dA
            if fix is not None:
                fx = fixs[r][:, px]
                pick = np.where(fx == 2, B_idx[r] == 15, np.where(fx == 1, ~(A_idx[r] <= 1), pick))
            o = np.where(pick[:, None], b, a)
            e = np.clip(cc - o, -clampe, clampe)
            if fix is not None:
                e = np.where(fixs[r][:, px][:, None] > 0, 0.0, e)
            bits[r, :, px] = pick
            e_row = e * 7 / 16
            err_next[:, px] += e * 5 / 16
            if 0 <= px - dr < 8: err_next[:, px - dr] += e * 3 / 16
            if 0 <= px + dr < 8: err_next[:, px + dr] += e * 1 / 16
    return A_idx, B_idx, bits


def encode(src, fix=None):
    """-> pat (h, nc) uint8, col (h, nc) uint8, rendered image"""
    A, B, bits = code_rows(src, fix=fix)
    pat = (bits.astype(np.uint8) << (7 - np.arange(8, dtype=np.uint8))).sum(-1).astype(np.uint8)
    col = ((B << 4) | A).astype(np.uint8)
    img = np.where(bits[..., None], P.TMS[B][:, :, None, :], P.TMS[A][:, :, None, :]).reshape(src.shape[0], src.shape[1], 3)
    return pat, col, np.clip(img, 0, 255).astype(np.uint8)


def grab(i, t, w, h, flt=''):
    vf = "crop=w='min(iw,ih*4/3)':h='min(ih,iw*3/4)':x='(iw-out_w)*0.5':y='(ih-out_h)/2',scale=%d:%d:flags=area%s" % (w, h, flt)
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', '%.2f' % t, '-i', os.path.join(PROJ, 'Videos', CLIPS[i]), '-frames:v', '1', '-vf', vf,
                        '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(h, w, 3)


def duration(i):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', os.path.join(PROJ, 'Videos', CLIPS[i])], capture_output=True, text=True)
    return float(r.stdout)


def main():
    idx = [int(a) for a in sys.argv[1:]] or range(len(CLIPS))
    for i in idx:
        dur = duration(i)
        cells = []
        for k in range(NCAND):
            t = dur * (k + 0.5) / NCAND
            src = grab(i, t, 256, 192)
            Image.fromarray(src).save(os.path.join(OUT, 'clip%02d_%d_src.png' % (i, k)))
            big = grab(i, t, 256, 192)       # (same size: the stills are coded at 256x192 like the game image)
            _, _, im = encode(big.astype(np.float32))
            Image.fromarray(im).save(os.path.join(OUT, 'clip%02d_%d_s2.png' % (i, k)))
            th = grab(i, t, 64, 48)
            _, _, tim = encode(th.astype(np.float32))
            Image.fromarray(tim).save(os.path.join(OUT, 'clip%02d_%d_thumb.png' % (i, k)))
            cell = np.zeros((192 + 52, 256, 3), np.uint8)
            cell[:192] = im; cell[192:240, :64] = 0; cell[192:240, :64] = np.repeat(np.repeat(tim, 1, 0), 1, 1)[:48, :64] if False else tim
            cell[196:244 - 4, 70:70 + 128] = 0
            cells.append((cell, t))
        W2, Hc = 256, 244
        sheet = Image.new('RGB', (4 * W2, 2 * Hc), (30, 30, 30)); d = ImageDraw.Draw(sheet)
        for k, (cell, t) in enumerate(cells):
            x, y = (k % 4) * W2, (k // 4) * Hc
            sheet.paste(Image.fromarray(cell), (x, y)); d.text((x + 72, y + 200), 'clip %d  cand %d  t=%.1fs' % (i, k, t), fill=(255, 255, 0))
        sheet.save(os.path.join(OUT, 'sheet_clip%02d.png' % i))
        print('stills', i, CLIPS[i], flush=True)


if __name__ == '__main__':
    main()
