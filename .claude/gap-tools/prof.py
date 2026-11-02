"""usage: prof.py LOGFILE.prof -> the work of the game after every mvsync (cycles from the ret of mvsync to the next call), per caller (return address) and busy level"""
import sys, collections
C = 3579545.0
ev = [l.split() for l in open(sys.argv[1]) if l.strip()]
works = []
for a, b in zip(ev, ev[1:]):
    if a[0] == 'R' and b[0] == 'I':
        works.append((int(a[3]) if len(a) > 3 else -1, a[2], (float(b[1]) - float(a[1])) * C, int(a[4]) if len(a) > 4 else 0))
idle = sorted(w[2] for w in works if w[0] == 0)
print('frames %d; idle (level 0) work: median %.0f cycles  max %.0f' % (len(works), idle[len(idle) // 2] if idle else -1, idle[-1] if idle else -1))
by = collections.defaultdict(list)
for lev, ret, cyc, jq in works:
    if lev != 0: by[(lev, ret)].append(cyc)
for k, v in sorted(by.items()):
    v.sort(); print('level %d, caller %s: n=%d median %.0f min %.0f max %.0f cycles  (= %.2f samples of 446)' % (k[0], k[1], len(v), v[len(v) // 2], v[0], v[-1], v[len(v) // 2] / 446.0))
