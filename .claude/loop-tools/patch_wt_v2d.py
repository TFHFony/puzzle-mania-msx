"""v2 -> v2d: the bank switch tests with fixed, small run lengths (a bank load of ~3 ms must not push a run beyond one frame)"""
p = r'F:\MSX Projects\PMdev26\.claude\loop-tools\build_waittest.py'
s = open(p).read()
NL = chr(10)


def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)


i0 = s.index("    ('SAME BANK +LDIR 256'")
i1 = s.index("]", s.index("('BANK 1<>2 +RD 1 ROM'"))
new = ("    ('SAME BANK LDIR64 x2', ['ld a,3', 'ld (0x7000),a'], SW_LDIR64 + SW_LDIR64, 'ram')," + NL +
       "    ('BANK 3<>4 LDIR 64', [], ['ld a,3', 'ld (0x7000),a'] + SW_LDIR64 + ['ld a,4', 'ld (0x7000),a'] + SW_LDIR64, 'ram')," + NL +
       "    ('CYCLE 8 BANKS LDIR64', [], ['ld a,(0xC700)', 'inc a', 'ld (0xC700),a', 'and 7', 'add a,5', 'ld (0x7000),a'] + SW_LDIR64, 'ram')," + NL +
       "    ('SAME BANK LDIR 64', ['ld a,5', 'ld (0x7000),a'], SW_LDIR64, 'ram')," + NL +
       "    ('BANK 1<>2 +RD 1 ROM', [], ['ld a,1', 'ld (0x7000),a', 'ld a,(0x8000)', 'ld a,2', 'ld (0x7000),a', 'ld a,(0x8000)'] * 8, 'rom')," + NL)
s = s[:i0] + new + s[i1:]
rep("def rep(body, n=K): return body * n", "OVERRIDE = {'SAME BANK LDIR64 x2': (2, 4, 1), 'BANK 3<>4 LDIR 64': (1, 2, 1), 'CYCLE 8 BANKS LDIR64': (3, 6, 0), 'SAME BANK LDIR 64': (3, 6, 0)}" + NL + NL + NL + "def rep(body, n=K): return body * n")
rep("    L2 = max(2, int(TARGET / c)); L1 = max(1, L2 // 2)", "    L2 = max(2, int(TARGET / c)); L1 = max(1, L2 // 2)" + NL + "    if nm in OVERRIDE: L1, L2 = OVERRIDE[nm][:2]")
j = s.index("    items = 2 if ('LDIR 256' in nm)")
k = s.index("    names.append(")
s = s[:j] + ("    items = 16 if nm.startswith('BANK 1<>2 +RD') else 64 if len(body) == 64 else 32" + NL +
             "    sh = OVERRIDE[nm][2] if nm in OVERRIDE else {16: 4, 32: 5, 64: 6}[items]" + NL +
             "    ctab.append('        dw %d, %d, %d' % (L2 - L1, REFS[i] & 0xFFFF, REFS[i] >> 16) + NL + '        db %d, 0' % sh)" + NL) + s[k:]
rep("COST = {'nop': 5, 'xor a': 5, 'ld a,r': 11, 'outi': 19}", "COST = {'nop': 5, 'xor a': 5, 'ld a,r': 11, 'outi': 19, 'inc a': 5, 'and 7': 8, 'add a,5': 8}")
open(p, 'w').write(s)
print('patched v2d')
