"""one-time patch: tools/gen_tvplay16.py burn(): burns that nop (5) and ld a,r (11) cannot make exactly (12, 13, 14, 17..19, 23, 24) get three more instructions
(ld a,0 = 8, neg = 10, jr $+2 = 13), so that every cycle count from 5 up can be made except 6, 7, 9, 12; the old results stay the same where they were exact"""
p = 'F:/MSX Projects/PMdev26/tools/gen_tvplay16.py'
s = open(p, encoding='utf8').read()
assert 'EXTRA' not in s
old = """    if not best:                                  # (1..4 cycles cannot be made: the nearest below)
        return burn(n - 1, lab) if n > 1 else []
"""
new = """    if not best:                                  # not exact with nop / ld a,r: the extra instructions (A and the flags are free in a burn)
        ex = burn_ext(n, lab)
        if ex is not None:
            return ex
        return burn(n - 1, lab) if n > 1 else []            # (1..4 cycles cannot be made: the nearest below)
"""
assert old in s
s = s.replace(old, new)
helper = '''EXTRA = {5: '        nop', 8: '        ld a,0', 10: '        neg', 11: '        ld a,r', 13: '        jr $+2'}     # cycles of the instructions of a burn (MSX: +1 per opcode fetch, +1 per I/O)


def _combo(rem):
    """the fewest instructions of EXTRA that make rem cycles (None: impossible)"""
    best = [None] * (rem + 1)
    best[0] = []
    for v in range(1, rem + 1):
        for c in EXTRA:
            if v >= c and best[v - c] is not None and (best[v] is None or len(best[v - c]) + 1 < len(best[v])):
                best[v] = best[v - c] + [c]
    return best[rem]


def burn_ext(n, lab):
    for k in range(n // 18, -1, -1):
        base = 18 * k + 3 if k else 0
        if n - base < 0:
            continue
        cs = _combo(n - base)
        if cs is not None:
            out = []
            if k:
                out += ['        ld e,%d' % k, '.b%s: dec e' % lab, '        jr nz,.b%s' % lab]
            return out + [EXTRA[c] for c in sorted(cs)]
    return None


'''
i = s.index('def burn(n, lab):')
s = s[:i] + helper + s[i:]
old2 = '''    out = {0}
    for k in range(0, limit // 18 + 1):
        base = 18 * k + 3 if k else 0
        for a in range(0, limit // 5 + 1):
            for b in range(0, limit // 11 + 1):
                v = base + 5 * a + 11 * b
                if v <= limit:
                    out.add(v)
    return out
'''
new2 = '''    out = {0}
    for k in range(0, limit // 18 + 1):
        base = 18 * k + 3 if k else 0
        for v in range(0, limit - base + 1):
            if _combo(v) is not None:
                out.add(base + v)
    return out
'''
assert old2 in s
s = s.replace(old2, new2)
open(p, 'w', encoding='utf8').write(s)
print('ok')
