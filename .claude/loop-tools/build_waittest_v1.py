"""Diagnostic ROM 3 (4 MB, ASCII16): what does a real MSX do to the cycle count?  Every test is a loop of K = 32 copies of one thing (NOP, a PSG write, a VDP write,
a bank switch of the mapper ...) in the RAM (or in the ROM), run for L loops.  The time of a run is measured against the VDP frame: start at a blanking, run L loops,
then count the polls of the status register until the next blanking (N).  Two values of L per test: the cycles of ONE loop = F * (S1 - S2) / (16 * cf * (L2 - L1))
(the offsets cancel), cf = polls of a frame (the ruler: the cost of a poll does not matter), F = 71364 cycles (50 Hz; MSX2 and later are put on 50 Hz like the game does).
A blanking that is missed (N > cf) is corrected.  16 runs per value, the sum of the N is shown (S1 for L1, S2 for L2).  tools: wt_calc.py reads the numbers.
   python build_waittest.py [--out file]"""
import os, sys, subprocess
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, '..', '..'))
SJ = r'F:\MSX Projects\Dev27\.claude\msx-video-tools\sjasmplus\sjasmplus-1.24.0.win\sjasmplus.exe'
arg = lambda n, d=None: sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d
OUT = arg('--out', os.path.join(PROJ, 'PM_WaitTest_4MB_ASCII16.rom'))
LT = os.path.join(HERE, 'lt3'); os.makedirs(LT, exist_ok=True)
K = 32
TARGET = 0.6 * 71364                          # cycles of the longest run

COST = {'nop': 5, 'xor a': 5, 'ld a,r': 11, 'outi': 19}


def cost(ins):
    if ins in COST: return COST[ins]
    if ins.startswith('out (') or ins.startswith('in a,('): return 13
    if ins.startswith('ld a,(0x') or ins.startswith('ld (0x'): return 14
    if ins.startswith('ld a,') or ins.startswith('ld b,') or ins.startswith('ld c,'): return 8
    if ins.startswith('ld hl,'): return 11
    raise ValueError(ins)


def rep(body, n=K): return body * n


VSET = ['xor a', 'out (0x99),a', 'ld a,0x5C', 'out (0x99),a']
TESTS = [
    ('NOP x32 RAM', [], rep(['nop']), 'ram'),
    ('NOP x64 RAM', [], rep(['nop'], 64), 'ram'),
    ('NOP x32 ROM', [], rep(['nop']), 'rom'),
    ('OUT PSG A0 RAM', ['ld a,7'], rep(['out (0xA0),a']), 'ram'),
    ('IN PSG A2 RAM', ['ld a,7'], rep(['in a,(0xA2)']), 'ram'),
    ('IN PPI A9 RAM', [], rep(['in a,(0xA9)']), 'ram'),
    ('LD (RAM),A RAM', [], rep(['ld (0xC800),a']), 'ram'),
    ('LD A,(RAM) RAM', [], rep(['ld a,(0xC800)']), 'ram'),
    ('VDP ADDR 99 x32 RAM', [], rep(VSET, K // 2), 'ram'),
    ('VDP DATA 98 B2B RAM', VSET + ['xor a'], rep(['out (0x98),a']), 'ram'),
    ('VDP DATA 98+LDAR RAM', VSET + ['xor a'], rep(['out (0x98),a', 'ld a,r']), 'ram'),
    ('VDP OUTI+LDAR RAM', VSET + ['ld hl,0xC800', 'ld b,0', 'ld c,0x98'], rep(['outi', 'ld a,r']), 'ram'),
    ('VDP STATUS 99 x32 RAM', [], rep(['in a,(0x99)']), 'ram'),
    ('MAPPER SAME BANK RAM', ['ld a,1'], rep(['ld (0x7000),a']), 'ram'),
    ('MAPPER 1<>2 RAM', [], rep(['ld a,1', 'ld (0x7000),a', 'ld a,2', 'ld (0x7000),a'], K // 2), 'ram'),
    ('MAPPER 1<>2 +RD RAM', [], rep(['ld a,1', 'ld (0x7000),a', 'ld a,(0x8000)', 'ld a,2', 'ld (0x7000),a', 'ld a,(0x8000)'], K // 2), 'ram'),
    ('MAPPER SAME +RD RAM', [], rep(['ld a,1', 'ld (0x7000),a', 'ld a,(0x8000)']), 'ram'),
    ('READ PAGE2 ROM RAM', [], rep(['ld a,(0x8000)']), 'ram'),
    ('MAPPER 1<>2 ROM', [], rep(['ld a,1', 'ld (0x7000),a', 'ld a,2', 'ld (0x7000),a'], K // 2), 'rom'),
    ('MAPPER SAME BANK ROM', ['ld a,1'], rep(['ld (0x7000),a']), 'rom'),
    ('NOP x32 RAM (AGAIN)', [], rep(['nop']), 'ram'),
]
NT = len(TESTS)

blobs = []; tab = []; names = []; model = []
for i, (nm, pre, body, where) in enumerate(TESTS):
    c = sum(cost(x) for x in pre) + sum(cost(x) for x in body) + 28
    L2 = int(TARGET / c); L1 = L2 // 2
    lines = ['t%d:' % i] + ['        ' + x for x in pre]
    lines.append('t%d_l:' % i)
    lines += ['        ' + x for x in body]
    lines += ['        dec de', '        ld a,d', '        or e', '        jp nz,t%d_l' % i, '        ret']
    if where == 'ram':
        blobs.append('t%d_src:\n        DISP 0xC100\n' % i + '\n'.join(lines) + '\nt%d_end:\n        ENT' % i)
        tab.append('        dw 0xC100, t%d_src, t%d_end-t%d, %d, %d, n%d' % (i, i, i, L1, L2, i))
    else:
        blobs.append('\n'.join(lines))
        tab.append('        dw t%d, 0, 0, %d, %d, n%d' % (i, L1, L2, i))
    names.append('n%d:     db "%2d %-21s",0' % (i, i + 1, nm))
    model.append('%d|%s|%d|%d|%d|%d' % (i, nm, len(body) if nm.startswith('NOP') else 0, c, L1, L2))
open(os.path.join(LT, 'model.txt'), 'w').write('\n'.join(model) + '\n')

ASM = r'''        DEVICE NOSLOT64K
cf      equ 0xC000
tn      equ 0xC002
ml      equ 0xC004
msum    equ 0xC006
mr      equ 0xC008
runad   equ 0xC00A
msx2    equ 0xC00C
page    equ 0xC00E
firsts  equ 0xC00F
fn      equ 0xC010                      ; 8 words: the first N values (test 1, L1)
rp      equ 0xC020
tl1     equ 0xC022
tl2     equ 0xC024
res     equ 0xC040                      ; per test 2 words: sum of N for L1 and for L2
NT      equ %(nt)d
        ORG 0x4000
        db "AB"
        dw init
        dw 0,0,0,0,0,0
        ORG 0x4010
init:   di
        ld sp,0xF380
        ld hl,0xC000
        ld de,0xC001
        ld bc,0x04FF
        ld (hl),0
        ldir
        ld a,(0x002D)
        ld (msx2),a
        xor a
        ld (0x6000),a                   ; ASCII16: page 1 = bank 0, page 2 = bank 1
        inc a
        ld (0x7000),a
        call 0x0138                     ; RSLREG: page 2 = our cartridge slot (the same as page 1)
        rrca
        rrca
        and 3
        ld c,a
        ld b,0
        ld hl,0xFCC1
        add hl,bc
        or (hl)
        ld c,a
        inc hl
        inc hl
        inc hl
        inc hl
        ld a,(hl)
        and 0x0C
        or c
        ld h,0x80
        call 0x0024                     ; ENASLT
        di
        ld a,7                          ; PSG: tone and noise off, volumes 0
        out (0xA0),a
        ld a,0xBF
        out (0xA1),a
        ld a,8
        out (0xA0),a
        xor a
        out (0xA1),a
        ld a,9
        out (0xA0),a
        xor a
        out (0xA1),a
        ld a,10
        out (0xA0),a
        xor a
        out (0xA1),a
        call txmode
        ld a,(msx2)
        or a
        jr z,again
        ld a,(0xFFE8)                   ; MSX2 and later: 50 Hz like the game
        or 2
        ld (0xFFE8),a
        out (0x99),a
        ld a,0x89
        out (0x99),a
again:  call txclear
        ld hl,s_run
        ld de,0
        call puts
        call ruler
        call run_all
        xor a
        ld (page),a
        call show
.w:     call keys
        and 1
        jr nz,.w
.w2:    call keys
        and 1
        jr z,.w2
        ld a,(page)
        xor 1
        ld (page),a
        call show
        jr .w

keys:   in a,(0xAA)                     ; row 8: bit 0 = SPACE (0 = pressed)
        and 0xF0
        or 8
        out (0xAA),a
        in a,(0xA9)
        cpl
        ret

tvwait: in a,(0x99)
.w:     in a,(0x99)
        rlca
        jr nc,.w
        ret
count:  ld bc,0
.l:     in a,(0x99)
        inc bc
        rlca
        jr nc,.l
        ret
jphl:   jp (hl)

ruler:  call tvwait                     ; cf = the smallest number of polls of 8 frames
        ld hl,0xFFFF
        ld (cf),hl
        ld a,8
        ld (mr),a
.l:     call count
        ld hl,(cf)
        or a
        sbc hl,bc
        jr c,.n
        ld (cf),bc
.n:     ld a,(mr)
        dec a
        ld (mr),a
        jr nz,.l
        ret

run_all:                                ; every test: L1 and L2
        xor a
        ld (tn),a
        inc a
        ld (firsts),a
.t:     ld a,(tn)
        call setup
        ld a,(tn)
        add a,a
        add a,a
        ld l,a
        ld h,0
        ld de,res
        add hl,de
        ld (rp),hl
        ld hl,(tl1)
        call meas
        ld hl,(rp)
        ld (hl),e
        inc hl
        ld (hl),d
        inc hl
        ld (rp),hl
        xor a
        ld (firsts),a
        ld hl,(tl2)
        call meas
        ld hl,(rp)
        ld (hl),e
        inc hl
        ld (hl),d
        ld a,(tn)
        inc a
        ld (tn),a
        cp NT
        jr nz,.t
        ret

setup:  ld l,a                          ; A = test: copy its loop to the RAM, tl1 / tl2 / runad (the entries are 12 bytes)
        ld h,0
        ld d,h
        ld e,l
        add hl,hl
        add hl,de
        add hl,hl
        add hl,hl
        ld de,ttab
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld (runad),de
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld c,(hl)
        inc hl
        ld b,(hl)
        inc hl
        push hl
        ld a,b
        or c
        jr z,.nc
        ex de,hl
        ld de,0xC100
        ldir
.nc:    pop hl
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld (tl1),de
        ld e,(hl)
        inc hl
        ld d,(hl)
        ld (tl2),de
        ret

meas:   ld (ml),hl                      ; HL = L: DE = the sum of the N of 16 runs
        ld hl,0
        ld (msum),hl
        ld a,16
        ld (mr),a
        call tvwait
.r:     ld de,(ml)
        ld hl,(runad)
        call jphl
        in a,(0x99)
        call count
        ld hl,(cf)
        or a
        sbc hl,bc                       ; cf - N
        jr nc,.ok
        ld a,l                          ; N > cf: a blanking was missed, N = N - cf
        cpl
        ld l,a
        ld a,h
        cpl
        ld h,a
        inc hl
        ld b,h
        ld c,l
.ok:    ld a,(firsts)
        or a
        jr z,.ns
        ld a,(mr)                       ; the first 8 runs of the first test are kept
        neg
        add a,16
        cp 8
        jr nc,.ns
        ld l,a
        ld h,0
        add hl,hl
        ld de,fn
        add hl,de
        ld (hl),c
        inc hl
        ld (hl),b
.ns:    ld hl,(msum)
        add hl,bc
        ld (msum),hl
        ld a,(mr)
        dec a
        ld (mr),a
        jr nz,.r
        ld de,(msum)
        ret

vset:   ld a,e
        out (0x99),a
        ld a,d
        or 0x40
        out (0x99),a
        ret
puts:   call vset
pstr:   ld a,(hl)
        or a
        ret z
        out (0x98),a
        inc hl
        jr pstr

txmode: ld hl,txregs                    ; text mode: name table at 0, font at 0800h
        ld b,8
        ld c,0x80
.v:     ld a,(hl)
        out (0x99),a
        ld a,c
        out (0x99),a
        inc hl
        inc c
        djnz .v
        ld a,(msx2)
        or a
        jr z,.m1
        xor a
        out (0x99),a
        ld a,0x8F
        out (0x99),a
.m1:    ld de,0x0800
        call vset
        ld hl,(0x0004)
        ld bc,0x0800
.fl:    ld a,(hl)
        out (0x98),a
        inc hl
        dec bc
        ld a,b
        or c
        jr nz,.fl
        ret
txclear:
        ld de,0
        call vset
        ld bc,960
.cl:    ld a,32
        out (0x98),a
        dec bc
        ld a,b
        or c
        jr nz,.cl
        ret

show:   call txclear
        ld a,(page)
        or a
        jp nz,show2
        ld hl,s_title
        ld de,0
        call puts
        ld hl,s_cf
        ld de,40
        call puts
        ld hl,(cf)
        call pdec5
        ld hl,s_v
        call pstr
        ld a,(msx2)
        ld l,a
        ld h,0
        call pdec5
        ld hl,s_head
        ld de,80
        call puts
        xor a
        ld (tn),a
.l:     ld a,(tn)                       ; the row (3 + test) * 40
        add a,3
        ld l,a
        ld h,0
        ld d,h
        ld e,l
        add hl,hl
        add hl,hl
        add hl,de
        add hl,hl
        add hl,hl
        add hl,hl
        ex de,hl
        call vset
        ld a,(tn)
        add a,a
        ld l,a
        ld h,0
        ld de,ntab
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        ex de,hl
        call pstr
        ld a,' '
        out (0x98),a
        ld a,(tn)
        add a,a
        add a,a
        ld l,a
        ld h,0
        ld de,res
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        push hl
        ex de,hl
        call pdec5
        ld a,' '
        out (0x98),a
        pop hl
        ld e,(hl)
        inc hl
        ld d,(hl)
        ex de,hl
        call pdec5
        ld a,(tn)
        inc a
        ld (tn),a
        cp NT
        jp nz,.l
        ret

show2:  ld hl,s_p2
        ld de,0
        call puts
        ld hl,s_p3
        ld de,80
        call puts
        ld hl,fn
        ld b,8
        ld de,4*40+2
.l:     push bc
        push de
        call vset
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        push hl
        ex de,hl
        call pdec5
        pop hl
        pop de
        ex de,hl
        ld bc,40
        add hl,bc
        ex de,hl
        pop bc
        djnz .l
        ret

pdec5:  ld e,0
        ld bc,10000
        call .dig
        ld bc,1000
        call .dig
        ld bc,100
        call .dig
        ld bc,10
        call .dig
        ld bc,1
        ld e,1
.dig:   xor a
.s:     sbc hl,bc
        jr c,.dn
        inc a
        jr .s
.dn:    add hl,bc
        or a
        jr nz,.p
        bit 0,e
        jr nz,.p
        ld a,' '
        jr .o
.p:     ld e,1
        add a,'0'
.o:     out (0x98),a
        ret

txregs: db 0x00,0xD0,0x00,0x00,0x01,0x00,0x00,0xF4
s_run:  db "RUNNING THE TESTS ... (ABOUT 15 S)",0
s_title: db "PM WAIT TEST  (SPACE = OTHER PAGE)",0
s_cf:   db "RULER CF=",0
s_v:    db "  MSXVER=",0
s_head: db "# TEST                   S(L1)  S(L2)",0
s_p2:   db "PAGE 2: THE FIRST 8 RUNS OF TEST 1",0
s_p3:   db "N (POLLS TO THE NEXT BLANKING), L1:",0
%(names)s
ntab:
%(ntab)s
ttab:
%(tab)s

%(blobs)s
        ASSERT $ < 0x8000
        ds 0x8000-$,0xFF
        SAVEBIN "code.bin",0x4000,0x4000
'''
asm = ASM % dict(nt=NT, names='\n'.join(names), ntab='\n'.join('        dw n%d' % i for i in range(NT)), tab='\n'.join(tab), blobs='\n'.join(blobs))
open(os.path.join(LT, 'waittest.asm'), 'w').write(asm)
r = subprocess.run([SJ, '--nologo', '--lst=waittest.lst', '--sym=waittest.sym', 'waittest.asm'], cwd=LT, capture_output=True, text=True)
print(r.stdout + r.stderr)
if r.returncode: sys.exit('assembly failed')
code = open(os.path.join(LT, 'code.bin'), 'rb').read()
assert len(code) == 16384
rng = np.random.RandomState(28)
with open(OUT, 'wb') as f:
    f.write(code)
    for b in range(1, 256): f.write(rng.bytes(16384))
print(OUT, os.path.getsize(OUT), 'bytes,', NT, 'tests')
