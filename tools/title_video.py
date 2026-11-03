"""Title screen with a full colour video in the letters AND the music in one stream (test): the player is game/tvplay.inc (tools/gen_tvplay.py).
The stream of a frame (one 16 KB ROM bank per frame, 1562 iterations of 9 bytes; an iteration = 1 sample byte for the PSG + 8 bytes for the VDP):
  H1, H2:       1 sample byte each (bank switch, SPACE check, joystick check)
  per character row 0..23:  pattern row (32 iterations = 256 bytes), colour row (32 iterations), 1 sample byte (the end of the row)
The pattern row and the colour row of a character row follow each other, so that the picture never has new patterns with old colours for more than a row.
  build(video, start, nframes, coded, lift, music_path) -> (welcome bank, stream banks, number of frames, frame data)"""
import os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)

IT_FRAME = 2 + 24 * (32 + 32 + 1)            # iterations (= sample bytes) of a frame
SAMPLE_RATE = 3579545.0 / 446                # Hz
TITLE_GRADE = 'eq=saturation=1.2:contrast=1.05'      # look B of the STEF-1 clip (black level / saturation / contrast), in front of the colour steps of _enc
FADE_OUT = 0.0                               # s: the title video fades to black at its end (0: no fade, the last shot falls apart as a jigsaw: tools/jigsaw.py)
SAMPLE_RATE_PSG = int(round(SAMPLE_RATE))      # 8026 Hz: what the loop of game/tvplay.inc plays
PSG_FRAME_CYCLES = IT_FRAME * 446            # one video frame of the PSG loop (game/tvplay.inc)
SCC_FRAME_CYCLES = 719490                    # one video frame of the SCC loop (game/tvplay16.inc: 1612 iterations, the address iterations and the frame ends take more; measured in openMSX)
SAMPLE_RATE_SCC = int(round(3224 * 3579545.0 / SCC_FRAME_CYCLES))      # 16040 Hz: what the loop of game/tvplay16.inc plays on average
FPS16 = 3579545.0 / SCC_FRAME_CYCLES         # so the frames of the SCC video are cut from the clip at this rate: the picture runs as fast as in the PSG video
TITLE_START = 5.0                            # s: where the title video starts in Videos/STEF-1.mp4 (it runs for the length of the song)


def letter_mask():
    """256x192 bool: the pixels of the letters (the same drawing as the normal title)"""
    mask = Image.new('L', (256, 192), 0)
    font = ImageFont.truetype(r'C:\Windows\Fonts\impact.ttf', 400)
    for word, (x0, y0, x1, y1) in (('PUZZLE', (5, 5, 251, 91)), ('MANIA', (5, 101, 251, 187))):
        full = []
        for ch in word:
            g = Image.new('L', (800, 700), 0)
            ImageDraw.Draw(g).text((50, 20), ch, font=font, fill=255)
            full.append(g)
        ytop = min(g.getbbox()[1] for g in full); ybot = max(g.getbbox()[3] for g in full)       # one vertical range for the whole word: the baseline stays where it is
        glyphs = [g.crop((g.getbbox()[0], ytop, g.getbbox()[2], ybot)) for g in full]            # (the round U sticks out below the baseline, it must not move up)
        gap = 45
        H = ybot - ytop
        big = Image.new('L', (sum(g.width for g in glyphs) + gap * (len(glyphs) - 1), H), 0)
        x = 0
        for g in glyphs:
            big.paste(g, (x, 0)); x += g.width + gap
        mask.paste(big.resize((x1 - x0, y1 - y0), Image.LANCZOS), (x0, y0))
    return np.asarray(mask) >= 128


def extract(video, start, seconds, fps):
    vf = "crop=w='min(iw,ih*4/3)':h='min(ih,iw*3/4)':x='(iw-out_w)*0.5':y='(ih-out_h)/2',scale=256:192:flags=area,hqdn3d=3:3:8:6,fps=%.5f" % fps + (',' + TITLE_GRADE if TITLE_GRADE else '')
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(start), '-t', str(seconds), '-i', video, '-an', '-vf', vf, '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'],
                       capture_output=True, check=True)
    a = np.frombuffer(r.stdout, np.uint8)
    n = len(a) // (192 * 256 * 3)
    return a[:n * 192 * 256 * 3].reshape(n, 192, 256, 3)


def build(video, start=7.0, nframes=24, coded=None, lift=None, music_path=None, encode=None):
    import music
    fps = SAMPLE_RATE / IT_FRAME
    m = letter_mask()
    frames = extract(video, start, nframes / fps + 0.3, fps)[:nframes]
    assert len(frames) == nframes, len(frames)
    if encode:                                              # (parallel: build_tiet.py)
        datas = encode(list(frames))
        assert all(len(d) == 12288 for d in datas)
    else:
        datas = []
        for k, f in enumerate(frames):
            img = np.zeros((192, 256, 3), np.uint8)
            L = np.asarray(lift(Image.fromarray(f)))
            img[m] = L[m]
            d, rend = coded(img, (~m).astype(np.int8))           # 6144 pattern bytes + 6144 colour bytes in VRAM order
            assert len(d) == 12288
            datas.append(d)
            print('title frame', k, flush=True)
    os.makedirs(os.path.join(PROJ, 'work', 'tv'), exist_ok=True)
    np.save(os.path.join(PROJ, 'work', 'tv', 'frames.npy'), np.array([np.frombuffer(d, np.uint8) for d in datas]))
    n_samples = nframes * IT_FRAME
    x = music.decode(music_path, n_samples / SAMPLE_RATE_PSG + 0.05, fade=0.12, rate=SAMPLE_RATE_PSG)[:n_samples]      # decoded at the rate that the loop plays it: the song has its true speed (like the menu music: 8000 Hz decoded, 8000 Hz played)
    lv, _ = music.levels()
    snd = music.quantise(x, lv)
    if len(snd) < n_samples:
        snd = np.concatenate([snd, np.full(n_samples - len(snd), int(np.abs(np.asarray(lv) - 0.5).argmin()), np.uint8)])
    banks = []
    a = 0
    for f in range(nframes):
        P = datas[f][:6144]; C = datas[f][6144:]
        s = bytearray()

        def aud():
            nonlocal a
            s.append(int(snd[a])); a += 1
        aud(); aud()                                        # H1, H2
        for cy in range(24):
            for src in (P, C):
                row = src[cy * 256:(cy + 1) * 256]
                for k in range(32):
                    aud(); s.extend(row[k * 8:k * 8 + 8])
            aud()                                           # the end of the row
        assert len(s) == IT_FRAME + 24 * 512, len(s)
        banks.append(bytes(s) + bytes([0xFF]) * (16384 - len(s)))
    welcome = datas[0] + bytes([0xFF]) * (16384 - 12288)
    return welcome, banks, nframes, datas


def frames16(video, start, nframes):
    """the pictures for the SCC video: nframes frames cut at FPS16 (the SCC frame is longer than a frame of the PSG video)"""
    frames = extract(video, start, nframes / FPS16 + 0.3, FPS16)[:nframes]
    assert len(frames) == nframes, len(frames)
    datas = encode_parallel(list(frames), FPS16)
    assert all(len(d) == 12288 for d in datas)
    return datas


def build16(datas, nframes, music_path):
    """the stream for the SCC player (game/tvplay16.inc, tools/gen_tvplay16.py): 16 kHz music, 2 signed sample bytes per iteration; the iterations: H1, H2, per row
    (pattern, colour): an address iteration + 32 iterations with 8 video bytes, then an end-of-row iteration; F1, F2.  -> list of banks (one per frame)"""
    import music
    it16 = 2 + 24 * (2 * 33 + 1) + 2
    n_samples = nframes * it16 * 2
    x = music.decode(music_path, n_samples / SAMPLE_RATE_SCC + 0.05, fade=0.12, rate=SAMPLE_RATE_SCC)[:n_samples]       # (the rate of the loop: SCC_FRAME_CYCLES per frame of 3224 samples)
    snd = music.quantise(x, np.linspace(0, 1, 256))
    if len(snd) < n_samples:
        snd = np.concatenate([snd, np.full(n_samples - len(snd), 128, np.uint8)])
    snd = (snd ^ 0x80).astype(np.uint8)                       # signed bytes, silence = 0
    banks = []
    a = 0
    for f in range(nframes):
        P = datas[f][:6144]; C = datas[f][6144:]
        s = bytearray()

        def aud():
            nonlocal a
            s.append(int(snd[a])); s.append(int(snd[a + 1])); a += 2
        aud(); aud()                                        # H1, H2
        for cy in range(24):
            for src in (P, C):
                row = src[cy * 256:(cy + 1) * 256]
                aud()                                       # the address iteration
                for k in range(32):
                    aud(); s.extend(row[k * 8:k * 8 + 8])
            aud()                                           # the end of the row
        aud(); aud()                                        # F1, F2
        assert len(s) == it16 * 2 + 24 * 512, len(s)
        banks.append(bytes(s) + bytes([0xFF]) * (16384 - len(s)))
    return banks


# ---- the colours (tools/build_tiet.py, build_game.py --titlevideo): warm palette only, one contrast stretch per clip, saturation and gamma
WARM = {0, 1, 6, 8, 9, 10, 11, 13, 14, 15}       # black, dark red, medium red, light red, dark yellow, light yellow, magenta, grey, white: no greens and blues (they only gave speckles)
SAT, GAMMA = 1.5, 0.85


def grade(frame, lo, hi):
    """the look of the title video: one contrast stretch for the whole clip (no flicker), saturation, gamma"""
    from PIL import ImageEnhance
    a = np.clip((frame.astype(np.float32) - lo) / (hi - lo), 0, 1)
    im = ImageEnhance.Color(Image.fromarray((a * 255 + 0.5).astype(np.uint8))).enhance(SAT)
    return (np.clip(np.asarray(im).astype(np.float32) / 255, 0, 1) ** GAMMA * 255 + 0.5).astype(np.uint8)


LAST_GRADED = None                           # the last shot of the clip, whole picture, graded like the frames (set by encode_parallel: the jigsaw outro grows it out of the letters)


def _enc(args):
    sys.path.insert(0, r'F:\MSX Projects\Dev27\msx1-video-player	ools')
    import screen4_sim as S, stills
    import build_game as B
    from PIL import ImageEnhance
    frame, lo, hi, fade = args
    keep = [i for i in range(len(S.PI)) if int(S.PI[i]) in WARM and int(S.PJ[i]) in WARM]
    stills.PI = S.PI[keep]; stills.PJ = S.PJ[keep]
    m = letter_mask()
    L = grade(frame, lo, hi)
    img = np.zeros((192, 256, 3), np.uint8)
    img[m] = (L[m].astype(np.float32) * fade + 0.5).astype(np.uint8)       # the last FADE_OUT seconds fade to black
    d, rend = B.coded(img, (~m).astype(np.int8))
    return d


def encode_parallel(frames, fps=None):
    """the frames coded for SCREEN 2; cached (work/tvenc_<hash>.pkl: the hash covers the pictures, the settings and the coding code), the cache also restores LAST_GRADED"""
    import hashlib, pickle, inspect
    sys.path.insert(0, r'F:/MSX Projects/Dev27/msx1-video-player/tools')
    import build_game as B, screen4_sim as S, stills
    h = hashlib.md5()
    for f in frames:
        h.update(np.ascontiguousarray(f).tobytes())
    h.update(repr((fps, FADE_OUT, SAT, GAMMA, sorted(WARM), FPS16)).encode())
    h.update(inspect.getsource(B.coded).encode() + inspect.getsource(B.chars).encode() + inspect.getsource(_enc).encode() + inspect.getsource(grade).encode() + inspect.getsource(letter_mask).encode())
    for mod in (S, stills):
        h.update(repr(os.path.getmtime(mod.__file__)).encode())
    pk = os.path.join(PROJ, 'work', 'tvenc_%s.pkl' % h.hexdigest()[:16])
    global LAST_GRADED
    if os.path.exists(pk):
        datas, LAST_GRADED = pickle.load(open(pk, 'rb'))
        print('title frames: from the cache', flush=True)
        return datas
    datas = _encode_parallel(frames, fps)
    pickle.dump((datas, LAST_GRADED), open(pk, 'wb'))
    return datas


def _encode_parallel(frames, fps=None):
    from concurrent.futures import ProcessPoolExecutor
    m = letter_mask()
    lum = np.stack(frames[::3]).astype(np.float32).mean(-1)[:, m]
    lo, hi = float(np.percentile(lum, 1)), float(np.percentile(lum, 99))
    print('contrast stretch of the clip: %.0f .. %.0f' % (lo, hi), flush=True)
    global LAST_GRADED
    LAST_GRADED = grade(frames[-1], lo, hi)
    with ProcessPoolExecutor(max_workers=8) as ex:
        n = len(frames)
        fade = lambda k: min(1.0, (n - 1 - k) / (FADE_OUT * (fps or SAMPLE_RATE / IT_FRAME))) if FADE_OUT > 0 else 1.0
        return list(ex.map(_enc, [(f, lo, hi, fade(k)) for k, f in enumerate(frames)], chunksize=2))


def frames_of(video):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', video], capture_output=True, text=True)
    return int(float(r.stdout) * SAMPLE_RATE / IT_FRAME)


if __name__ == '__main__':
    import build_game as B
    w, banks, n, datas = build(os.path.join(PROJ, 'Videos', 'Puzzle.mp4'), nframes=4, coded=B.coded, lift=B.lift, music_path=os.path.join(PROJ, 'PM-Menu.mp3'))
    print(len(w), len(banks), n)
