"""v1 -> v2 of build_waittest.py in one go (replaces patch_wt_v2.py): tests of a bank switch + sequential read, the arithmetic on the ROM (patch_wt_v2b.py is run after this)"""
p = r'F:\MSX Projects\PMdev26\.claude\loop-tools\build_waittest.py'
s = open(p).read()
assert 'compute_all' not in s and 'SW_LDIR' not in s


def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)


NL = chr(10)
# --- cost model
rep("COST = {'nop': 5, 'xor a': 5, 'ld a,r': 11, 'outi': 19}", "COST = {'nop': 5, 'xor a': 5, 'ld a,r': 11, 'outi': 19}")
rep("def cost(ins):" + NL + "    if ins in COST: return COST[ins]" + NL,
    "def cost(ins):" + NL + "    if ins in COST: return COST[ins]" + NL + "    if ins.startswith('ldir'): return int(ins.split(';')[1]) * 21 - 5" + NL)
rep("    if ins.startswith('ld hl,'): return 11", "    if ins.startswith('ld hl,') or ins.startswith('ld de,') or ins.startswith('ld bc,'): return 11")
# --- tests: remove five that say little, add five of the bank switch + read
for name in ("    ('LD A,(RAM) RAM', [], rep(['ld a,(0xC800)']), 'ram'),",
             "    ('IN PSG A2 RAM', ['ld a,7'], rep(['in a,(0xA2)']), 'ram'),",
             "    ('MAPPER SAME +RD RAM', [], rep(['ld a,1', 'ld (0x7000),a', 'ld a,(0x8000)']), 'ram'),",
             "    ('MAPPER SAME BANK ROM', ['ld a,1'], rep(['ld (0x7000),a']), 'rom'),",
             "    ('MAPPER 1<>2 +RD RAM', [], rep(['ld a,1', 'ld (0x7000),a', 'ld a,(0x8000)', 'ld a,2', 'ld (0x7000),a', 'ld a,(0x8000)'], K // 2), 'ram'),"):
    rep(name + NL, '')
rep("def rep(body, n=K): return body * n" + NL,
    "def rep(body, n=K): return body * n" + NL + NL + NL + "SW_LDIR = ['ld hl,0x8000', 'ld de,0xC800', 'ld bc,256', 'ldir ; 256']" + NL +
    "SW_LDIR64 = ['ld hl,0x8000', 'ld de,0xC800', 'ld bc,64', 'ldir ; 64']" + NL)
rep("    ('NOP x32 RAM (AGAIN)', [], rep(['nop']), 'ram')," + NL + "]",
    "    ('NOP x32 RAM (AGAIN)', [], rep(['nop']), 'ram')," + NL +
    "    ('SAME BANK +LDIR 256', ['ld a,3', 'ld (0x7000),a'], SW_LDIR + SW_LDIR, 'ram')," + NL +
    "    ('BANK 3<>4 +LDIR 256', [], ['ld a,3', 'ld (0x7000),a'] + SW_LDIR + ['ld a,4', 'ld (0x7000),a'] + SW_LDIR, 'ram')," + NL +
    "    ('8 BANKS +LDIR 64', [], sum([['ld a,%d' % b, 'ld (0x7000),a'] + SW_LDIR64 for b in range(5, 13)], []), 'ram')," + NL +
    "    ('SAME BANK +LDIR 64 x8', ['ld a,5', 'ld (0x7000),a'], SW_LDIR64 * 8, 'ram')," + NL +
    "    ('BANK 1<>2 +RD 1 ROM', [], ['ld a,1', 'ld (0x7000),a', 'ld a,(0x8000)', 'ld a,2', 'ld (0x7000),a', 'ld a,(0x8000)'] * 8, 'rom')," + NL + "]")
rep("NT = len(TESTS)" + NL, "NT = len(TESTS)" + NL + "assert NT == 21, NT" + NL + "import json" + NL + "REFF = os.path.join(HERE, 'wt_refs.json')" + NL +
    "REFS = (json.load(open(REFF)) if os.path.exists(REFF) else []) + [0] * 40" + NL)
rep("blobs = []; tab = []; names = []; model = []", "blobs = []; tab = []; names = []; model = []; ctab = []")
rep("    L2 = int(TARGET / c); L1 = L2 // 2", "    L2 = max(2, int(TARGET / c)); L1 = max(1, L2 // 2)")
rep("    names.append(", "    items = 2 if ('LDIR 256' in nm) else 16 if nm.startswith('BANK 1<>2 +RD') else 8 if (nm.startswith('8 BANKS') or 'x8' in nm) else 64 if len(body) == 64 else 32" + NL +
    "    ctab.append('        dw %d, %d, %d' % (L2 - L1, REFS[i] & 0xFFFF, REFS[i] >> 16) + NL + '        db %d, 0' % {2: 1, 8: 3, 16: 4, 32: 5, 64: 6}[items])" + NL + "    names.append(")
rep("asm = ASM % dict(nt=NT,", "asm = ASM % dict(ctab=(NL := chr(10)).join(ctab), nt=NT,")
rep("ttab:" + NL + "%(tab)s" + NL, "ttab:" + NL + "%(tab)s" + NL + "ctab:" + NL + "%(ctab)s" + NL)
# --- variables, run flow, pages
rep("NT      equ %(nt)d" + NL, "NT      equ %(nt)d" + NL + """dblk    equ 0xC600                      ; 16 bytes: N / quotient (0..3), remainder (4..7), divisor (8..11), temporary (12..15)
cres    equ 0xC620                      ; per test 8 bytes: cycles of a loop (word, fraction byte), sign of the difference, |difference| per item (hundredths, word)
cp      equ 0xC6F0
ds      equ 0xC6F2
qv      equ 0xC6F4
fr      equ 0xC6F6
""")
rep("        call run_all" + NL + "        xor a" + NL + "        ld (page),a" + NL, "        call run_all" + NL + "        call compute_all" + NL + "        xor a" + NL + "        ld (page),a" + NL)
rep("        ld a,(page)" + NL + "        xor 1" + NL + "        ld (page),a" + NL + "        call show" + NL + "        jr .w",
    "        ld a,(page)" + NL + "        inc a" + NL + "        cp 3" + NL + "        jr c,.pg" + NL + "        xor a" + NL + ".pg:    ld (page),a" + NL + "        call show" + NL + "        jr .w")
rep("show:   call txclear" + NL + "        ld a,(page)" + NL + "        or a" + NL + "        jp nz,show2" + NL,
    "show:   call txclear" + NL + "        ld a,(page)" + NL + "        cp 2" + NL + "        jp z,show2" + NL + "        or a" + NL + "        jp z,show0" + NL)
rep('s_head: db "# TEST                   S(L1)  S(L2)",0', 's_head: db "# TEST                   S(L1)  S(L2)",0' + NL + 's_head0: db "# TEST                  CYC/LOOP  +/-ITEM",0')
rep('s_title: db "PM WAIT TEST  (SPACE = OTHER PAGE)",0', 's_title: db "PM WAIT TEST  (SPACE = NEXT PAGE)",0')
open(p, 'w').write(s)
print('patched v2c')
