"""Tune the burns of the FONY film players (tools/fony.json for the PSG player, tools/fony16.json for the SCC player): build a test ROM (--fonytest), log every sample write in
openMSX with its PC (.claude/snd-tools/snd_log.tcl), classify the iterations by the labels of game/ovl.sym and correct the burns until every iteration is exactly 446 cycles
(PSG) / both halves 223 cycles (SCC).   usage: tune_fony.py psg|scc [rounds]"""
import os, sys, re, json, subprocess, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, '..', '..'))
OPENMSX = r'C:\Program Files\openMSX\openmsx.exe'
TCL = os.path.join(PROJ, '.claude', 'snd-tools', 'snd_log.tcl')
CPU = 3579545.0
PERIOD = 446.0
ROM = os.path.join(HERE, 'FONY_TUNE.rom')
PSG_KINDS = {'pad': 'Q', 'p1': 'P1', 'p2': 'P2', 'p3': 'P3', 'h1': 'H1', 'h2': 'H2', 'row': 'S', 'sc': 'S', 'np': 'N', 'nc': 'N', 'e': 'E', 'f': 'F'}


def build(mode):
    subprocess.run([sys.executable, os.path.join(PROJ, 'tools', 'gen_fony.py')], check=True, capture_output=True)
    subprocess.run([sys.executable, os.path.join(PROJ, 'tools', 'gen_fony16.py')], check=True, capture_output=True)
    r = subprocess.run([sys.executable, os.path.join(PROJ, 'tools', 'build_game.py'), '--lite', '--quick', '--scc', '--fonytest', '--fonyframes', '12', '--out', ROM],
                       capture_output=True, text=True, cwd=PROJ)
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-2000:]); sys.exit('build failed')


def run(mode, sec=9):
    out = os.path.join(HERE, 'tune_%s.txt' % mode)
    if os.path.exists(out): os.remove(out)
    cmd = [OPENMSX, '-machine', 'Philips_NMS_8250', '-cart', ROM, '-romtype', 'NEO-16']
    if mode == 'scc': cmd += ['-ext', 'scc']
    p = subprocess.Popen(cmd + ['-script', TCL], env=dict(os.environ, MODE=mode, SEC=str(sec), OUT=out), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t = time.time()
    while not os.path.exists(out) and time.time() - t < 180:
        time.sleep(0.5)
    time.sleep(1)
    p.kill()
    rows = [l.split() for l in open(out).read().split('\n') if l.strip()]
    return np.array([float(r[0]) * CPU for r in rows]), np.array([int(r[1]) for r in rows])


def labels(prefix):
    d = {}
    for l in open(os.path.join(PROJ, 'game', 'ovl.sym')):
        m = re.match(r'%s(\w+?)(?:\.(\w+))?: EQU 0x([0-9A-F]+)' % prefix, l)
        if m:
            d[(m.group(1), m.group(2))] = int(m.group(3), 16)
    return d


def tune_psg(rounds):
    cfgp = os.path.join(PROJ, 'tools', 'fony.json')
    for r in range(rounds):
        build('psg')
        t, pc = run('psg')
        lab = labels('fy_')
        starts = sorted((a, k) for (k, loc), a in lab.items() if loc is None and k in ('pad', 'p1', 'p2', 'p3', 'h1', 'h2', 'row', 'sc', 'np', 'nc', 'e'))
        kind = lambda x: [k for a, k in starts if a <= x][-1] if x >= starts[0][0] else None
        first = np.concatenate([[True], np.diff(t) > 200])                  # the first write of every iteration
        T, PC = t[first], pc[first]
        K = [kind(x) for x in PC]
        res = {}
        for i in range(len(T) - 1):
            k = K[i]
            if k is None or T[i + 1] - T[i] > 600:
                continue
            if k == 'e' and K[i + 1] == 'pad':
                k = 'f'
            res.setdefault(k, []).append(T[i + 1] - T[i])
        cfg = json.load(open(cfgp))
        worst = 0; msg = []
        acc = {}
        for k, v in res.items():
            m = float(np.median(v)); worst = max(worst, abs(PERIOD - m))
            msg.append('%s %.1f(n=%d)' % (k, m, len(v)))
            acc.setdefault(PSG_KINDS[k], []).append(PERIOD - m)
        for key, errs in acc.items():
            cfg[key] = cfg.get(key, 0) + int(round(np.mean(errs)))
        print('round', r, 'worst %.1f' % worst, ' '.join(sorted(msg)), flush=True)
        json.dump(cfg, open(cfgp, 'w'))
        if worst < 0.6:
            print('tuned'); return


def tune_scc(rounds):
    cfgp = os.path.join(PROJ, 'tools', 'fony16.json')
    HALF = PERIOD / 2
    for r in range(rounds):
        build('scc')
        t, pc = run('scc')
        lab = labels('t16_')
        starts = []
        for (k, loc), a in lab.items():
            if loc is None and (k, 'ma') in lab and k in ('p1', 'p2', 'p3', 'h1', 'h2', 'ap', 'np', 'ac', 'nc', 'e'):
                starts.append((a, k, lab[(k, 'ma')]))
        starts.sort()

        def role(x):
            cur = None
            for a, k, ma in starts:
                if a <= x:
                    cur = (k, 'A' if x <= ma + 1 else 'B')
            return cur
        ev = [role(x) for x in pc]
        res = {}
        for i in range(len(t) - 2):
            a, b, c = ev[i], ev[i + 1], ev[i + 2]
            if a and b and a[1] == 'A' and b[1] == 'B' and a[0] == b[0] and t[i + 1] - t[i] < 400:
                res.setdefault((a[0], 1), []).append(t[i + 1] - t[i])
                if c and c[1] == 'A' and t[i + 2] - t[i + 1] < 400:
                    res.setdefault((a[0], 2), []).append(t[i + 2] - t[i + 1])
        cfg = json.load(open(cfgp))
        worst = 0; msg = []
        for (k, h), v in sorted(res.items()):
            m = float(np.median(v)); worst = max(worst, abs(HALF - m))
            key = '%s%d' % (k, h)
            cfg[key] = max(0.0, cfg.get(key, 20.0) + HALF - m)
            msg.append('%s%d %.1f' % (k, h, m))
        print('round', r, 'worst %.1f' % worst, ' '.join(msg), flush=True)
        json.dump(cfg, open(cfgp, 'w'), indent=1)
        if worst < 0.6:
            print('tuned'); return


if __name__ == '__main__':
    mode = sys.argv[1]
    rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    (tune_psg if mode == 'psg' else tune_scc)(rounds)
