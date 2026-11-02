"""Diagnostic ROM 2 (32 KB, ASCII16): runs the REAL title-video loop of the game (game/tvplay.inc, unmodified, one video frame = 1561 loops of 446 cycles)
8 times and measures how late it ends compared with the VDP frame: after each run the number of polls until the next vblank is counted, and the
number of polls of 8 whole frames (the ruler: the poll costs more on a machine with VDP wait states).  phase = 1 - sum(next) / sum(frames);
a loop that is x % slow moves the end of the run by x % of 696206 cycles.  Reference values: the same ROM in openMSX (tools: ltrun2.py).
   python build_logotest.py [--out file]"""
import os, sys, subprocess
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, '..', '..'))
SJ = r'F:\MSX Projects\Dev27\.claude\msx-video-tools\sjasmplus\sjasmplus-1.24.0.win\sjasmplus.exe'
arg = lambda n, d=None: sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d
OUT = arg('--out', os.path.join(PROJ, 'PM_LogoLoop_32KB_ASCII16.rom'))
LT = os.path.join(HERE, 'lt2'); os.makedirs(LT, exist_ok=True)
import shutil
shutil.copy(os.path.join(PROJ, 'game', 'tvplay.inc'), os.path.join(LT, 'tvplay.inc'))

ASM = r'''        DEVICE NOSLOT64K
TABHI   equ 0xD0
TVBANK  equ 257                         ; ASCII16: the low byte 1 = bank 1 (the data); the game's NEO16 build uses the same code with 256 + frame
TVFRAMES equ 1                          ; one video frame per run
tv_f    equ 0xC1EF
bankdummy equ 0xC1EC
sumf    equ 0xC000
sumn    equ 0xC002
lst     equ 0xC010                      ; 8 words: polls to the next vblank after each run
msx2    equ 0xC008
lptr    equ 0xC00A
        MACRO BANKHI addr
        ld (bankdummy),a
        ENDM
        ORG 0x4000
        db "AB"
        dw init
        dw 0,0,0,0,0,0
        ORG 0x4010
init:   di
        ld sp,0xF380
        ld hl,0xC000
        ld de,0xC001
        ld bc,0x12FF
        ld (hl),0
        ldir
        ld a,(0x002D)
        ld (msx2),a
        xor a
        ld (0x6000),a                   ; ASCII16: page 1 = bank 0, page 2 = bank 1 (the data of the video)
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
again:  call showwait
        ld hl,0
        ld (sumf),hl
        ld (sumn),hl
        ld hl,g2regs
        call vregs
        call waitf                      ; the ruler: polls in 8 whole frames
        ld b,8
.f:     push bc
        call countf
        ld hl,(sumf)
        add hl,bc
        ld (sumf),hl
        pop bc
        djnz .f
        ld hl,lst                       ; 8 runs of the real loop (tvplay uses IX/IY)
        ld (lptr),hl
        ld b,8
.r:     push bc
        call waitf
        call tvplay
        in a,(0x99)
        call countf
        ld hl,(lptr)
        ld (hl),c
        inc hl
        ld (hl),b
        inc hl
        ld (lptr),hl
        ld hl,(sumn)
        add hl,bc
        ld (sumn),hl
        pop bc
        djnz .r
        ld sp,0xF380
        call show
.w1:    call keys
        and 1
        jr nz,.w1
.w2:    call keys
        and 1
        jr z,.w2
        jp again

waitf:  in a,(0x99)
.w:     in a,(0x99)
        rlca
        jr nc,.w
        ret
countf: ld bc,0
.l:     in a,(0x99)
        inc bc
        rlca
        jr nc,.l
        ret
keys:   in a,(0xAA)                     ; row 8: bit 0 = SPACE (0 = pressed)
        and 0xF0
        or 8
        out (0xAA),a
        in a,(0xA9)
        cpl
        ret

vregs:  ld b,8                          ; HL = 8 register values (or 2 bytes for the status register select)
        ld c,0x80
.v:     ld a,(hl)
        out (0x99),a
        ld a,c
        out (0x99),a
        inc hl
        inc c
        djnz .v
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

txmode: ld hl,txregs                    ; text mode, name table at 0, font at 0800h (the video overwrote the VRAM)
        call vregs
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

showwait:
        call txmode
        ld hl,s_wait
        ld de,2*40+1
        jp puts

show:   call txmode
        ld hl,s_title
        ld de,0*40+1
        call puts
        ld hl,s_f
        ld de,2*40+1
        call puts
        ld hl,(sumf)
        call pdec5
        ld hl,s_n
        ld de,3*40+1
        call puts
        ld hl,(sumn)
        call pdec5
        ld hl,s_runs
        ld de,5*40+1
        call puts
        ld ix,lst
        ld b,8
        ld de,6*40+3
.l:     push bc
        push de
        call vset
        ld l,(ix+0)
        ld h,(ix+1)
        inc ix
        inc ix
        call pdec5
        pop de
        ld hl,40
        add hl,de
        ex de,hl
        pop bc
        djnz .l
        ld hl,s_k
        ld de,16*40+1
        call puts
        ld hl,s_k2
        ld de,17*40+1
        call puts
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

g2regs: db 0x02,0xC0,0x06,0xFF,0x03,0x36,0x07,0xF4
txregs: db 0x00,0xD0,0x00,0x00,0x01,0x00,0x00,0xF4
s_title: db "PM LOGO LOOP TEST (REAL TITLE LOOP)",0
s_wait: db "RUNNING ... (NO JOYSTICK FIRE / SPACE)",0
s_f:    db "FRAMES (SUM OF 8):   ",0
s_n:    db "NEXT VBLANK (SUM 8): ",0
s_runs: db "RUN  POLLS TO NEXT VBLANK",0
s_k:    db "TAKE A PHOTO. SPACE = RUN AGAIN.",0
s_k2:   db "(DON'T PRESS FIRE/SPACE DURING A RUN)",0

        INCLUDE "tvplay.inc"
        ASSERT $ < 0x8000
        ds 0x8000-$,0xFF
        SAVEBIN "code.bin",0x4000,0x4000
'''
open(os.path.join(LT, 'logotest.asm'), 'w').write(ASM)
r = subprocess.run([SJ, '--nologo', '--lst=logotest.lst', '--sym=logotest.sym', 'logotest.asm'], cwd=LT, capture_output=True, text=True)
print(r.stdout + r.stderr)
if r.returncode: sys.exit('assembly failed')
code = open(os.path.join(LT, 'code.bin'), 'rb').read()
assert len(code) == 16384
rng = np.random.RandomState(27)
with open(OUT, 'wb') as f:
    f.write(code); f.write(rng.bytes(16384))
print(OUT, os.path.getsize(OUT), 'bytes')
