"""one-time patch of build_waittest.py (v1 -> v2): the ROM computes the cycles per loop and the difference with the openMSX reference per item itself (3 pages), and
there are tests of a bank switch followed by a sequential read (the Pico+ may load a whole bank before the Z80 may go on)."""
p = r'F:\MSX Projects\PMdev26\.claude\loop-tools\build_waittest.py'
s = open(p).read()
assert 'compute_all' not in s


def rep(a, b):
    global s
    assert a in s, a[:60]
    s = s.replace(a, b, 1)


# ---- tests: items per loop (shift of the difference) and the bank switch + read tests
rep("def rep(body, n=K): return body * n\n", "def rep(body, n=K): return body * n\n\n\nSW_LDIR = ['ld hl,0x8000', 'ld de,0xC800', 'ld bc,256', 'ldir ; 256']\nSW_LDIR64 = ['ld hl,0x8000', 'ld de,0xC800', 'ld bc,64', 'ldir ; 64']\n")
rep("    ('NOP x32 RAM (AGAIN)', [], rep(['nop']), 'ram'),\n]",
    "    ('NOP x32 RAM (AGAIN)', [], rep(['nop']), 'ram'),\n"
    "    ('SAME BANK +LDIR 256', ['ld a,3', 'ld (0x7000),a'], SW_LDIR + SW_LDIR, 'ram'),\n"
    "    ('BANK 3<>4 +LDIR 256', [], ['ld a,3', 'ld (0x7000),a'] + SW_LDIR + ['ld a,4', 'ld (0x7000),a'] + SW_LDIR, 'ram'),\n"
    "    ('BANK 3<>4 +RD 1 BYTE', [], ['ld a,3', 'ld (0x7000),a', 'ld a,(0x8000)', 'ld a,4', 'ld (0x7000),a', 'ld a,(0x8000)'] * 2, 'ram'),\n"
    "    ('8 BANKS +LDIR 256', [], sum([['ld a,%d' % b, 'ld (0x7000),a'] + SW_LDIR64 for b in range(5, 13)], []), 'ram'),\n"
    "    ('SAME BANK +LDIR x8', ['ld a,5', 'ld (0x7000),a'], SW_LDIR64 * 8, 'ram'),\n]")
rep("    ctab.append('        dw %d, %d, %d\\n        db %d, 0' % (L2 - L1, REFS[i] & 0xFFFF, REFS[i] >> 16, 6 if items == 64 else 5))",
    "    items = 64 if len(body) == 64 else (2 if 'LDIR' in nm or 'RD 1' in nm else 32)\n"
    "    sh = {64: 6, 32: 5, 2: 1}[items]\n"
    "    if nm.startswith('8 BANKS') or nm.startswith('SAME BANK +LDIR x8'): sh = 3\n"
    "    ctab.append('        dw %d, %d, %d\\n        db %d, 0' % (L2 - L1, REFS[i] & 0xFFFF, REFS[i] >> 16, sh))")
rep("NT = len(TESTS)\n", "NT = len(TESTS)\nassert NT <= 21 + 5\n")
# the loops of the long tests: L1 must not be 0
rep("    L2 = int(TARGET / c); L1 = L2 // 2\n    lines", "    L2 = max(2, int(TARGET / c)); L1 = max(1, L2 // 2)\n    lines")
rep("    c = sum(cost(x) for x in pre) + sum(cost(x) for x in body) + 28\n    L2 = int(TARGET / c); L1 = L2 // 2\n    items",
    "    c = sum(cost(x) for x in pre) + sum(cost(x) for x in body) + 28\n    L2 = max(2, int(TARGET / c)); L1 = max(1, L2 // 2)\n    items")
rep("COST = {'nop': 5, 'xor a': 5, 'ld a,r': 11, 'outi': 19}", "COST = {'nop': 5, 'xor a': 5, 'ld a,r': 11, 'outi': 19}")
rep("    if ins in COST: return COST[ins]\n", "    if ins in COST: return COST[ins]\n    if ins.startswith('ldir'): return int(ins.split(';')[1]) * 21 - 5\n")
rep("    if ins.startswith('ld hl,'): return 11\n", "    if ins.startswith('ld hl,') or ins.startswith('ld de,') or ins.startswith('ld bc,'): return 11\n")

# ---- refs
rep("NT = len(TESTS)\nassert", "NT = len(TESTS)\nimport json\nREFF = os.path.join(HERE, 'wt_refs.json')\nREFS = (json.load(open(REFF)) if os.path.exists(REFF) else []) + [0] * 40\nassert")
rep("asm = ASM % dict(nt=NT,", "asm = ASM % dict(ctab='\\n'.join(ctab), nt=NT,")
rep("ttab:\n%(tab)s\n", "ttab:\n%(tab)s\nctab:\n%(ctab)s\n")
# ctab list must exist before use: define it empty before the loop that builds the tests
rep("blobs = []; tab = []; names = []; model = []", "blobs = []; tab = []; names = []; model = []; ctab = []")
rep("        dw 0,0,0,0,0,0\n        ORG 0x4010\ninit:", "        dw 0,0,0,0,0,0\n        ORG 0x4010\ninit:")

# ---- variables
rep("NT      equ %(nt)d\n", """NT      equ %(nt)d
dblk    equ 0xC600                      ; 16 bytes: N / quotient (0..3), remainder (4..7), divisor (8..11), temporary (12..15)
cres    equ 0xC620                      ; per test 8 bytes: cycles of a loop (word, fraction byte), sign of the difference, |difference| per item (hundredths, word)
cp      equ 0xC6F0
ds      equ 0xC6F2
qv      equ 0xC6F4
fr      equ 0xC6F6
""")
rep("        call run_all\n        xor a\n        ld (page),a\n", "        call run_all\n        call compute_all\n        xor a\n        ld (page),a\n")
rep("        ld a,(page)\n        xor 1\n        ld (page),a\n        call show\n        jr .w", "        ld a,(page)\n        inc a\n        cp 3\n        jr c,.pg\n        xor a\n.pg:    ld (page),a\n        call show\n        jr .w")
rep("show:   call txclear\n        ld a,(page)\n        or a\n        jp nz,show2\n", "show:   call txclear\n        ld a,(page)\n        cp 2\n        jp z,show2\n        or a\n        jp z,show0\n")
rep('s_head: db "# TEST                   S(L1)  S(L2)",0', 's_head: db "# TEST                   S(L1)  S(L2)",0\ns_head0: db "# TEST                  CYC/LOOP  +/-ITEM",0')
rep('s_title: db "PM WAIT TEST  (SPACE = OTHER PAGE)",0', 's_title: db "PM WAIT TEST  (SPACE = NEXT PAGE)",0')
# the rows of the table: 26 tests do not fit in 21 text rows: page 1 shows the first 21, page 0 all (two columns are not needed: rows 3..23 and the rest on page 3)
for nm in ("    ('LD A,(RAM) RAM', [], rep(['ld a,(0xC800)']), 'ram'),\n", "    ('IN PSG A2 RAM', ['ld a,7'], rep(['in a,(0xA2)']), 'ram'),\n",
           "    ('MAPPER SAME +RD RAM', [], rep(['ld a,1', 'ld (0x7000),a', 'ld a,(0x8000)']), 'ram'),\n",
           "    ('BANK 3<>4 +RD 1 BYTE', [], ['ld a,3', 'ld (0x7000),a', 'ld a,(0x8000)', 'ld a,4', 'ld (0x7000),a', 'ld a,(0x8000)'] * 2, 'ram'),\n",
           "    ('MAPPER SAME BANK ROM', ['ld a,1'], rep(['ld (0x7000),a']), 'rom'),\n"):
    rep(nm, '')
rep("assert NT <= 21 + 5\n", "assert NT == 21, NT\n")
open(p, 'w').write(s)
print('part 1 ok')
