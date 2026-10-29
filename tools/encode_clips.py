"""Encode the clips to SCREEN 2 frame data (pat/col per frame) with the msx1-video-player encoder.
  encode_clips.py [clip id ...]          full clips, 10 fps          -> work/clipNN_bytes.npz        (128 MB ROM)
  encode_clips.py --lite [clip id ...]   shortened, 50/6 fps, fade-out -> work/lite_clipNN_bytes.npz  (64 MB ROM, all clips <= 60 MB)
clip 6 (Oops2) is not used any more.
"""
import os, sys, subprocess, time
import numpy as np
import multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, r'F:\MSX Projects\Dev27\msx1-video-player\tools')
import msx1_video as V
H, W = 192, 256
CLIPS = ['clip.mp4', 'Easter2025.mp4', 'FH.mp4', 'File-Hunter-25.mp4', 'Fony-35.mp4', 'MSXdev-20.mp4', 'Oops2.mp4', 'PM.m4v', 'Puzzle.mp4',
         'www.file-hunter.com2022.mp4', 'STEF-1.mp4']
USED = [0, 10, 2, 3, 4, 5, 7, 8, 9, 1]      # photo p = clip USED[p]
GRADE = {10: 'eq=saturation=1.2:contrast=1.05'}                            # ffmpeg filter (black level / saturation / contrast) in front of the encoder, per clip
FPS = 10
LITE_FPS = 50 / 6                           # one frame per 6 fields on a 50 Hz machine (8.33 fps; 8.57 fps on 60 Hz with 7 fields)
LITE_BUDGET = 5100                          # frames: 4 frames of 12 KB are packed in 3 banks, so about 3830 banks of 16 KB (60 MB)
FADE = 1.5                                  # seconds


def duration(i):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', os.path.join(PROJ, 'Videos', CLIPS[i])], capture_output=True, text=True)
    return float(r.stdout)


def lite_plan():
    """seconds and frames per used clip: every clip shortened by the same ratio so that all together fit the budget"""
    d = {i: duration(i) for i in USED}
    ratio = min(1.0, LITE_BUDGET / (LITE_FPS * sum(d.values())))
    return {i: (d[i] * ratio, int(d[i] * ratio * LITE_FPS)) for i in USED}


def extract(i, lite):
    src = os.path.join(PROJ, 'Videos', CLIPS[i])
    crop = "crop=w='min(iw,ih*4/3)':h='min(ih,iw*3/4)':x='(iw-out_w)*0.5':y='(ih-out_h)/2',scale=256:192:flags=area,hqdn3d=3:3:8:6"
    if GRADE.get(i):
        crop += ',' + GRADE[i]
    if lite:
        sec, n = lite_plan()[i]
        out = os.path.join(PROJ, 'work', 'lite_clip%02d_frames.rgb' % i)
        vf = crop + ",fps=%.6f,fade=t=out:st=%.3f:d=%.3f" % (LITE_FPS, sec - FADE, FADE)
        extra = ['-t', '%.3f' % sec, '-frames:v', str(n)]
    else:
        out = os.path.join(PROJ, 'work', 'clip%02d_frames.rgb' % i)
        vf = crop + ",fps=%d" % FPS
        extra = []
    if not os.path.exists(out):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-an', '-vf', vf] + extra + ['-pix_fmt', 'rgb24', '-f', 'rawvideo', out], check=True)
    return out, os.path.getsize(out) // (H * W * 3)


def main():
    args = sys.argv[1:]
    lite = '--lite' in args
    idx = [int(a) for a in args if a != '--lite'] or USED
    if lite:
        plan = lite_plan()
        print({i: (round(s, 1), n) for i, (s, n) in plan.items()}, 'frames', sum(n for _, n in plan.values()), flush=True)
    for i in idx:
        f = os.path.join(PROJ, 'work', ('lite_' if lite else '') + 'clip%02d_bytes.npz' % i)
        if os.path.exists(f):
            continue
        t0 = time.time()
        frames, n = extract(i, lite)
        tasks = [(frames, n, s, min(n, s + 38), 'col15') for s in range(0, n, 38)]
        with mp.Pool(22) as pool:
            res = sorted(pool.imap_unordered(V.work, tasks), key=lambda r: r[0])
        np.savez(f, pat=np.concatenate([r[1] for r in res]), col=np.concatenate([r[2] for r in res]))
        os.remove(frames)
        print('clip', i, CLIPS[i], n, 'frames', '%.0fs' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    mp.freeze_support()
    main()
