"""usage: analyse.py LOGFILE -> per busy level: frames, samples played/skipped; the extra skipped samples relative to the idle level; frame period spread"""
import sys, collections
L = open(sys.argv[1]).read().split('\n')
tail = [l for l in L if l.startswith('moves')]
rows = [tuple(float(x) if i == 0 else int(x) for i, x in enumerate(l.split())) for l in L if l and not l.startswith('moves')]
print(tail[0] if tail else 'no tail')
if len(rows) < 3: print('too few rows', len(rows)); sys.exit()
dt = [b[0] - a[0] for a, b in zip(rows, rows[1:])]
dt_ms = sorted(d * 1000 for d in dt)
print('frames %d  period ms: min %.2f median %.2f max %.2f  (>21 ms: %d)' % (len(rows), dt_ms[0], dt_ms[len(dt_ms) // 2], dt_ms[-1], sum(1 for d in dt_ms if d > 21)))
by = collections.defaultdict(list)
for r in rows: by[r[1]].append(r)
idle = by.get(0, [])
base = collections.Counter(r[3] for r in idle).most_common(1)[0][0] if idle else 0
tot = 0
per = collections.defaultdict(list)
for a, b in zip(rows, rows[1:]): per[b[1]].append((b[0] - a[0]) * 1000)
for lev in sorted(by):
    rs = by[lev]; sk = collections.Counter(r[3] for r in rs); n = collections.Counter(r[2] for r in rs)
    extra = sum(r[3] - base for r in rs)
    tot += max(extra, 0) if lev else 0
    print('level %d: %4d frames  skipped %s  played %s  extra-vs-idle %d' % (lev, len(rs), dict(sk), dict(n), extra))
print('period ms per level (the frame itself): ' + '  '.join('L%d %.2f-%.2f (mean %.2f)' % (lev, min(v), max(v), sum(v) / len(v)) for lev, v in sorted(per.items())))
print('idle skip = %d;  total extra skipped samples over %.1f s: %d  = %.2f %% of all samples' % (base, rows[-1][0] - rows[0][0], tot, 100.0 * tot / (len(rows) * 160)))
# runs of non-idle frames
runs = []; cur = 0
for r in rows:
    if r[1] != 0: cur += 1
    elif cur: runs.append(cur); cur = 0
if cur: runs.append(cur)
print('non-idle runs (frames): n=%d  %s' % (len(runs), collections.Counter(runs).most_common(8)))
