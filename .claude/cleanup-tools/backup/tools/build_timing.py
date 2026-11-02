"""Timing test ROM (64 KB, ASCII16) from game/timing.asm:   python tools/build_timing.py [out.rom]"""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from build_game import SJASM
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PROJ, 'PuzzleMania_TIMING_ASCII16.rom')
r = subprocess.run([SJASM, '--nologo', 'timing.asm'], cwd=os.path.join(PROJ, 'game'), capture_output=True, text=True)
if r.returncode != 0:
    sys.exit(r.stdout + r.stderr)
code = open(os.path.join(PROJ, 'game', 'timing.bin'), 'rb').read()
assert len(code) == 16384
open(out, 'wb').write(code + bytes([0xAA]) * 16384 * 3)
print('written', out)
