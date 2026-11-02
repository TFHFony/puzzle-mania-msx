"""wt_calc.py real.txt [ref.txt] [F]: cycles per loop of every test of PM_WaitTest from the numbers on the screen (a dump of the name table, or typed from a photo as
lines like ' 4 OUT PSG A0 RAM  22360 13986' plus a line 'RULER CF= 1924'); with ref.txt (the same ROM in openMSX): the difference per item (32 items per loop)."""
import sys, re
args = [a for a in sys.argv[1:] if not a.isdigit() or len(a) < 5]
F = 71364
model = {}
for ln in open('lt3/model.txt'):
    i, nm, nb, c, L1, L2 = ln.strip().split('|'); model[int(i)] = (nm, int(c), int(L1), int(L2))


def load(fn):
    txt = open(fn).read().splitlines()
    cf = int(re.search(r'CF=\s*(\d+)', ' '.join(txt)).group(1))
    rows = {}
    for ln in txt:
        m = re.match(r'\s*(\d+) (.{21}) +(\d+) +(\d+)\s*$', ln)
        if m: rows[int(m.group(1)) - 1] = (int(m.group(3)), int(m.group(4)))
    out = {}
    for i, (S1, S2) in rows.items():
        nm, c, L1, L2 = model[i]
        out[i] = F * (S1 - S2) / (16.0 * cf * (L2 - L1))
    return cf, out


cf, real = load(args[0])
ref = load(args[1])[1] if len(args) > 1 else None
print('cf', cf, 'poll cycles %.2f' % (F / cf))
print('%-24s %9s %9s %9s %9s' % ('test', 'cyc/loop', 'ref', 'diff', 'per item'))
for i in sorted(real):
    nm = model[i][0]
    r = ref[i] if ref else float('nan')
    print('%-24s %9.2f %9.2f %+9.2f %+9.3f' % (nm, real[i], r, real[i] - r, (real[i] - r) / 32))
