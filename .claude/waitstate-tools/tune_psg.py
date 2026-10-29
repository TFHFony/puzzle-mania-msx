"""tune the burns (heads.inc) of the PSG work slots against the game: build a test ROM, measure the slot intervals (slotmeas.py), adjust.  python tune_psg.py rounds"""
import subprocess, sys, os, re
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import headsutil as H, slotmeas
PROJ = r'F:\MSX Projects\PMdev26'
ROM = r'F:\MSX Projects\PMdev26\.claude\waitstate-tools\wip\PuzzleMania_keys_TEST.rom'
TARGET = 446.6
def build():
    r = subprocess.run([sys.executable, os.path.join(PROJ, 'tools', 'build_game.py'), '--out', ROM, '--titlevideo', '--msx2pal', '--scc'], capture_output=True, text=True, cwd=PROJ)
    if r.returncode: print(r.stdout[-1500:], r.stderr[-1500:]); sys.exit('build failed')
def one():
    pcs = set(slotmeas.first_write_pcs())
    ev = slotmeas.measure(ROM)
    frames = []; cur = None
    for k, a, t in ev:
        if k == 'M': cur = []; frames.append(cur)
        elif k == 'W' and cur is not None and int(a, 16) in pcs: cur.append(float(t) * 3579545)
    res = [np.diff(f) for f in frames[1:-1]]
    n = min(len(r) for r in res)
    return np.median(np.array([r[:n] for r in res]), 0)
def solve(want):
    best = None
    for b in range(1, 40):
        for n in range(0, 5):
            e = abs(14 * b + 3 + 5 * n - want)
            if best is None or e < best[0]: best = (e, b, n)
    return best[1], best[2]
if __name__ == '__main__':
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    for r in range(rounds):
        build()
        iv = one()
        d = H.load()
        ns = len(iv)
        bad = [(i + 1, iv[i]) for i in range(ns) if abs(iv[i] - TARGET) > 4]
        print('round %d: %d slots, %d off: %s' % (r, ns, len(bad), ' '.join('%d:%.0f' % x for x in bad)), flush=True)
        if not bad: break
        for i, m in bad:
            cur = 14 * d['B%d' % i] + 3 + 5 * d['N%d' % i]
            b, n = solve(cur + (TARGET - m))
            print('   slot %d: %.0f -> burn %d -> B%d N%d (%d)' % (i, m, cur, b, n, 14 * b + 3 + 5 * n))
            d['B%d' % i], d['N%d' % i] = b, n
        H.save(d, max(int(k[1:]) for k in d if re.match(r'B\d+$', k)))
