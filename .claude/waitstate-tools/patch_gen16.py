"""one-time patch: tools/gen_tvplay16.py gets main(wait, pfx, outname): a variant for machines with a VDP wait state (every outi takes a cycle more): the N iterations (8 outi: 5 in the first
half, 3 in the second) get 5 / 3 cycles less burn, so that the two samples stay 223 cycles apart and the iteration 446 cycles on such a machine"""
p = r'F:\MSX Projects\PMdev26\tools\gen_tvplay16.py'
s = open(p, encoding='utf8').read()
assert 'def main():' in s and 'wait=False' not in s
s = s.replace('import os, json\n', 'import os, json, re\n', 1)
s = s.replace('def main():\n    cfg = load_cfg()\n', '''def representable(limit=400):
    """the cycle counts that burn() makes exactly: 0, or 18k+3 (k >= 0, k = 0: nothing) + 5a + 11b"""
    out = {0}
    for k in range(0, limit // 18 + 1):
        base = 18 * k + 3 if k else 0
        for a in range(0, limit // 5 + 1):
            for b in range(0, limit // 11 + 1):
                v = base + 5 * a + 11 * b
                if v <= limit:
                    out.add(v)
    return out


def wait_cfg(cfg):
    """the burns of a machine with a VDP wait state: np / nc (the 8 outi iterations) shorter by 5 (first half) and 3 (second half), the sum kept exact where it can be"""
    R = representable()
    c2 = dict(cfg)
    for k in ('np', 'nc'):
        a1 = max(r for r in R if r <= int(round(cfg[k + '1'])))
        a2 = max(r for r in R if r <= int(round(cfg[k + '2'])))
        t1, t2 = a1 - 5, a2 - 3
        best = None
        for tot in (t1 + t2, t1 + t2 - 1):
            for r1 in sorted(R):
                r2 = tot - r1
                if r2 in R and (best is None or abs(r1 - t1) < best[0]):
                    best = (abs(r1 - t1), r1, r2)
            if best:
                break
        assert best, (k, t1, t2)
        c2[k + '1'], c2[k + '2'] = float(best[1]), float(best[2])
        print('%s: burns %d / %d -> %d / %d (wanted %d / %d)' % (k, a1, a2, best[1], best[2], t1, t2))
    return c2


def main(wait=False, pfx='', outname='tvplay16.inc'):
    cfg = load_cfg()
    if wait:
        cfg = wait_cfg(cfg)
''', 1)
old = "    open(os.path.join(PROJ, 'game', 'tvplay16.inc'), 'w').write('\\n'.join(L) + '\\n')\n    print('tvplay16.inc', len(L), 'lines')\n"
assert old in s
new = ("    txt = '\\n'.join(L) + '\\n'\n"
       "    if pfx:\n"
       "        txt = re.sub(r'\\b(tvplay16|tv16_exit|tv16_row|t16_[a-z0-9]+)\\b', pfx + r'\\1', txt)\n"
       "    open(os.path.join(PROJ, 'game', outname), 'w').write(txt)\n"
       "    print(outname, len(L), 'lines')\n")
s = s.replace(old, new)
open(p, 'w', encoding='utf8').write(s)
print('ok')
