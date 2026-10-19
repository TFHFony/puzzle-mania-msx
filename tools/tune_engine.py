"""Calibrate the VDP job engine of the player: the paths of the loop (copy 4 bytes, next row part 1, address of the next row, nothing to do) must take
exactly as long as a plain iteration (the sample period).  Builds the framed sample ROM with a test job, logs the PSG and VDP writes in openMSX
(wlog2.tcl), classifies the loop iterations by their VDP traffic and adjusts EBC/ENC, EBH1/ENH1, EBH2/ENH2, EBI/ENI in game/heads.inc.
usage: tune_engine.py [rounds]"""
import os, sys, re, subprocess
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
OPENMSX = r'C:\Program Files\openMSX\openmsx.exe'
TCL = os.path.join(PROJ, '.claude', 'pm-tools', 'wlog2.tcl')
CPU = 3579545.0
PERIOD = 313 * 228 / 160.0
HEADS = os.path.join(PROJ, 'game', 'heads.inc')
NS = int(open(os.path.join(PROJ, 'game', 'slots_ns.txt')).read())
CLASSES = (('C', 'EBC', 'ENC'), ('H1', 'EBH1', 'ENH1'), ('H2', 'EBH2', 'ENH2'), ('I', 'EBI', 'ENI'))


def read_heads():
    return dict((m.group(1), int(m.group(2))) for m in re.finditer(r'(\w+) equ (\d+)', open(HEADS).read()))


def write_heads(d):
    keys = [m.group(1) for m in re.finditer(r'(\w+) equ \d+', open(HEADS).read())]
    open(HEADS, 'w').write(''.join('%s equ %d\n' % (k, d[k]) for k in keys))


def run(job):
    args = [sys.executable, os.path.join(HERE, 'build_sample.py'), '--curve', 'ym', '--framed', '--out', os.path.join('work', 'job_test.rom')]
    if job: args.append('--job')
    subprocess.run(args, check=True, capture_output=True)
    w = os.path.join(PROJ, 'work', 'wlog2.txt')
    if os.path.exists(w): os.remove(w)
    subprocess.run([OPENMSX, '-machine', 'Philips_VG_8020', '-cart', os.path.join(PROJ, 'work', 'job_test.rom'), '-romtype', 'NEO-16', '-script', TCL], capture_output=True, timeout=300)
    ev = []
    sel = None
    for ln in open(w):
        p, v, tm = ln.split()
        ev.append((p, int(v), float(tm) * CPU))
    # PSG reg 8 selects
    ts = np.array([t for p, v, t in ev if p == 'A0' and v == 8])
    vd = [(p, t) for p, v, t in ev if p in ('98', '99')]
    vt = np.array([t for p, t in vd]); vp = np.array([p == '98' for p, t in vd])
    d = np.diff(ts)
    starts = [0] + list(np.where(d > 1.5 * PERIOD)[0] + 1)
    res = {'C': [], 'H1': [], 'H2': [], 'I': [], 'n': 0}
    for s in starts:
        seq = []
        k = s + NS + 1                                   # the loop iterations of the block (after the slots)
        end = s
        while end + 1 < len(ts) and d[end] < 1.5 * PERIOD: end += 1
        for i in range(k, end):
            lo, hi = np.searchsorted(vt, ts[i], 'right'), np.searchsorted(vt, ts[i + 1], 'left')
            n98 = int(vp[lo:hi].sum()); n99 = int((~vp[lo:hi]).sum())
            seq.append((d[i], n98, n99))
        res['n'] += 1
        for j, (iv, a, b) in enumerate(seq):
            if (a, b) == (4, 0): res['C'].append(iv)
            elif (a, b) == (0, 2): res['H2'].append(iv)
            elif (a, b) == (0, 0):
                nxt = seq[j + 1] if j + 1 < len(seq) else None
                if nxt and (nxt[1], nxt[2]) == (0, 2): res['H1'].append(iv)
                else: res['I'].append(iv)
    return res


if __name__ == '__main__':
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    h = read_heads()
    for r in range(rounds):
        write_heads(h)
        res = run(True)
        ridle = run(False)
        res['I'] = ridle['I'] + res['I']
        print('round', r, 'blocks', res['n'])
        worst = 0
        for name, kb, kn in CLASSES:
            v = np.array(res[name])
            if len(v) == 0:
                print('  %-3s no samples' % name); continue
            m = np.median(v)
            print('  %-3s n=%5d median %.1f mean %.1f sd %.1f  (target %.1f)  %s=%d %s=%d' % (name, len(v), m, v.mean(), v.std(), PERIOD, kb, h[kb], kn, h[kn]))
            worst = max(worst, abs(m - PERIOD))
            want = 18 * h[kb] + 5 * h[kn] - (m - PERIOD)
            best = None
            for bb in range(1, 40):
                for nn in range(0, 5):
                    e = abs(18 * bb + 5 * nn - want)
                    if best is None or e < best[0]: best = (e, bb, nn)
            h[kb], h[kn] = best[1], best[2]
        if worst < 3.5: break
    write_heads(h)
    print('final', {k: h[k] for k in ('EBC', 'ENC', 'EBH1', 'ENH1', 'EBH2', 'ENH2', 'EBI', 'ENI')})
