"""Diagnostic ROM (4 MB, ASCII16): does the cycle-timed loop of the title video (8 VDP bytes + 3 PSG writes per loop, no frame lock) run at the
speed the cycle count says, measured against the VDP frame?  Six tests of 250 VDP frames each: the number of loops that fit in 250 frames is
compared with the expected number (frame = 313*228 cycles at 50 Hz, 262*228 at 60 Hz).  Variables: code in ROM / RAM, data read from ROM / RAM,
VDP writes on / off.  Output: ROM + .claude/loop-tools/lt/looptest.asm
   python build_looptest.py [--period N] [--out file]"""
import os, sys, subprocess
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, '..', '..'))
SJ = r'F:\MSX Projects\Dev27\.claude\msx-video-tools\sjasmplus\sjasmplus-1.24.0.win\sjasmplus.exe'
arg = lambda n, d=None: sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d
PERIOD = int(arg('--period', '640'))
OUT = arg('--out', os.path.join(PROJ, 'PM_LoopTiming_4MB_ASCII16.rom'))
LT = os.path.join(HERE, 'lt'); os.makedirs(LT, exist_ok=True)
FRAMES = 250
DEXP50 = int(round(FRAMES * 313 * 228 / PERIOD)); DEXP60 = int(round(FRAMES * 262 * 228 / PERIOD))
ADJ_V, ADJ_N = int(arg('--adjv', '17')), int(arg('--adjn', '7'))
AUDIO_C, CNT_C, VDP_C, WRAP_C, JP_C = 164, 64, 268, 20, 11

cnt = [0]
def burn(n):
    """lines that take exactly n cycles (E, DE free): loops of 18k+3, nops (5), inc de (7)"""
    best = None
    for k in range(n // 18, -1, -1):
        base = 18 * k + 3 if k else 0
        rem = n - base
        if rem < 0: continue
        for b in range(0, rem // 7 + 1):
            if (rem - 7 * b) % 5 == 0:
                best = (k, (rem - 7 * b) // 5, b); break
        if best: break
    assert best, n
    k, a, b = best; out = []
    if k:
        cnt[0] += 1
        out += ['        ld e,%d' % k, '.b%d:    dec e' % cnt[0], '        jr nz,.b%d' % cnt[0]]
    return out + ['        nop'] * a + ['        inc de'] * b

def loop(vdp, ramdata, idx):
    fixed = AUDIO_C + CNT_C + WRAP_C + JP_C + (VDP_C if vdp else 0)
    L = ['        ld a,(hl)', '        inc hl', '        ld e,a', '        ld d,TABHI',
         '        ld a,8', '        out (0xA0),a', '        ld a,(de)', '        out (0xA1),a', '        inc d',
         '        ld a,9', '        out (0xA0),a', '        ld a,(de)', '        out (0xA1),a', '        inc d',
         '        ld a,10', '        out (0xA0),a', '        ld a,(de)', '        out (0xA1),a',
         '        exx', '        in a,(0x99)', '        rlca', '        ld a,b', '        sbc a,0', '        ld b,a', '        inc de', '        exx',
         '        jp z,done']
    if vdp:
        L += ['        xor a', '        out (0x99),a', '        ld a,0x78', '        out (0x99),a', '        outi']
        L += ['        ld a,r', '        outi'] * 7
    L += ['        set 6,h' if ramdata else '        res 6,h', '        set 7,h']
    L += burn(PERIOD - fixed + (ADJ_V if vdp else ADJ_N))        # ADJ: measured in openMSX (my cycle count of the instructions was off)
    L += ['        jp t%d_loop' % idx]
    return L

# (code in RAM, data in RAM, vdp)
TESTS = [(0, 0, 1), (1, 1, 1), (0, 0, 0), (1, 1, 0), (1, 0, 1), (0, 1, 1)]
body = []; tab = []; rows = []
for i, (cr, dr, vd) in enumerate(TESTS):
    L = loop(vd, dr, i)
    if cr:
        body.append('t%d_src:\n        DISP 0xC100\nt%d_loop:' % (i, i)); body += L; body.append('t%d_end:\n        ENT' % i)
        tab.append('        dw 0xC100, t%d_src, t%d_end-t%d_loop, %s' % (i, i, i, '0xC000' if dr else '0x8000'))
    else:
        body.append('t%d_loop:' % i); body += L
        tab.append('        dw t%d_loop, 0, 0, %s' % (i, '0xC000' if dr else '0x8000'))
    rows.append(' %d %s  %s  %s  ' % (i + 1, 'RAM' if cr else 'ROM', 'RAM' if dr else 'ROM', 'YES' if vd else 'NO '))

ASM = r'''        DEVICE NOSLOT64K
TABHI   equ 0xD0
tn      equ 0xC000
dres    equ 0xC002
runad   equ 0xC004
sgn     equ 0xC006
hzv     equ 0xC007
msx2    equ 0xC008
DEXP50  equ %(d50)d
DEXP60  equ %(d60)d
        ORG 0x4000
        db "AB"
        dw init
        dw 0,0,0,0,0,0
        ORG 0x4010
init:   di
        ld sp,0xF380
        ld a,(0x002D)
        ld b,a
        ld hl,0xC000
        ld de,0xC001
        ld bc,0x12FF
        ld (hl),0
        ldir
        ld a,(0x002D)
        ld (msx2),a
        xor a
        ld (0x6000),a                   ; ASCII16: page 1 = bank 0, page 2 = bank 128 (the data of the tests)
        ld a,0x80
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
        ld hl,vdpregs                   ; text mode by hand: name table at 0, font at 0800h
        ld b,8
        ld c,0x80
.vr:    ld a,(hl)
        out (0x99),a
        ld a,c
        out (0x99),a
        inc hl
        inc c
        djnz .vr
        ld a,(msx2)
        or a
        jr z,.m1
        xor a                           ; MSX2: status register 0 (frame flag)
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
again:  call draw
        xor a
        ld (tn),a
nexttest:
        ld a,(tn)
        cp 6
        jp z,fin
        ld de,16*40+1
        call vset
        ld hl,s_run
        call pstr
        ld a,(tn)
        add a,'1'
        out (0x98),a
        call setup

done:   exx                             ; the loop ends here (main registers again): DE' = number of loops
        ld (dres),de
        ld sp,0xF380
        call showrow
        ld hl,tn
        inc (hl)
        jp nexttest

setup:  ld a,(tn)
        ld l,a
        ld h,0
        add hl,hl
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
        ldir                            ; the loop to RAM
.nc:    pop hl
        ld e,(hl)
        inc hl
        ld d,(hl)
        ex de,hl                        ; HL = start of the data stream
        ld ix,(runad)
        in a,(0x99)
.sy:    in a,(0x99)                     ; start at a frame flag
        rlca
        jr nc,.sy
        exx
        ld b,%(fr)d                      ; B' = frames to go, DE' = loops
        ld de,0
        exx
        ld c,0x98
        jp (ix)

fin:    ld de,16*40+1
        call vset
        ld hl,s_fin
        call pstr
        ld de,12*40+1
        call vset
        ld a,(hzv)
        cp 50
        ld hl,s_hz50
        jr z,.h
        ld hl,s_hz60
.h:     call pstr
.w1:    call keys
        and 1
        jr nz,.w1
.w2:    call keys
        and 1
        jr z,.w2
        jp again

keys:   in a,(0xAA)                     ; row 8: bit 0 = SPACE (0 = pressed)
        and 0xF0
        or 8
        out (0xAA),a
        in a,(0xA9)
        cpl
        ret

showrow:
        ld a,(tn)                       ; VRAM address = (5 + tn) * 40 + 18
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
        ld de,218
        add hl,de
        ex de,hl
        call vset
        ld hl,(dres)
        push hl
        call pdec5
        ld a,' '
        out (0x98),a
        ld a,' '
        out (0x98),a
        pop hl
        call calc
        ret

calc:   push hl                         ; HL = loops: 50 or 60 Hz?
        ld de,(DEXP50+DEXP60)/2
        or a
        sbc hl,de
        pop hl
        jr c,.s60
        ld a,50
        ld (hzv),a
        ld de,DEXP50
        ld bc,DEXP50/100
        jr .go
.s60:   ld a,60
        ld (hzv),a
        ld de,DEXP60
        ld bc,DEXP60/100
.go:    push bc
        ex de,hl
        or a
        sbc hl,de                       ; HL = expected - measured (+ = the loop is slower than the cycle count says)
        ld a,'+'
        jp p,.pos
        ld a,'-'
        ex de,hl
        ld hl,0
        or a
        sbc hl,de
.pos:   ld (sgn),a
        ld de,600
        push hl
        or a
        sbc hl,de
        pop hl
        jr c,.sm
        srl h                           ; large deviation: x and the unit both / 4 (the ratio stays)
        rr l
        srl h
        rr l
        pop bc
        srl b
        rr c
        srl b
        rr c
        push bc
        push hl
        or a
        sbc hl,de
        pop hl
        jr nc,.big
.sm:
        ex de,hl
        ld hl,0
        ld b,100
.m:     add hl,de
        djnz .m                         ; x * 100
        pop bc
        push bc
        srl b
        rr c
        add hl,bc                       ; + unit / 2 (rounding)
        pop bc
        ld de,0
.q:     or a
        sbc hl,bc
        jr c,.qd
        inc de
        jr .q
.qd:    ld hl,999
        or a
        sbc hl,de
        jr c,.big2
        ld a,d
        or e
        jr nz,.nz
        ld a,'+'
        ld (sgn),a
.nz:    ld a,(sgn)
        out (0x98),a
        ex de,hl
        call pfix
        ld a,' '
        out (0x98),a
        ld a,'%%'
        out (0x98),a
        ret
.big:   pop bc
.big2:  ld hl,s_big
        jp pstr

pfix:   ld b,'0'                        ; HL = hundredths: d.dd
        ld de,100
.l:     or a
        sbc hl,de
        jr c,.e
        inc b
        jr .l
.e:     add hl,de
        ld a,b
        out (0x98),a
        ld a,'.'
        out (0x98),a
        ld a,l
        ld b,'0'
.t:     sub 10
        jr c,.t2
        inc b
        jr .t
.t2:    add a,10
        ld c,a
        ld a,b
        out (0x98),a
        ld a,c
        add a,'0'
        out (0x98),a
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

draw:   ld de,0
        call vset
        ld bc,960
.cl:    xor a
        ld a,32
        out (0x98),a
        dec bc
        ld a,b
        or c
        jr nz,.cl
        ld hl,s_title
        ld de,0*40+1
        call puts
        ld hl,s_sub
        ld de,1*40+1
        call puts
        ld hl,s_head
        ld de,4*40
        call puts
        ld hl,rowtxt
        ld de,5*40
        ld b,6
.r:     push bc
        push de
        call puts
        pop de
        ld bc,40
        ex de,hl
        add hl,bc
        ex de,hl
        pop bc
        inc hl
        djnz .r
        ld hl,s_n1
        ld de,14*40+1
        call puts
        ld hl,s_n2
        ld de,19*40+1
        call puts
        ld hl,s_n3
        ld de,20*40+1
        call puts
        ld hl,s_n4
        ld de,21*40+1
        call puts
        ld hl,s_n5
        ld de,22*40+1
        call puts
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

vdpregs: db 0x00,0xD0,0x00,0x00,0x01,0x00,0x00,0xF4
s_title: db "PM LOOP TIMING TEST  (ASCII16, 4 MB)",0
s_sub:   db "%(per)d CYCLES/LOOP, %(fr)d VDP FRAMES/TEST",0
s_head:  db " # CODE DATA VDP  LOOPS  SLOWER",0
s_run:   db "RUNNING TEST ",0
s_fin:   db "DONE - SPACE = RUN AGAIN  ",0
s_hz50:  db "VDP FRAME RATE: 50 HZ",0
s_hz60:  db "VDP FRAME RATE: 60 HZ",0
s_big:   db "BIG    ",0
s_n1:    db "EXPECTED LOOPS: %(d50)d/50HZ %(d60)d/60HZ",0
s_n2:    db "SLOWER + = THE Z80 LOOP RUNS SLOWER",0
s_n3:    db "THAN THE CYCLE COUNT SAYS (VS VDP).",0
s_n4:    db "CODE/DATA: WHERE THE LOOP RUNS FROM /",0
s_n5:    db "WHERE ITS DATA IS READ.  VDP: 8 BYTES",0
rowtxt:
%(rows)s
ttab:
%(tab)s

%(body)s
        ASSERT $ < 0x8000
'''
rowsdb = '\n'.join('        db "%s",0' % r for r in rows)
asm = ASM % dict(d50=DEXP50, d60=DEXP60, fr=FRAMES, per=PERIOD, rows=rowsdb, tab='\n'.join(tab), body='\n'.join(body))
asm += '        ds 0x8000-$,0xFF\n        SAVEBIN "code.bin",0x4000,0x4000\n'
open(os.path.join(LT, 'looptest.asm'), 'w').write(asm)
r = subprocess.run([SJ, '--nologo', '--lst=looptest.lst', '--sym=looptest.sym', 'looptest.asm'], cwd=LT, capture_output=True, text=True)
print(r.stdout + r.stderr)
if r.returncode: sys.exit('assembly failed')
code = open(os.path.join(LT, 'code.bin'), 'rb').read()
assert len(code) == 16384
rng = np.random.RandomState(26)
with open(OUT, 'wb') as f:
    f.write(code)
    for b in range(1, 256): f.write(rng.bytes(16384))
print(OUT, os.path.getsize(OUT), 'bytes; expected loops: %d (50 Hz) / %d (60 Hz)' % (DEXP50, DEXP60))
