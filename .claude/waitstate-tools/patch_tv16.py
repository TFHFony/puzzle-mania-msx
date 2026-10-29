"""one-time patch: the SCC title video gets its own frames: the same look (speed of the picture) as the PSG video although an SCC frame is 3.3 % longer"""
BS = chr(92)
P = 'F:/MSX Projects/PMdev26/tools/'
s = open(P + 'title_video.py', encoding='utf8').read()
assert 'SCC_FRAME_CYCLES' not in s
a = "TITLE_START = 5.0 "
assert s.count(a) == 1
s = s.replace(a, """PSG_FRAME_CYCLES = IT_FRAME * 446            # one video frame of the PSG loop (game/tvplay.inc)
SCC_FRAME_CYCLES = 719490                    # one video frame of the SCC loop (game/tvplay16.inc: 1612 iterations, the address iterations and the frame ends take more; measured in openMSX)
FPS16 = 3579545.0 / SCC_FRAME_CYCLES         # so the frames of the SCC video are cut from the clip at this rate: the picture runs as fast as in the PSG video
""" + a, 1)
old = """def encode_parallel(frames):
    from concurrent.futures import ProcessPoolExecutor"""
assert old in s
s = s.replace(old, """def encode_parallel(frames, fps=None):
    from concurrent.futures import ProcessPoolExecutor""")
old = "        fade = lambda k: min(1.0, (n - 1 - k) / (FADE_OUT * SAMPLE_RATE / IT_FRAME))\n"
assert old in s
s = s.replace(old, "        fade = lambda k: min(1.0, (n - 1 - k) / (FADE_OUT * (fps or SAMPLE_RATE / IT_FRAME)))\n")
old = "def build16(datas, nframes, music_path):"
assert old in s
s = s.replace(old, '''def frames16(video, start, nframes):
    """the pictures for the SCC video: nframes frames cut at FPS16 (the SCC frame is longer than a frame of the PSG video)"""
    frames = extract(video, start, nframes / FPS16 + 0.3, FPS16)[:nframes]
    assert len(frames) == nframes, len(frames)
    datas = encode_parallel(list(frames), FPS16)
    assert all(len(d) == 12288 for d in datas)
    return datas


''' + old, 1)
open(P + 'title_video.py', 'w', encoding='utf8').write(s)

b = open(P + 'build_game.py', encoding='utf8').read()
old = """            mus16 += title_video.build16(tvdatas, tvn, os.path.join(PROJ, 'PM-Menu.mp3'))
            TV16 = M16_E
"""
assert old in b
b = b.replace(old, """            tvn16 = int(round(tvn * title_video.PSG_FRAME_CYCLES / title_video.SCC_FRAME_CYCLES))          # the same length in time as the PSG video (an SCC frame is 3.3 % longer: fewer frames)
            tvdatas16 = title_video.frames16(tvv, title_video.TITLE_START, tvn16)
            mus16 += title_video.build16(tvdatas16, tvn16, os.path.join(PROJ, 'PM-Menu.mp3'))
            TV16 = M16_E
""")
old = "    TV16 = 0\n"
assert b.count(old) == 1
b = b.replace(old, "    TV16 = 0\n    tvn16 = 0\n")
old = "TV16, tvn if TV16 else 0,"
assert b.count(old) == 1
b = b.replace(old, "TV16, tvn16 if TV16 else 0,")
open(P + 'build_game.py', 'w', encoding='utf8').write(b)
print('ok')
