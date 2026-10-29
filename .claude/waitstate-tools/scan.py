import re, sys, os, bisect, subprocess
import numpy as np
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
sym = {}
for l in open(r'F:\MSX Projects\PMdev26\game\pm.sym'):
    m = re.match(r'([\w.]+): EQU 0x([0-9A-Fa-f]+)', l)
    if m: sym[m.group(1)] = int(m.group(2), 16)
def run(rom, ton='15', machine='Philips_NMS_8250', n=4000, wait=False):
    out = os.path.join(HERE, 'scw_run.txt').replace(chr(92), '/')
    if os.path.exists(out): os.remove(out)
    env = dict(os.environ, TON=ton, OUT=out)
    subprocess.run([r'C:\Program Files\openMSX\openmsx.exe', '-machine', machine, '-cart', rom, '-romtype', 'NEO-16', '-ext', 'scc', '-script', os.path.join(HERE, 'scw.tcl')], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=400)
    return open(out).read().splitlines()
def analyse(lines, pfx='t16_'):
    ev = [l.split() for l in lines]
    T = np.array([float(t) * 3579545 for t, _ in ev]); P = [int(p, 16) for _, p in ev]
    kinds = {}
    for k, v in sym.items():
        m = re.match(r'%s(\w+?)(?:\.(\w+))?$' % pfx, k)
        if m and m.group(2) is None: kinds[m.group(1)] = v
    starts = sorted((v, k) for k, v in kinds.items())
    ma = {k: sym.get('%s%s.ma' % (pfx, k)) for k in kinds}
    def role(pc):
        i = bisect.bisect_right([v for v, _ in starts], pc) - 1
        k = starts[i][1]
        return k, ('A' if ma.get(k) is not None and pc <= ma[k] + 1 else 'B')
    R = [role(p) for p in P]
    res = defaultdict(list)
    for i in range(len(T) - 1):
        d = T[i + 1] - T[i]
        if d < 400: res[(R[i][0], R[i][1], R[i + 1][0], R[i + 1][1])].append(d)
    return res
if __name__ == '__main__':
    rom = sys.argv[1]
    res = analyse(run(rom))
    for k, v in sorted(res.items()):
        print(k, len(v), 'median %.2f mean %.2f' % (np.median(v), np.mean(v)))
