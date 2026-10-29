"""Build the Puzzle Mania NEO16 ROM (tools/build_all.py builds all versions).
  python tools/build_game.py [--lite] [--curve ym|ay|joint] [--out file.rom] [--quick] [--fresh]
  --lite   64 MB version: shortened 8.33 fps clips with fade-out (work/lite_clipNN_bytes.npz); without it: the full clips at 10 fps
  --kmenu/--kpuz K (--kmenub/--kpuzb: frames with work after the block, --kmenuc/--kpuzc: the frame of an action) skipped samples per frame of that track; its music is coded for it (defaults 2/5/6 menu, 2/5/4 puzzle)
  --curve  PSG volume curve of the music (default: the neutral curve 'joint'; 'ym' and 'ay' are test options)
Needs work/clipNN_bytes.npz (encode_clips.py), work/stills (stills.py), work/fony_disk.bin + work/fony5.bin + game/fonyov.inc (fony_intro.py); photo choice per clip: tools/choices.json
ROM banks: 0 game | 1 + 10 p + k: photo p, k = 0 plain image + thumbnail, 1 size buttons, 2..5 thick tile lines 3x3..6x6, 6..9 thin tile lines |
           WELCOME, FONY, HOWTO x3, CREDITS, SELFTEST | title video picture, menu music, puzzle music | VIDEO0..: video frames, one per bank
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
WELCOME, FONY, HOWTO, CREDITS, SELFTEST = 101, 102, 103, 106, 107        # behind the 10 photos of 10 banks (game/equ.inc NPHOTO)
PLR_BANK = 254
TITLEV, MUSIC0 = 108, 109    # TITLEV: the first picture of the title video (the 128 MB ROM)
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


def coded(img, fix=None, pal=None):
    pat, col, rend = encode(np.asarray(img, np.float32), fix, pal)
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


def photo_banks(src_png, p=0, preview_dir=None, pal=None, thumbpal=None, look=None, btnpal=None):
    """pal: the palette of the photo (MSX2 version), thumbpal: the palette of the menu (the thumbnail)"""
    src = lift(Image.open(src_png).convert('RGB')) if look is None else look(Image.open(src_png).convert('RGB'))
    banks = []
    thumbpal = pal if thumbpal is None else thumbpal
    plain, r0 = coded(src, None, pal)
    th = Image.new('RGB', (104, 80)); th.paste(thumbnail(src, 100, 76), (2, 2))          # thumbnail 104x80, black border
    tf = np.ones((80, 104), np.int8); tf[2:78, 2:102] = 0
    tdata, rt = coded(th, tf, thumbpal)
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
        d, r = coded(a, bf, pal if btnpal is None else btnpal); btn += d; rb.append(r)
    assert len(btn) == 4 * 1728
    banks.append(pad(btn))
    rp = []
    for thin in (False, True):
        for N in SIZES:
            li, lf = lined(src, N, thin)
            d, r = coded(li, lf, pal); banks.append(pad(d)); rp.append(r)
    assert len(banks) == STRIDE
    if preview_dir:
        os.makedirs(preview_dir, exist_ok=True)
        Image.fromarray(r0).save(os.path.join(preview_dir, 'photo%d_plain.png' % p))
        Image.fromarray(rt).save(os.path.join(preview_dir, 'photo%d_thumb.png' % p))
        Image.fromarray(np.concatenate([np.concatenate(rb[:2], 1), np.concatenate(rb[2:], 1)], 0)).save(os.path.join(preview_dir, 'photo%d_buttons.png' % p))
    return banks


def welcome_image(photo_png, pal=None, look=None):
    """black screen, PUZZLE / MANIA in big capitals over the full 256x192, the letters filled with the photo"""
    photo = np.asarray(lift(Image.open(photo_png).convert('RGB')) if look is None else look(Image.open(photo_png).convert('RGB')))
    import title_video                          # (the same letters as the title video: the baseline of the word stays where it is)
    m = title_video.letter_mask()
    img = np.zeros((192, 256, 3), np.uint8)
    img[m] = photo[m]
    data, rend = coded(img, (~m).astype(np.int8), pal)
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


def packed(pat, col):
    """the frames of a clip one behind the other (12288 bytes each), padded to whole banks"""
    d = b''.join(frame_bytes(pat[j], col[j])[:12288] for j in range(len(pat)))
    return d + bytes([0xFF]) * (-len(d) % 16384)


def build_assets(choices, fresh):
    """photo banks, title, FONY, how to play, credits (cached: they take a few minutes)"""
    pk = os.path.join(PROJ, 'work', 'assets.pkl')
    key = (choices, USED, 'v4', os.path.getmtime(os.path.join(HERE, 'title_video.py')), os.path.getmtime(os.path.join(HERE, 'screens.py')), os.path.getmtime(os.path.join(PROJ, 'work', 'fony_disk.bin')))
    if os.path.exists(pk) and not fresh:
        k, banks = pickle.load(open(pk, 'rb'))
        if k == key:
            return banks
    import screens
    import palette_opt as PO1
    banks = [None]
    prev = os.path.join(PROJ, 'work', 'preview')
    for p, c in enumerate(USED):
        png = os.path.join(PROJ, 'work', 'stills', 'clip%02d_%d_src.png' % (c, choices[c]))
        banks += photo_banks(png, p, prev, look=(lambda im, k=c: PO1.adjust(im, **PO1.LOOK_CLIP[k])) if c in PO1.LOOK_CLIP else None)
        print('photo', p, 'clip', c, 'candidate', choices[c], flush=True)
    assert len(banks) == 1 + STRIDE * len(USED)
    while len(banks) < WELCOME:
        banks.append(pad(b''))
    wb, wr = welcome_image(os.path.join(PROJ, 'work', 'stills', 'clip%02d_%d_src.png' % (WELCOME_PHOTO, choices[WELCOME_PHOTO])))
    Image.fromarray(wr).save(os.path.join(prev, 'welcome.png'))
    banks.append(wb)
    banks.append(pad(open(os.path.join(PROJ, 'work', 'fony_disk.bin'), 'rb').read()))          # the FONY logo of the disk (tools/fony_intro.py)
    for n in ('howto1', 'howto2', 'howto3', 'credits'):          # howto3 is not used any more: an empty bank keeps the layout
        if n == 'howto3':
            banks.append(pad(b''))
            continue
        data, rend = screens.screen(n, coded)
        Image.fromarray(rend).resize((768, 576), Image.NEAREST).save(os.path.join(prev, n + '.png'))
        banks.append(pad(data))
    banks.append(pad(b'NEO16OK!'))
    assert len(banks) == TITLEV, len(banks)
    pickle.dump((key, banks), open(pk, 'wb'))
    return banks


def build_msx2_assets(choices, fresh):
    """MSX2 and later (128 MB ROM): the 100 photo banks again, coded for the palette of the photo (the thumbnails for the palette of the menu), and the title with the photo.
    -> (101 banks, the palette table: 23 x 32 bytes: TMS, menu, photo 0..9, title, size menus 0..9)"""
    import palette_opt as PO
    pj = PO.load()
    pk = os.path.join(PROJ, 'work', 'assets_msx2.pkl')
    key = (choices, USED, 'v4', PO.LOOK, os.path.getmtime(os.path.join(HERE, 'title_video.py')), os.path.getmtime(PO.PJSON), os.path.getmtime(os.path.join(HERE, 'stills.py')))
    pal = lambda a: np.array(a, np.float32)
    tab = PO.to_v9938(pj['tms']) + PO.to_v9938(pj['menu']) + b''.join(PO.to_v9938(x) for x in pj['photo'])
    wp = USED.index(WELCOME_PHOTO)
    tab += PO.to_v9938(pj['photo'][wp])
    tab += b''.join(PO.to_v9938(x) for x in pj['size'])               # 12..20: the size menu of every photo
    if os.path.exists(pk) and not fresh:
        k, banks = pickle.load(open(pk, 'rb'))
        if k == key:
            return banks, tab
    banks = []
    for p, c in enumerate(USED):
        png = os.path.join(PROJ, 'work', 'stills', 'clip%02d_%d_src.png' % (c, choices[c]))
        banks += photo_banks(png, p, None, pal(pj['photo'][p]), pal(pj['menu']), lambda im, k=c: PO.adjust(im, **PO.LOOK_CLIP.get(k, PO.LOOK)), pal(pj['size'][p]))
        print('msx2 photo', p, flush=True)
    wb, wr = welcome_image(os.path.join(PROJ, 'work', 'stills', 'clip%02d_%d_src.png' % (WELCOME_PHOTO, choices[WELCOME_PHOTO])), pal(pj['photo'][wp]), lambda im: PO.adjust(im, **PO.LOOK))
    os.makedirs(os.path.join(PROJ, 'work', 'preview'), exist_ok=True)
    Image.fromarray(wr).save(os.path.join(PROJ, 'work', 'preview', 'welcome_msx2.png'))
    banks.append(wb)
    assert len(banks) == 1 + STRIDE * len(USED)
    pickle.dump((key, banks), open(pk, 'wb'))
    return banks, tab


def main():
    arg = lambda name, default=None: sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default
    lite = '--lite' in sys.argv
    quick = '--quick' in sys.argv
    scc = '--scc' in sys.argv                                                   # the music goes to an SCC if there is one (a second player block in bank PLR_BANK - 1)
    ascii16 = '--ascii16' in sys.argv                                           # 4 MB test ROM for the ASCII16 mapper (8-bit banks): clip 0 behind the music, as many frames as fit
    test0 = '--only-clip0' in sys.argv or ascii16                              # test ROM: every photo plays clip 0
    clips = [0] if test0 else USED
    ctab = [0] * len(USED) if test0 else list(range(len(clips)))                # clip table entry -> clip in 'clips'
    curve = arg('--curve', 'joint')
    os.environ['PSG_CURVE'] = curve
    # skipped samples per frame of the track (the music is coded for it): idle / a frame with work after the block / the frame of an action
    kmenu, kmenub, kmenuc = int(arg('--kmenu', '2')), int(arg('--kmenub', '5')), int(arg('--kmenuc', '6'))
    kpuz, kpuzb, kpuzc = int(arg('--kpuz', '2')), int(arg('--kpuzb', '5')), int(arg('--kpuzc', '4'))
    import music
    out = arg('--out', os.path.join(PROJ, 'PuzzleMania_64MB.rom' if lite else 'PuzzleMania_128MB.rom'))
    choices = json.load(open(os.path.join(HERE, 'choices.json')))      # candidate per clip id
    banks = build_assets(choices, '--fresh' in sys.argv)
    r = subprocess.run([SJASM, '--nologo', 'wtest.asm'], cwd=os.path.join(PROJ, 'game'), capture_output=True, text=True)      # the VDP wait state test: it lives in the bank SELFTEST behind the signature (screens.asm wt_go copies it to the RAM)
    if r.returncode != 0:
        print(r.stdout + r.stderr)
        sys.exit('assembly of the wait state test failed')
    banks[SELFTEST] = pad(b'NEO16OK!'.ljust(16, bytes(1)) + open(os.path.join(PROJ, 'game', 'wtest.bin'), 'rb').read())
    banks.append(pad(b''))                                                     # TITLEV
    mus_menu = music.track('menu', os.path.join(PROJ, 'PM-Menu.mp3'), banks=14, gapk=kmenu)           # 28.7 s, loops
    mus_pm = music.track('pm', os.path.join(PROJ, 'PM.wav'), gapk=kpuz)                              # 85 banks, loops
    for t in (mus_menu, mus_pm):
        for k in range(0, len(t), 16384):
            banks.append(t[k:k + 16384])
    MENU_S = MUSIC0; PM_S = MENU_S + len(mus_menu) // 16384; PM_E = PM_S + len(mus_pm) // 16384
    assert len(banks) == PM_E and len(banks) <= VIDEO0, (len(banks), PM_E)
    tvbase = tvn = 0
    tvb = []
    if '--titlevideo' in sys.argv:                  # a video in the letters of the title, with the music in the same stream (tools/title_video.py, game/tvplay.inc)
        import title_video
        tvv = os.path.join(PROJ, 'Videos', 'STEF-1.mp4')          # from 5 s for the length of the song (title_video.TITLE_START)
        nf = int(arg('--titleframes', '0')) or title_video.frames_of(os.path.join(PROJ, 'PM-Menu.mp3'))
        tvw, tvb, tvn, tvdatas = title_video.build(tvv, title_video.TITLE_START, nf, None, None, os.path.join(PROJ, 'PM-Menu.mp3'), encode=title_video.encode_parallel)
        banks[TITLEV] = tvw                         # the photo title stays in WELCOME
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
        lim = int(arg('--clipframes', '0')) or (40 if quick else (PLR_BANK - (1 if scc else 0) - len(banks) if ascii16 else None))      # --clipframes N: a test ROM with short clips; ASCII16: the frames have to fit in the banks behind the music
        return d['pat'][:lim], d['col'][:lim]
    n = [len(load(c)[0]) for c in clips]
    base = []; b = len(banks) if ascii16 else VIDEO0 + len(tvb)
    nb = [(3 * x + 3) // 4 for x in n]                                          # the frames are packed: 4 frames of 12 KB in 3 banks
    for k in range(len(clips)):
        base.append(b); b += nb[k]
    msx2 = '--msx2pal' in sys.argv                                              # the 128 MB ROM: a palette per photo on an MSX2 or later
    PB2 = b if msx2 else 0
    msx2banks, paltab = build_msx2_assets(choices, '--fresh' in sys.argv) if msx2 else ([], b'')
    mus16 = []                                                                  # the music for the SCC player: 16 kHz, behind the MSX2 banks
    TV16 = 0
    tvn16 = 0
    if scc:
        mus_menu16 = music.track16('menu', os.path.join(PROJ, 'PM-Menu.mp3'), banks=28, gapk=kmenu)
        mus_pm16 = music.track16('pm', os.path.join(PROJ, 'PM.wav'), gapk=kpuz)
        mus16 = [t[k:k + 16384] for t in (mus_menu16, mus_pm16) for k in range(0, len(t), 16384)]
        M16_S = b + len(msx2banks); M16_P = M16_S + len(mus_menu16) // 16384; M16_E = M16_P + len(mus_pm16) // 16384
        if tvn:                                                                 # the title video for the SCC: its own stream (16 kHz music in it)
            tvn16 = int(round(tvn * title_video.PSG_FRAME_CYCLES / title_video.SCC_FRAME_CYCLES))          # the same length in time as the PSG video (an SCC frame is 3.3 % longer: fewer frames)
            tvdatas16 = title_video.frames16(tvv, title_video.TITLE_START, tvn16)
            mus16 += title_video.build16(tvdatas16, tvn16, os.path.join(PROJ, 'PM-Menu.mp3'))
            TV16 = M16_E
    EX0 = b + len(msx2banks) + len(mus16)                                       # behind everything: the FONY logo for the SCREEN 5 of an MSX2, the jingle (PSG 8 kHz: 2 banks, SCC 16 kHz: 3 banks)
    import fony_intro
    jwav = os.path.join(PROJ, 'assets', 'fony_jingle.wav')
    jing8 = music.track('fony', jwav, gapk=kmenu)
    jing16 = music.track16('fony', jwav, gapk=kmenu) if scc else b''
    jwin = os.path.join(PROJ, 'assets', 'fony_jingle_win.wav')                    # the same jingle without the silence in front: the win jingle (track 3)
    jingw8 = music.track('fonywin', jwin, gapk=kmenu)
    jingw16 = music.track16('fonywin', jwin, gapk=kmenu) if scc else b''
    extra = [fony_intro.msx2_bank()] + [t[k:k + 16384] for t in (jing8, jing16, jingw8, jingw16) for k in range(0, len(t), 16384)]
    FONY5B = EX0; J8_S = EX0 + 1; J8_E = J8_S + len(jing8) // 16384; J16_S = J8_E; J16_E = J16_S + len(jing16) // 16384; JW8_S = J16_E; JW8_E = JW8_S + len(jingw8) // 16384; JW16_S = JW8_E; JW16_E = JW16_S + len(jingw16) // 16384
    assert EX0 + len(extra) <= (PLR_BANK if ascii16 else 4096 if lite else 16384), b
    subprocess.run([sys.executable, os.path.join(HERE, 'gen_slots.py')], check=True, capture_output=True)
    subprocess.run([sys.executable, os.path.join(HERE, 'gen_slots.py'), '--scc16'], check=True, capture_output=True)
    if scc and tvn:
        subprocess.run([sys.executable, os.path.join(HERE, 'gen_tvplay16.py')], check=True, capture_output=True)
        subprocess.run([sys.executable, os.path.join(HERE, 'gen_tvplay16.py'), '--wait'], check=True, capture_output=True)       # (and the loop for a machine with a VDP wait state)
    clock = json.load(open(os.path.join(HERE, 'clock.json')))
    cscc = json.load(open(os.path.join(HERE, 'clock_scc.json')))
    gen = 'WELCOME equ %d\nFONY equ %d\nHOWTO equ %d\nCREDITS equ %d\nSELFTEST equ %d\nTITLEV equ %d\nFONY5B equ %d\n' % (WELCOME, FONY, HOWTO, CREDITS, SELFTEST, TITLEV, FONY5B)
    bnf = os.path.join(HERE, 'build_number.txt')                                  # the build number of the specs screen: counted by the full 128 MB builds only (lite, quick and test builds show none)
    official = not (lite or quick or ascii16 or test0 or arg('--clipframes') or arg('--titleframes')) and os.path.basename(out) == 'PuzzleMania_128MB.rom'
    bn = int(open(bnf).read().strip()) + 1 if official else 0
    open(os.path.join(PROJ, 'game', 'buildno.inc'), 'w').write(('sp_build: db "%s",0' % ('/ %d' % bn if bn else '')) + chr(10))
    open(os.path.join(PROJ, 'game', 'cfg.inc'), 'w').write('ASCII16 equ %d\nDIAG equ %d\nFREE equ %d\nTITLEVIDEO equ %d\nTVBANK equ %d\nTVFRAMES equ %d\nPLR_BANK equ %d\nTIETONLY equ 0\nBUILDID equ %d\nSCC equ %d\nTVBANK16 equ %d\nTVFRAMES16 equ %d\nMSX2PAL equ %d\nPBOFFS equ %d\nWELCOME2 equ %d\n' % (1 if ascii16 else 0, 1 if '--diag' in sys.argv else 0, 0 if '--locked' in sys.argv else 1, 1 if tvn else 0, tvbase, tvn, PLR_BANK, (0 if lite else 2 if arg('--clipframes') else 1), 1 if '--scc' in sys.argv else 0, TV16, tvn16 if TV16 else 0, 1 if msx2 else 0, PB2 - 1 if msx2 else 0, PB2 + STRIDE * len(USED) if msx2 else 0))
    open(os.path.join(PROJ, 'game', 'clk.inc'), 'w').write('MDELAY equ %d\nFI_PAL equ %d\nFI_NTSC equ %d\nFI_PAL_SCC equ %d\nFI_NTSC_SCC equ %d\n' % (clock['MDELAY'], clock['FI_PAL'], clock['FI_NTSC'], cscc['FI_PAL'], cscc['FI_NTSC']))
    open(os.path.join(PROJ, 'game', 'clk_scc.inc'), 'w').write('SCCPAD equ %d' % cscc['SCCPAD'] + chr(10) + 'QPAD equ %d' % cscc.get('QPAD', 18) + chr(10))
    gen += 'mustab:\n        dw %d,%d\n        db 1,%d,%d,%d\n        dw %d,%d\n        db 1,%d,%d,%d\n        dw %d,%d\n        db 0,%d,%d,%d\n        dw %d,%d\n        db 0,%d,%d,%d\n' % (MENU_S, PM_S, kmenu, kmenub, kmenuc, PM_S, PM_E, kpuz, kpuzb, kpuzc, J8_S, J8_E, kmenu, kmenub, kmenuc, JW8_S, JW8_E, kmenu, kmenub, kmenuc)
    gen += 'vextra: db %d\n' % (1 if lite else 0)
    if scc:
        gen += 'mustab_scc:\n        dw %d,%d\n        db 1,%d,%d,%d\n        dw %d,%d\n        db 1,%d,%d,%d\n        dw %d,%d\n        db 0,%d,%d,%d\n        dw %d,%d\n        db 0,%d,%d,%d\n' % (M16_S, M16_P, kmenu, kmenub, kmenuc, M16_P, M16_E, kpuz, kpuzb, kpuzc, J16_S, J16_E, kmenu, kmenub, kmenuc, JW16_S, JW16_E, kmenu, kmenub, kmenuc)
    if msx2:
        gen += 'pal_tab:\n' + ''.join('        db ' + ','.join(str(x) for x in paltab[i:i + 16]) + '\n' for i in range(0, len(paltab), 16))
    gen += 'cliptab:\n' + ''.join('        dw %d,%d\n' % (base[k], n[k]) for k in ctab) + 'ptab:\n' + ''.join('        db %d,%d,%d,%d\n' % PTAB[N] for N in SIZES)
    import menu_logo
    lg = menu_logo.logo_bytes()
    gen += 'logo_dat:' + chr(10) + ''.join('        db ' + ','.join(str(x) for x in lg[i:i + 16]) + chr(10) for i in range(0, len(lg), 16))
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
    open(os.path.join(gdir, 'plrsize.inc'), 'w').write('PLR_SIZE equ 0\nPLR_SIZE_SCC equ 0\n')
    r = subprocess.run([SJASM, '--nologo', 'plr.asm'], cwd=gdir, capture_output=True, text=True)      # the player block (RAM resident)
    if r.returncode != 0:
        print(r.stdout + r.stderr)
        sys.exit('assembly of the player failed')
    plr = open(os.path.join(gdir, 'plr.bin'), 'rb').read()
    assert len(plr) <= 16384
    plr_scc = b''
    if scc:
        r = subprocess.run([SJASM, '--nologo', '--sym=plr_scc.sym', 'plr_scc.asm'], cwd=gdir, capture_output=True, text=True)       # the player block for the SCC
        if r.returncode != 0:
            print(r.stdout + r.stderr)
            sys.exit('assembly of the SCC player failed')
        plr_scc = open(os.path.join(gdir, 'plr_scc.bin'), 'rb').read()
        assert len(plr_scc) <= 16384
    open(os.path.join(gdir, 'plrsize.inc'), 'w').write('PLR_SIZE equ %d\nPLR_SIZE_SCC equ %d\n' % (len(plr), len(plr_scc)))
    tmsp = paltab[:32] if msx2 else bytes(32)
    open(os.path.join(gdir, 'fonyov.inc'), 'w').write(fony_intro.inc() + 'tms_pal:\n' + ''.join('        db ' + ','.join(str(x) for x in tmsp[i:i + 16]) + '\n' for i in range(0, 32, 16)))
    r = subprocess.run([SJASM, '--nologo', '--sym=pm.sym', 'pm.asm'], cwd=gdir, capture_output=True, text=True)
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
                f.write(packed(pat, col))
        f.write(bytes([0xFF]) * 16384 * (PLR_BANK - 1 - len(banks) - (sum(nb) if ascii16 else 0)))
        f.write((plr_scc + bytes([0xFF]) * (16384 - len(plr_scc))) if scc else bytes([0xFF]) * 16384)      # bank PLR_BANK - 1: the player block for the SCC
        f.write(plr + bytes([0xFF]) * (16384 - len(plr)))      # bank PLR_BANK: the player block for the RAM
        f.write(ovl)                    # bank VIDEO0 - 1 = OVLB
        for bk in tvb:                  # the stream of the title video (NEO16)
            f.write(bk)
        for k, c in enumerate([] if ascii16 else clips):
            pat, col = load(c)
            f.write(packed(pat, col))
        for bk in msx2banks:            # the photos for the palette of the photo (MSX2 and later), then the title
            f.write(bk)
        for bk in mus16:                # the music for the SCC player
            f.write(bk)
        for bk in extra:                # the logo of the disk (SCREEN 5), the jingle
            f.write(bk)
    if bn:
        open(bnf, 'w').write('%d' % bn + chr(10))
        print('build number', bn)
    free = 0x3EE0 - len(code[:0x3EE0].rstrip(b'\xff'))
    print('ROM', out, os.path.getsize(out) // 1024 // 1024, 'MB,', b, 'banks,', sum(n), 'frames, curve', curve, ', free in the code bank:', free, 'bytes')


if __name__ == '__main__':
    main()
