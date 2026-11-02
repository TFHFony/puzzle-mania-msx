"""Analyse work/wlog.txt (tcl wlog.tcl): sample period, jitter inside the blocks, block start phase against the frame (cycles of 3.579545 MHz)."""
import sys, numpy as np
CPU = 3579545.0
T = 313 * 228 / CPU if len(sys.argv) < 2 or sys.argv[1] != '60' else 262 * 228 / CPU
t = []
sel = None
for ln in open('F:/MSX Projects/PMdev26/work/wlog.txt'):
    p, v, tm = ln.split()
    if p == '0': sel = int(v)
    elif sel == 8 and p == '1': pass
    if p == '0' and int(v) == 8: t.append(float(tm))
t = np.array(t); d = np.diff(t) * CPU
P = np.median(d)
print('writes', len(t), 'median period %.2f cycles' % P)
gaps = np.where(d > 1.5 * P)[0]
starts = [0] + list(gaps + 1); ends = list(gaps) + [len(t) - 1]
print('blocks', len(starts), 'lengths', [e - s + 1 for s, e in zip(starts, ends)][:8])
res = []
for s, e in zip(starts, ends):
    if e - s < 20: continue
    k = np.arange(e - s + 1); y = (t[s:e + 1] - t[s]) * CPU
    c = np.polyfit(k, y, 1); res.append(y - np.polyval(c, k))
    per = c[0]
if res:
    r = np.concatenate(res); print('period (fit) %.3f cycles; in-block jitter rms %.2f cycles, max %.1f' % (per, r.std(), abs(r).max()))
ph = np.array([(t[s] % T) * CPU for s in starts])
print('block start phase vs frame: first %s' % np.round(ph[:10] - ph[0], 1))
ph = ph - ph[0]; ph = (ph + T * CPU / 2) % (T * CPU) - T * CPU / 2
print('start phase spread: std %.1f cycles, peak-peak %.1f cycles' % (ph.std(), ph.max() - ph.min()))
