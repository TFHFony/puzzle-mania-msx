"""Build the Puzzle Mania NEO16 ROM (tools/build_all.py builds all versions).
  python tools/build_game.py [--lite] [--curve ym|ay|joint] [--out file.rom] [--quick] [--fresh]
  --lite   64 MB version: shortened 8.33 fps clips with fade-out (work/lite_clipNN_bytes.npz); without it: the full clips at 10 fps
  --kmenu/--kpuz K (--kmenub/--kpuzb: frames with work after the block, --kmenuc/--kpuzc: the frame of an action) skipped samples per frame of that track; its music is coded for it (defaults 2/5/6 menu, 2/5/10 puzzle)
  --curve  PSG volume curve of the music (default: the neutral curve 'joint'; 'ym' and 'ay' are test options)
Needs work/clipNN_bytes.npz (encode_clips.py), work/stills (stills.py), work/fony_copper.bin (fony_logo.py); photo choice per clip: tools/choices.json
ROM banks: 0 game | 1 + 10 p + k: photo p, k = 0 plain image + thumbnail, 1 size buttons, 2..5 thick tile lines 3x3..6x6, 6..9 thin tile lines |
           WELCOME, FONY, HOWTO x3, CREDITS, SELFTEST | jingle, menu music, puzzle music | VIDEO0..: video frames, one per bank
"""
import os, sys, json, subprocess, pickle
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, r'F:\MSX Projects\Dev27\msx1-video-player\tools')
from stills import encode
from encode_clips import CLIPS, USED

STRIDE = 10                 # banks per photo
WELCOME, FONY, HOWTO, CREDITS, SELFTEST = 91, 92, 93, 96, 97
PLR_BANK = 254
JINGLE, MUSIC0 = 98, 100
VIDEO0 = 256                # 4 MB for the game, the video starts here
WELCOME_PHOTO = 7           # the letters of the title are filled with this photo (clip id)
# puzzle geometry per size N: (tile width, tile height, offset x, offset y) in characters
PTAB = {3: (10, 8, 1, 0), 4: (8, 6, 0, 0), 5: (6, 4, 1, 2), 6: (5, 4, 1, 0)}
SIZES = list(PTAB)
LINE = (255, 255, 255)
SJASM = r'F:\MSX Projects\Dev27\.claude\msx-video-tools\sjasmplus\sjasmplus-1.24.0.win\sjasmplus.exe'


def chars(a):
    """(h, w8) bytes per pixel row -> char order (cy, cx, row)"""
    h, w = a.shape
    return a.reshape(h // 8, 8, w).transpose(0, 2, 1).reshape(-1).tobytes()


def coded(img, fix=None):
    pat, col, rend = encode(np.asarray(img, np.float32), fix)
    return chars(pat) + chars(col), rend


def pad(b, n=16384):
    assert len(b) <= n, len(b)
    return b + bytes([0xFF]) * (n - len(b))


def lined(src, N, thin=False):
    """puzzle image with tile lines: thick = a line on all four edges of every tile (2 px between tiles), thin = left and top edge (1 px)"""
    tw, th, ox, oy = PTAB[N]
    im = np.array(src)
    fix = np.zeros(im.shape[:2], np.int8)
    for ty in range(N):
        for tx in range(N):
            x0 = (ox + tx * tw) * 8; x1 = (ox + (tx + 1) * tw) * 8; y0 = (oy + ty * th) * 8; y1 = (oy + (ty + 1) * th) * 8
            edges = [(slice(y0, y1), x0), (y0, slice(x0, x1))]
            if not thin:
                edges += [(slice(y0, y1), x1 - 1), (y1 - 1, slice(x0, x1))]
            for sl in edges:
                im[sl] = LINE; fix[sl] = 2
    return im, fix


def lift(img):
    """brighten dark photos (adaptive gamma) and lift the blacks, so that dark areas keep some texture in the puzzle"""
    a = np.asarray(img, np.float32) / 255
    lum = float((0.3 * a[..., 0] + 0.55 * a[..., 1] + 0.15 * a[..., 2]).mean())
    g = min(1.0, max(0.55, np.log(0.45) / np.log(max(lum, 0.05))))
    a = 0.09 + 0.91 * a ** g
    return Image.fromarray(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8))


def thumbnail(src, w, h):
    """a small photo that survives the 2 colours per 8 pixels: sharpen before and after the reduction, stretch the contrast, a little more colour"""
    im = src.filter(ImageFilter.UnsharpMask(radius=2.0, percent=110, threshold=2))
    im = im.resize((w, h), Image.LANCZOS)
    im = ImageOps.autocontrast(im, cutoff=1)
    im = ImageEnhance.Color(im).enhance(1.2)
    return im.filter(ImageFilter.UnsharpMask(radius=0.8, percent=90, threshold=1))


def arrows():
    """two 16x32 px (2x4 chars) triangles: pattern bytes (char order) + colour bytes"""
    out = {}
    for name in ('r', 'l'):
        pat = np.zeros((32, 16), np.uint8)
        for y in range(32):
            L = int(round(15 * (1 - abs(y - 15.5) / 16))) + 1
            if name == 'r':
                pat[y, :L] = 1
            else:
                pat[y, 16 - L:] = 1
        by = np.packbits(pat, axis=1)
        d = by.reshape(4, 8, 2).transpose(0, 2, 1).reshape(-1).tobytes()
        out[name] = d + bytes([0xB1]) * 64
    return out


def photo_banks(src_png, p=0, preview_dir=None):
    src = lift(Image.open(src_png).convert('RGB'))
    banks = []
    plain, r0 = coded(src)
    th = Image.new('RGB', (104, 80)); th.paste(thumbnail(src, 100, 76), (2, 2))          # thumbnail 104x80, black border
    tf = np.ones((80, 104), np.int8); tf[2:78, 2:102] = 0
    tdata, rt = coded(th, tf)
    banks.append(pad(plain + tdata))
    btn = b''; rb = []                                                                    # size buttons 96x72: photo, border, grid lines
    for N in SIZES:
        im = Image.new('RGB', (96, 72)); im.paste(thumbnail(src, 92, 68), (2, 2))
        a = np.array(im)
        bf = np.ones((72, 96), np.int8); bf[2:70, 2:94] = 0
        for k in range(1, N):
            xx = 2 + round(k * 92 / N); yy = 2 + round(k * 68 / N)
            a[2:70, xx] = LINE; bf[2:70, xx] = 2
            a[yy, 2:94] = LINE; bf[yy, 2:94] = 2
        d, r = coded(a, bf); btn += d; rb.append(r)
    assert len(btn) == 4 * 1728
    banks.append(pad(btn))
    rp = []
    for thin in (False, True):
        for N in SIZES:
            li, lf = lined(src, N, thin)
            d, r = coded(li, lf); banks.append(pad(d)); rp.append(r)
    assert len(banks) == STRIDE
    if preview_dir:
        os.makedirs(preview_dir, exist_ok=True)
        Image.fromarray(r0).save(os.path.join(preview_dir, 'photo%d_plain.png' % p))
        Image.fromarray(rt).save(os.path.join(preview_dir, 'photo%d_thumb.png' % p))
        Image.fromarray(np.concatenate([np.concatenate(rb[:2], 1), np.concatenate(rb[2:], 1)], 0)).save(os.path.join(preview_dir, 'photo%d_buttons.png' % p))
    return banks


def welcome_image(photo_png):
    """black screen, PUZZLE / MANIA in big capitals over the full 256x192, the letters filled with the photo"""
    photo = np.asarray(lift(Image.open(photo_png).convert('RGB')))
    mask = Image.new('L', (256, 192), 0)
    font = ImageFont.truetype(r'C:\Windows\Fonts\impact.ttf', 400)
    for word, (x0, y0, x1, y1) in (('PUZZLE', (5, 5, 251, 91)), ('MANIA', (5, 101, 251, 187))):
        glyphs = []
        for ch in word:
            g = Image.new('L', (800, 700), 0)
            ImageDraw.Draw(g).text((50, 20), ch, font=font, fill=255)
            glyphs.append(g.crop(g.getbbox()))
        gap = 45                                    # letter spacing at the 400 pt rendering
        H = max(g.height for g in glyphs)
        big = Image.new('L', (sum(g.width for g in glyphs) + gap * (len(glyphs) - 1), H), 0)
        x = 0
        for g in glyphs:
            big.paste(g, (x, H - g.height)); x += g.width + gap
        mask.paste(big.resize((x1 - x0, y1 - y0), Image.LANCZOS), (x0, y0))
    m = np.asarray(mask) >= 128
    img = np.zeros((192, 256, 3), np.uint8)
    img[m] = photo[m]
    data, rend = coded(img, (~m).astype(np.int8))
    return pad(data), rend


def vram_order(a):
    out = np.zeros(6144, np.uint8)
    y = np.arange(192)[:, None]; c = np.arange(32)[None, :]
    idx = (y // 64) * 2048 + (((y % 64) // 8) * 32 + c) * 8 + (y % 8)
    out[idx.ravel()] = a.ravel()
    return out


def frame_bytes(pat, col):
    P = vram_order(pat); C = vram_order(col)
    return pad(b''.join(P[t * 2048:(t + 1) * 2048].tobytes() + C[t * 2048:(t + 1) * 2048].tobytes() for t in range(3)))


def build_assets(choices, fresh):
    """photo banks, title, FONY, how to play, credits (cached: they take a few minutes)"""
    pk = os.path.join(PROJ, 'work', 'assets.pkl')
    key = (choices, USED, 'v3', os.path.getmtime(os.path.join(HERE, 'screens.py')), os.path.getmtime(os.path.join(PROJ, 'work', 'fony_copper.bin')))
    if os.path.exists(pk) and not fresh:
        k, banks = pickle.load(open(pk, 'rb'))
        if k == key:
            return banks
    import screens
    banks = [None]
    prev = os.path.join(PROJ, 'work', 'preview')
    for p, c in enumerate(USED):
        png = os.path.join(PROJ, 'work', 'stills', 'clip%02d_%d_src.png' % (c, choices[c]))
        banks += photo_banks(png, p, prev)
        print('photo', p, 'clip', c, 'candidate', choices[c], flush=True)
    assert len(banks) == 1 + STRIDE * len(USED)
    while len(banks) < WELCOME:
        banks.append(pad(b''))
    wb, wr = welcome_image(os.path.join(PROJ, 'work', 'stills', 'clip%02d_%d_src.png' % (WELCOME_PHOTO, choices[WELCOME_PHOTO])))
    Image.fromarray(wr).save(os.path.join(prev, 'welcome.png'))
    banks.append(wb)
    banks.append(pad(open(os.path.join(PROJ, 'work', 'fony_copper.bin'), 'rb').read()))
    for n in ('howto1', 'howto2', 'howto3', 'credits'):          # howto3 is not used any more: an empty bank keeps the layout
        if n == 'howto3':
            banks.append(pad(b''))
            continue
        data, rend = screens.screen(n, coded)
        Image.fromarray(rend).resize((768, 576), Image.NEAREST).save(os.path.join(prev, n + '.png'))
        banks.append(pad(data))
    banks.append(pad(b'NEO16OK!'))
    assert len(banks) == JINGLE, len(banks)
    pickle.dump((key, banks), open(pk, 'wb'))
    return banks


def main():
    arg = lambda name, default=None: sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default
    lite = '--lite' in sys.argv
    quick = '--quick' in sys.argv
    ascii16 = '--ascii16' in sys.argv                                           # 4 MB test ROM for the ASCII16 mapper (8-bit banks): clip 0 behind the music, as many frames as fit
    test0 = '--only-clip0' in sys.argv or ascii16                              # test ROM: every photo plays clip 0
    clips = [0] if test0 else USED
    ctab = [0] * len(USED) if test0 else list(range(len(clips)))                # clip table entry -> clip in 'clips'
    curve = arg('--curve', 'joint')
    os.environ['PSG_CURVE'] = curve
    # skipped samples per frame of the track (the music is coded for it): idle / a frame with work after the block / the frame of an action
    kmenu, kmenub, kmenuc = int(arg('--kmenu', '2')), int(arg('--kmenub', '5')), int(arg('--kmenuc', '6'))
    kpuz, kpuzb, kpuzc = int(arg('--kpuz', '2')), int(arg('--kpuzb', '5')), int(arg('--kpuzc', '7'))
    import music, jingle
    out = arg('--out', os.path.join(PROJ, 'PuzzleMania_64MB.rom' if lite else 'PuzzleMania_128MB.rom'))
    choices = json.load(open(os.path.join(HERE, 'choices.json')))      # candidate per clip id
    banks = build_assets(choices, '--fresh' in sys.argv)
    mus_jingle = music.array_track('jingle', jingle.make(), 2)
    mus_menu = music.track('menu', os.path.join(PROJ, 'PM-Menu.mp3'), banks=14, gapk=kmenu)           # 28.7 s, loops
    mus_pm = music.track('pm', os.path.join(PROJ, 'PM.wav'), gapk=kpuz)                              # 85 banks, loops
    for t in (mus_jingle, mus_menu, mus_pm):
        for k in range(0, len(t), 16384):
            banks.append(t[k:k + 16384])
    MENU_S = MUSIC0; PM_S = MENU_S + len(mus_menu) // 16384; PM_E = PM_S + len(mus_pm) // 16384
    assert len(banks) == PM_E and len(banks) <= VIDEO0, (len(banks), PM_E)
    tvbase = tvn = 0
    tvb = []
    if '--titlevideo' in sys.argv:                  # a video in the letters of the title, with the music in the same stream (tools/title_video.py, game/tvplay.inc)
        import title_video
        tvv = os.path.join(PROJ, 'Videos', 'PM-LOGO.mp4')
        nf = int(arg('--titleframes', '0')) or title_video.frames_of(tvv)
        tvw, tvb, tvn, _ = title_video.build(tvv, 0.0, nf, None, None, os.path.join(PROJ, 'PM-Menu.mp3'), encode=title_video.encode_parallel)
        banks[WELCOME] = tvw
        if ascii16:                                 # ASCII16: the stream sits behind the music; NEO16: at the start of the video banks
            tvbase = len(banks)
            banks += tvb
            tvb = []
        else:
            tvbase = VIDEO0
    if '--assets-only' in sys.argv:
        return

    def load(c):
        f = os.path.join(PROJ, 'work', ('lite_' if lite else '') + 'clip%02d_bytes.npz' % c)
        if not os.path.exists(f):
            f = os.path.join(PROJ, 'work', 'clip%02d_bytes.npz' % c)
        d = np.load(f)
        lim = 40 if quick else (PLR_BANK - len(banks) if ascii16 else None)      # ASCII16: the frames have to fit in the banks behind the music
        return d['pat'][:lim], d['col'][:lim]
    n = [len(load(c)[0]) for c in clips]
    base = []; b = len(banks) if ascii16 else VIDEO0 + len(tvb)
    for k in range(len(clips)):
        base.append(b); b += n[k]
    assert b <= (PLR_BANK if ascii16 else 4096 if lite else 16384), b
    subprocess.run([sys.executable, os.path.join(HERE, 'gen_slots.py')], check=True, capture_output=True)
    clock = json.load(open(os.path.join(HERE, 'clock.json')))
    gen = 'WELCOME equ %d\nFONY equ %d\nHOWTO equ %d\nCREDITS equ %d\nSELFTEST equ %d\n' % (WELCOME, FONY, HOWTO, CREDITS, SELFTEST)
    open(os.path.join(PROJ, 'game', 'cfg.inc'), 'w').write('ASCII16 equ %d\nDIAG equ %d\nFREE equ %d\nTITLEVIDEO equ %d\nTVBANK equ %d\nTVFRAMES equ %d\nPLR_BANK equ %d\nTIETONLY equ 0\n' % (1 if ascii16 else 0, 1 if '--diag' in sys.argv else 0, 0 if '--locked' in sys.argv else 1, 1 if tvn else 0, tvbase, tvn, PLR_BANK))
    open(os.path.join(PROJ, 'game', 'clk.inc'), 'w').write('MDELAY equ %d\nFI_PAL equ %d\nFI_NTSC equ %d\n' % (clock['MDELAY'], clock['FI_PAL'], clock['FI_NTSC']))
    gen += 'mustab:\n        dw %d,%d\n        db 1,%d,%d,%d\n        dw %d,%d\n        db 1,%d,%d,%d\n        dw %d,%d\n        db 0,0,0,0\n' % (MENU_S, PM_S, kmenu, kmenub, kmenuc, PM_S, PM_E, kpuz, kpuzb, kpuzc, JINGLE, JINGLE + 2)
    gen += 'vextra: db %d\n' % (1 if lite else 0)
    gen += 'cliptab:\n' + ''.join('        dw %d,%d\n' % (base[k], n[k]) for k in ctab) + 'ptab:\n' + ''.join('        db %d,%d,%d,%d\n' % PTAB[N] for N in SIZES)
    ar = arrows()
    for nm in ('l', 'r'):
        gen += 'arrow_%s:\n' % nm + ''.join('        db ' + ','.join(str(x) for x in ar[nm][i:i + 16]) + '\n' for i in range(0, 128, 16))
    gdir = os.path.join(PROJ, 'game')
    open(os.path.join(gdir, 'gen.inc'), 'w').write(gen)
    pt = ''
    for s, t in enumerate(music.fade_sets()):
        for ch, nm in enumerate('ABC'):
            vals = [x[ch] for x in t]
            pt += ('tabA:\n' if s == 0 and ch == 0 else '') + ''.join('        db ' + ','.join(str(v) for v in vals[i:i + 16]) + '\n' for i in range(0, 256, 16))
    open(os.path.join(gdir, 'psgtab.inc'), 'w').write(pt)
    open(os.path.join(gdir, 'plrsize.inc'), 'w').write('PLR_SIZE equ 0\n')
    r = subprocess.run([SJASM, '--nologo', 'plr.asm'], cwd=gdir, capture_output=True, text=True)      # the player block (RAM resident)
    if r.returncode != 0:
        print(r.stdout + r.stderr)
        sys.exit('assembly of the player failed')
    plr = open(os.path.join(gdir, 'plr.bin'), 'rb').read()
    assert len(plr) <= 16384
    open(os.path.join(gdir, 'plrsize.inc'), 'w').write('PLR_SIZE equ %d\n' % len(plr))
    r = subprocess.run([SJASM, '--nologo', 'pm.asm'], cwd=gdir, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout + r.stderr)
        sys.exit('assembly failed')
    r = subprocess.run([SJASM, '--nologo', 'ovl.asm'], cwd=gdir, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout + r.stderr)
        sys.exit('assembly of the overlay failed')
    ovl = open(os.path.join(gdir, 'ovl.bin'), 'rb').read()
    assert len(ovl) == 16384 and len(banks) < PLR_BANK
    code = open(os.path.join(gdir, 'pm.bin'), 'rb').read()
    assert len(code) == 16384
    with open(out, 'wb') as f:
        f.write(code)
        for bk in banks[1:]:
            f.write(bk)
        if ascii16:                     # the frames follow the music
            for k, c in enumerate(clips):
                pat, col = load(c)
                for j in range(n[k]):
                    f.write(frame_bytes(pat[j], col[j]))
        f.write(bytes([0xFF]) * 16384 * (PLR_BANK - len(banks) - (sum(n) if ascii16 else 0)))
        f.write(plr + bytes([0xFF]) * (16384 - len(plr)))      # bank PLR_BANK: the player block for the RAM
        f.write(ovl)                    # bank VIDEO0 - 1 = OVLB
        for bk in tvb:                  # the stream of the title video (NEO16)
            f.write(bk)
        for k, c in enumerate([] if ascii16 else clips):
            pat, col = load(c)
            for j in range(n[k]):
                f.write(frame_bytes(pat[j], col[j]))
    free = 0x3EE0 - len(code[:0x3EE0].rstrip(b'\xff'))
    print('ROM', out, os.path.getsize(out) // 1024 // 1024, 'MB,', b, 'banks,', sum(n), 'frames, curve', curve, ', free in the code bank:', free, 'bytes')


if __name__ == '__main__':
    main()
