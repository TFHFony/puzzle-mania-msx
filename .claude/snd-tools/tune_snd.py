"""Tune the pads of the jingle player (game/sndcfg.inc): build a test ROM (--jngtest), log every sample in openMSX with its PC, measure the distance of the samples per
position in the pass (8 per pass, by the address of the write), correct SND_A.. (PSG) / SND_S.. (SCC) by the error, repeat.
usage: tune_snd.py psg|scc [rounds]"""
import os, re, sys, subprocess, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, '..', '..'))
OPENMSX = r'C:\Program Files\openMSX\openmsx.exe'
CPU = 3579545.0
CFG = os.path.join(PROJ, 'game', 'sndcfg.inc')
ROM = os.path.join(PROJ, '.claude', 'snd-tools', 'JNG_TUNE.rom')


def cfg():
    return {k: int(v) for k, v in re.findall(r'(\w+) equ (-?\d+)', open(CFG).read())}


def write_cfg(d):
    open(CFG, 'w').write(''.join('%s equ %d\n' % (k, v) for k, v in d.items()))


def build():
    r = subprocess.run([sys.executable, os.path.join(PROJ, 'tools', 'build_game.py'), '--lite', '--quick', '--scc', '--jngtest', '--out', ROM], capture_output=True, text=True, cwd=PROJ)
    if r.returncode != 0:
        print(r.stdout[-1500:], r.stderr[-1500:])
        return False
    return True


def measure(mode, sec=7):
    out = os.path.join(HERE, 'snd_%s.txt' % mode)
    if os.path.exists(out): os.remove(out)
    cmd = [OPENMSX, '-machine', 'Philips_NMS_8250', '-cart', ROM, '-romtype', 'NEO-16']
    if mode == 'scc': cmd += ['-ext', 'scc']
    p = subprocess.Popen(cmd + ['-script', os.path.join(HERE, 'snd_log.tcl')], env=dict(os.environ, MODE=mode, SEC=str(sec), OUT=out), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t = time.time()
    while not os.path.exists(out) and time.time() - t < 120:
        time.sleep(0.5)
    time.sleep(1)
    p.kill()
    rows = [l.split() for l in open(out).read().split('\n') if l.strip()]
    return np.array([float(r[0]) for r in rows]), np.array([int(r[1]) for r in rows])


def gaps(mode, t, pc):
    """-> {burst index 0..7 by address: median distance (cycles) to the next sample}"""
    vals, cnt = np.unique(pc, return_counts=True)             # (the loop only: the PCs of the other writes of the game are rare)
    keep = set(v for v, c in zip(vals.tolist(), cnt.tolist()) if c > cnt.max() * 0.3 and v >= 0x4800)
    sel = np.array([x in keep for x in pc.tolist()])
    t, pc = t[sel], pc[sel]
    if mode == 'psg':
        up = sorted(set(pc.tolist()))
        first = up[0::3]                                    # three writes per burst: the first one of each
        assert len(first) == 8, ('PSG: %d writes' % len(up), up)
        sel = np.isin(pc, first)
        t, pc = t[sel], pc[sel]
    else:
        up = sorted(set(pc.tolist()))
        assert len(up) == 8, ('SCC: %d writes' % len(up), up)
        first = up
    d = np.diff(t) * CPU
    res = {}
    for k, a in enumerate(first):
        x = d[pc[:-1] == a]
        res[k] = float(np.median(x))
    return res


if __name__ == '__main__':
    mode = sys.argv[1]
    rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    c = cfg()
    T = c['SND_T'] if mode == 'psg' else c['SND_TS']
    pre = 'SND_A' if mode == 'psg' else 'SND_S'
    for r in range(rounds):
        if not build(): sys.exit('build failed')
        t, pc = measure(mode)
        g = gaps(mode, t, pc)
        print('round', r, 'T', T, 'gaps', ['%.1f' % g[k] for k in range(8)], flush=True)
        err = [round(T - g[k]) for k in range(8)]
        if all(abs(e) == 0 for e in err):
            print('tuned'); break
        for k in range(8):
            name = '%s%d%d' % (pre, k // 2 + 1, k % 2 + 1)
            c[name] += err[k]
        write_cfg(c)
