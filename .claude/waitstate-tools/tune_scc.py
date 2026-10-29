"""tune the burns (tools/scc16.json b1 / b2) of the SCC player slots against the game: build a test ROM, measure the intervals of the frequency writes (A->B, B->A' of every slot), adjust.  python tune_scc.py rounds"""
import subprocess, sys, os, json, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = r'F:\MSX Projects\PMdev26'
ROM = os.path.join(HERE, 'wip', 'PuzzleMania_keys_TEST.rom')
CFG = os.path.join(PROJ, 'tools', 'scc16.json')
HALF = 446.025 / 2
def build():
    r = subprocess.run([sys.executable, os.path.join(PROJ, 'tools', 'build_game.py'), '--out', ROM, '--titlevideo', '--msx2pal', '--scc'], capture_output=True, text=True, cwd=PROJ)
    if r.returncode: print(r.stdout[-1500:], r.stderr[-1500:]); sys.exit('build failed')
def measure():
    out = os.path.join(HERE, 'sct.txt').replace(chr(92), '/')
    if os.path.exists(out): os.remove(out)
    env = dict(os.environ, T0='46', OUT=out)
    p = subprocess.Popen([r'C:\Program Files\openMSX\openmsx.exe', '-machine', 'Philips_NMS_8250', '-cart', ROM, '-romtype', 'NEO-16', '-ext', 'scc', '-script', os.path.join(HERE, 'scctune.tcl')], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = time.time()
    for chk in (20, 40, 60, 90):
        while time.time() - t0 < chk and p.poll() is None and not os.path.exists(out): time.sleep(1)
        print('  check at %ds: running=%s output=%s' % (chk, p.poll() is None, os.path.exists(out)), flush=True)
        if os.path.exists(out) or p.poll() is not None: break
    time.sleep(1)
    if p.poll() is None: p.kill(); print('  killed')
    frames = []; cur = None
    for l in open(out).read().splitlines():
        k, t = l.split()
        if k == 'M': cur = []; frames.append(cur)
        elif cur is not None: cur.append(float(t) * 3579545)
    res = [np.diff(f) for f in frames[1:-1]]
    n = min(len(r) for r in res)
    return np.median(np.array([r[:n] for r in res]), 0)
if __name__ == '__main__':
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    for r in range(rounds):
        build()
        ns = int(open(os.path.join(PROJ, 'game', 'slots_ns.txt')).read())
        iv = measure()
        cfg = json.load(open(CFG))
        bad = []
        for i in range(1, ns + 1):
            if 2 * i - 1 >= len(iv): break
            m1, m2 = iv[2 * i - 2], iv[2 * i - 1]
            for h, m in ((1, m1), (2, m2)):
                if abs(m - HALF) > 3.5: bad.append((i, h, m))
        print('round %d: %d slots (%d intervals), %d halves off: %s' % (r, ns, len(iv), len(bad), ' '.join('%d.%d:%.0f' % x for x in bad)), flush=True)
        if not bad: break
        for i, h, m in bad:
            key = 'b%d' % h
            cur = cfg[key].get(str(i), 0.0)
            cfg[key][str(i)] = max(0.0, cur + HALF - m)
        json.dump(cfg, open(CFG, 'w'), indent=1)
