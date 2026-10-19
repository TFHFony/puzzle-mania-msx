"""Calibrate the work slots of the PSG player (game/heads.inc): the first 10 iterations of every block carry a piece of the work of the frame instead of
the delay and must take exactly as long as a normal iteration.  Builds the framed sample ROM (player with slots), logs the PSG writes in openMSX
(wlog.tcl), measures the 10 slot intervals against the sample period and adjusts the burn (B = djnz count, N = nops) of every slot.
usage: tune_slots.py [rounds]"""
import os, sys, re, subprocess
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
OPENMSX = r'C:\Program Files\openMSX\openmsx.exe'
TCL = os.path.join(PROJ, '.claude', 'pm-tools', 'wlog.tcl')
CPU = 3579545.0
PERIOD = 313 * 228 / 160.0
HEADS = os.path.join(PROJ, 'game', 'heads.inc')
NS = int(open(os.path.join(PROJ, 'game', 'slots_ns.txt')).read())


def read_heads():
    d = dict((m.group(1), int(m.group(2))) for m in re.finditer(r'(\w+) equ (\d+)', open(HEADS).read()))
    return [d['B%d' % i] for i in range(1, NS + 1)], [d['N%d' % i] for i in range(1, NS + 1)]


def write_heads(b, n):
    d = dict((m.group(1), int(m.group(2))) for m in re.finditer(r'(\w+) equ (\d+)', open(HEADS).read()))      # keep the other entries (the job engine)
    for i in range(NS):
        d['B%d' % (i + 1)] = b[i]; d['N%d' % (i + 1)] = n[i]
    keys = ['%s%d' % (c, i + 1) for i in range(NS) for c in 'BN'] + [k for k in d if not re.match(r'[BN]\d+$', k)]
    open(HEADS, 'w').write(''.join('%s equ %d\n' % (k, d[k]) for k in keys))


def measure():
    subprocess.run([sys.executable, os.path.join(HERE, 'build_sample.py'), '--curve', 'ym', '--framed', '--out', os.path.join('work', 'slots_test.rom')],
                   check=True, capture_output=True)
    w = os.path.join(PROJ, 'work', 'wlog.txt')
    if os.path.exists(w): os.remove(w)
    subprocess.run([OPENMSX, '-machine', 'Philips_VG_8020', '-cart', os.path.join(PROJ, 'work', 'slots_test.rom'), '-romtype', 'NEO-16', '-script', TCL],
                   capture_output=True, timeout=300)
    t = []
    for ln in open(w):
        p, v, tm = ln.split()
        if p == '0' and int(v) == 8: t.append(float(tm) * CPU)
    t = np.array(t); d = np.diff(t)
    starts = [0] + list(np.where(d > 1.5 * PERIOD)[0] + 1)
    iv = []
    for s in starts:
        if s + NS + 1 < len(t) and (s == 0 or True):
            iv.append(d[s:s + NS + 1])
    iv = np.array(iv[1:])                       # the first block may be a partial one
    return iv


if __name__ == '__main__':
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    b, n = read_heads()
    for r in range(rounds):
        write_heads(b, n)
        iv = measure()
        mean = np.median(iv, 0); sd = iv.std(0)
        print('round', r, 'blocks', len(iv))
        for i in range(NS + 1):
            print('  interval %d: mean %.1f (target %.1f), sd %.1f   %s' % (i + 1, mean[i], PERIOD, sd[i], ('B%d=%d N%d=%d' % (i + 1, b[i], i + 1, n[i])) if i < NS else '(first normal iteration)'))
        worst = max(abs(mean[:NS] - PERIOD))
        if worst < 3.5: break
        for i in range(NS):
            want = 14 * b[i] + 5 * n[i] - (mean[i] - PERIOD)
            best = None
            for bb in range(1, 40):
                for nn in range(0, 3):
                    e = abs(14 * bb + 5 * nn - want)
                    if best is None or e < best[0]: best = (e, bb, nn)
            b[i], n[i] = best[1], best[2]
    write_heads(b, n)
    print('final', b, n)
