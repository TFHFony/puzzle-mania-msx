"""Test ROM (ASCII16, compact): the FONY logo, then the PUZZLE MANIA title with a video in the letters and the music (menu music), until SPACE / fire; then again.
   python tools/build_tiet.py Videos/PM-LOGO.mp4 TIET1.ROM
Banks: 0 code | 1 title picture (frame 0) | 2 FONY | 3 self test | 4 player block | 5.. the stream of the title video (one bank per frame, tools/title_video.py)."""
import os, sys, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
os.environ['PSG_CURVE'] = 'joint'
sys.path.insert(0, HERE)
sys.path.insert(0, r'F:\MSX Projects\Dev27\msx1-video-player\tools')
import numpy as np
from PIL import Image


def main(video, out):
    import build_game as B
    import title_video, music
    from concurrent.futures import ProcessPoolExecutor
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', video], capture_output=True, text=True)
    dur = float(r.stdout)
    fps = title_video.SAMPLE_RATE / title_video.IT_FRAME
    n = int(dur * fps)
    if len(sys.argv) > 3:
        n = min(n, int(sys.argv[3]))
    assert 5 + n <= 256, n

    welcome, stream, n, _ = title_video.build(video, 0.0, n, None, None, os.path.join(PROJ, 'PM-Menu.mp3'), encode=title_video.encode_parallel)
    gdir = os.path.join(PROJ, 'game')
    subprocess.run([sys.executable, os.path.join(HERE, 'gen_slots.py')], check=True, capture_output=True)
    clock = json.load(open(os.path.join(HERE, 'clock.json')))
    open(os.path.join(gdir, 'cfg.inc'), 'w').write('ASCII16 equ 1\nDIAG equ 0\nFREE equ 1\nTITLEVIDEO equ 1\nTVBANK equ 5\nTVFRAMES equ %d\nPLR_BANK equ 4\nTIETONLY equ 1\n' % n)
    open(os.path.join(gdir, 'clk.inc'), 'w').write('MDELAY equ %d\nFI_PAL equ %d\nFI_NTSC equ %d\n' % (clock['MDELAY'], clock['FI_PAL'], clock['FI_NTSC']))
    gen = 'WELCOME equ 1\nFONY equ 2\nHOWTO equ 0\nCREDITS equ 0\nSELFTEST equ 3\n'
    gen += 'mustab:\n' + '        dw 0,0\n        db 0,0,0,0\n' * 3
    gen += 'vextra: db 0\ncliptab:\n' + '        dw 0,0\n' * 10 + 'ptab:\n' + ''.join('        db %d,%d,%d,%d\n' % B.PTAB[N] for N in B.SIZES)
    ar = B.arrows()
    for nm in ('l', 'r'):
        gen += 'arrow_%s:\n' % nm + ''.join('        db ' + ','.join(str(x) for x in ar[nm][i:i + 16]) + '\n' for i in range(0, 128, 16))
    open(os.path.join(gdir, 'gen.inc'), 'w').write(gen)
    pt = ''
    for s, t in enumerate(music.fade_sets()):
        for ch, nm in enumerate('ABC'):
            vals = [x[ch] for x in t]
            pt += ('tabA:\n' if s == 0 and ch == 0 else '') + ''.join('        db ' + ','.join(str(v) for v in vals[i:i + 16]) + '\n' for i in range(0, 256, 16))
    open(os.path.join(gdir, 'psgtab.inc'), 'w').write(pt)
    subprocess.run([sys.executable, os.path.join(HERE, 'gen_tvplay.py')], check=True)
    open(os.path.join(gdir, 'plrsize.inc'), 'w').write('PLR_SIZE equ 0\n')
    for asm in ('plr.asm',):
        r = subprocess.run([B.SJASM, '--nologo', asm], cwd=gdir, capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(r.stdout + r.stderr)
    plr = open(os.path.join(gdir, 'plr.bin'), 'rb').read()
    open(os.path.join(gdir, 'plrsize.inc'), 'w').write('PLR_SIZE equ %d\n' % len(plr))
    r = subprocess.run([B.SJASM, '--nologo', 'pm.asm'], cwd=gdir, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(r.stdout + r.stderr)
    code = open(os.path.join(gdir, 'pm.bin'), 'rb').read()
    assert len(code) == 16384
    fony = B.pad(open(os.path.join(PROJ, 'work', 'fony_copper.bin'), 'rb').read())
    with open(out, 'wb') as f:
        f.write(code)
        f.write(welcome)
        f.write(fony)
        f.write(B.pad(b'NEO16OK!'))
        f.write(plr + bytes([0xFF]) * (16384 - len(plr)))
        for bk in stream:
            f.write(bk)
    print('ROM', out, os.path.getsize(out) // 1024, 'KB,', 5 + n, 'banks,', n, 'video frames')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
