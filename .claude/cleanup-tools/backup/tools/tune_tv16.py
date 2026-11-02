"""Calibrate the SCC title video player (tools/tvplay16.json): both samples of an iteration 223.01 cycles apart in every kind of iteration.
Builds a small test ROM (--lite --quick --scc --titlevideo), logs the frequency writes of the SCC with their PC (t122.tcl), measures A->B and B->A' per kind
(the labels of game/pm.sym) and corrects the burns.  usage: tune_tv16.py [rounds]"""
import os, sys, re, json, subprocess, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
OPENMSX = r'C:\Program Files\openMSX\openmsx.exe'
TCL = os.path.join(PROJ, '.claude', 'pm-tools', 't122.tcl')
OUT = os.path.join(PROJ, 'work', 'shots', 't122.txt')
CPU = 3579545.0
HALF = 446.025 / 2
CFG = os.path.join(HERE, 'tvplay16.json')
ROM = 'PuzzleMania_S16TV.rom'
KINDS = ['h1', 'h2', 'ap', 'np', 'ac', 'nc', 'e', 'f1', 'f2']


def build():
    r = subprocess.run([sys.executable, os.path.join(HERE, 'gen_tvplay16.py')], capture_output=True, text=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, 'build_game.py'), '--lite', '--quick', '--scc', '--titlevideo', '--titleframes', '24', '--out', ROM],
                       capture_output=True, text=True, cwd=PROJ)
    if r.returncode != 0:
        print(r.stdout[-1500:], r.stderr[-1500:]); sys.exit('build failed')


def run():
    if os.path.exists(OUT):
        os.remove(OUT)
    p = subprocess.Popen([OPENMSX, '-machine', 'Philips_NMS_8250', '-cart', os.path.join(PROJ, ROM), '-romtype', 'NEO-16', '-ext', 'scc', '-script', TCL],
                         env=dict(os.environ, DUMP='x'))
    t = time.time()
    try:
        while not os.path.exists(OUT) and time.time() - t < 60:
            time.sleep(1)
        time.sleep(1)
    finally:
        p.kill()


def labels():
    d = {}
    for l in open(os.path.join(PROJ, 'game', 'pm.sym')):
        m = re.match(r't16_(\w+?)(?:\.(\w+))?: EQU 0x([0-9A-F]+)', l)
        if m:
            d[(m.group(1), m.group(2))] = int(m.group(3), 16)
    return d


def analyse():
    lab = labels()
    starts = []                                   # (start address, kind, address of the A marker)
    for (k, loc), a in lab.items():
        if loc is None and k not in ('f1',):
            kk = 'f1' if k == 'f1a' else k
            if (k, 'ma') in lab:
                starts.append((a, kk, lab[(k, 'ma')]))
    starts.sort()
    ev = [l.split() for l in open(OUT).read().splitlines()]
    T = np.array([float(t) * CPU for t, _ in ev]); PCs = [int(pc, 16) for _, pc in ev]

    def role(pc):
        cur = None
        for a, k, ma in starts:
            if a <= pc:
                cur = (k, 'A' if pc <= ma + 1 else 'B')
        return cur
    res = {k: {'ab': [], 'ba': []} for k in KINDS}
    evr = [role(pc) for pc in PCs]
    for i in range(len(T) - 2):
        a, b, c = evr[i], evr[i + 1], evr[i + 2]
        if a and b and a[1] == 'A' and b[1] == 'B' and a[0] == b[0] and a[0] in res and T[i + 1] - T[i] < 400:
            res[a[0]]['ab'].append(T[i + 1] - T[i])
            if c and c[1] == 'A' and T[i + 2] - T[i + 1] < 400:
                res[a[0]]['ba'].append(T[i + 2] - T[i + 1])
    return res


def main():
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    for r in range(rounds):
        cfg = json.load(open(CFG)) if os.path.exists(CFG) else {}
        build(); run()
        res = analyse()
        msg = []; worst = 0
        for k in KINDS:
            ab = res[k]['ab']; ba = res[k]['ba']
            if not ab:
                continue
            m1 = float(np.median(ab)); m2 = float(np.median(ba)) if ba else None
            key = {'np': 'np', 'nc': 'nc'}.get(k, k)
            for half, m in ((1, m1), (2, m2)):
                if m is None:
                    continue
                kk = '%s%d' % (key, half)
                cfg[kk] = max(0.0, cfg.get(kk, 20.0) + HALF - m)
                worst = max(worst, abs(HALF - m))
            msg.append('%s %.1f/%s (n=%d)' % (k, m1, '%.1f' % m2 if m2 else '-', len(ab)))
        print('round %d: worst %.1f; %s' % (r, worst, '; '.join(msg)), flush=True)
        json.dump(cfg, open(CFG, 'w'), indent=1)
    print('done')


if __name__ == '__main__':
    main()
