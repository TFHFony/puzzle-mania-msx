"""Build everything from the sources in one go:   python tools/build_all.py [--fresh] [--only 128|64]
  1. FONY logo screen          (assets/fony_disk: the logo of the old disk -> work/fony_disk.bin, work/fony5.bin, game/fonyov.inc; assets/fony_jingle.wav = its jingle)
  2. video clips               (full 10 fps + shortened 8.33 fps with fade-out) and the candidate stills, only when missing
  3. the ROMs                  PuzzleMania_128MB.rom (full length clips, a video in the letters of the title), PuzzleMania_64MB.rom (shortened clips, the photo in the title)
  4. PuzzleMania_checksums.txt (sizes and MD5)
The game itself is game/pm.asm (+ includes), assembled with sjasmplus by build_game.py."""
import os, sys, subprocess, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
PY = sys.executable


def run(*args):
    print('>', ' '.join(os.path.basename(a) if os.path.sep in a else a for a in args), flush=True)
    subprocess.run([PY] + list(args), check=True, cwd=PROJ)


def main():
    fresh = ['--fresh'] if '--fresh' in sys.argv else []
    only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None
    if not os.path.exists(os.path.join(PROJ, 'work', 'fony_disk.bin')) or not os.path.exists(os.path.join(PROJ, 'game', 'fonyov.inc')):
        run(os.path.join(HERE, 'fony_intro.py'))
    os.makedirs(os.path.join(PROJ, 'work', 'stills'), exist_ok=True)
    if not os.path.exists(os.path.join(PROJ, 'work', 'stills', 'clip09_7_src.png')):
        run(os.path.join(HERE, 'stills.py'))
    for i in (0, 1, 2, 3, 4, 5, 7, 8, 9):
        if not os.path.exists(os.path.join(PROJ, 'work', 'clip%02d_bytes.npz' % i)):
            run(os.path.join(HERE, 'encode_clips.py'))
            break
    for i in (0, 1, 2, 3, 4, 5, 7, 8, 9):
        if not os.path.exists(os.path.join(PROJ, 'work', 'lite_clip%02d_bytes.npz' % i)):
            run(os.path.join(HERE, 'encode_clips.py'), '--lite')
            break
    jobs = [('128', 'PuzzleMania_128MB.rom', ['--titlevideo', '--msx2pal', '--scc']), ('64', 'PuzzleMania_64MB.rom', ['--lite'])]
    lines = []
    for key, name, opts in jobs:
        if only and only != key:
            continue
        run(os.path.join(HERE, 'build_game.py'), '--out', os.path.join(PROJ, name), *opts, *fresh)
        fresh = []
        data = open(os.path.join(PROJ, name), 'rb').read()
        lines.append('%-28s %12d bytes  md5 %s' % (name, len(data), hashlib.md5(data).hexdigest()))
    if not only:
        open(os.path.join(PROJ, 'PuzzleMania_checksums.txt'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
