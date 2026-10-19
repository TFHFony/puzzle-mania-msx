; Timing test ROM (64 KB, ASCII16): tools/build_timing.py.  For every kind of bus access it counts how many times a small loop runs in one video frame
; (vblank to vblank), 50 frames per test: avg / min / max.  A pure RAM loop gives the frame length in loop rounds; every other loop adds one access to it,
; so a slower access (flash cartridge, I/O, wait states of a machine) shows as a smaller number.  The loops run from RAM (copied to C400h), except ROM EXEC.
        DEVICE NOSLOT64K
        ORG 0x4000
        db "AB"
        dw init
        dw 0,0,0,0,0,0
        ORG 0x4020

CHGMOD  equ 0x005F
CHPUT   equ 0x00A2
RAMC    equ 0xC400
TAB     equ 0xC800                      ; results: 3 words per test
lead    equ 0xC7F0
ti      equ 0xC7F1
rowi    equ 0xC7F2
colc    equ 0xC7F3
nameptr equ 0xC7F4
tabptr  equ 0xC7F6
NT      equ 9

init:   di
        ld sp,0xF380
        xor a
        ld (0x6000),a                   ; page 1 = bank 0
        call 0x0138                     ; RSLREG: page 2 = our cartridge slot
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
        ld a,1
        ld (0x7000),a                   ; page 2 = bank 1
        ld hl,ramsrc
        ld de,RAMC
        ld bc,ramend-ramsrc
        ldir
        xor a
        call CHGMOD                     ; SCREEN 0
        di
        xor a
        out (0x99),a
        ld a,0x8F                       ; R#15 = 0: the status register S#0 is read
        out (0x99),a
        ld a,0xD0                       ; R#1: 16K, display on, NO vblank interrupt (the BIOS interrupt routine would steal the vblank flag)
        out (0x99),a
        ld a,0x81
        out (0x99),a

main:   di
        ld a,12                         ; clear screen
        call CHPUT
        ld hl,s_sw1
        call prt
        di
        ld de,500
        call swait                      ; 500 frames: time it with a stopwatch
        ld hl,s_sw2
        call prt
        di
        xor a
        ld (ti),a
.t:     ld a,(ti)
        ld l,a
        ld h,0
        add hl,hl
        ld de,tests
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        push de                         ; the test routine
        ld a,(ti)
        ld l,a
        ld h,0
        ld c,l
        ld b,h
        add hl,hl
        add hl,bc
        add hl,hl                       ; 6 * test number
        ld de,TAB
        add hl,de
        ex de,hl                        ; DE = result slot
        pop hl                          ; HL = test routine
        call meas
        ld a,(ti)
        inc a
        ld (ti),a
        cp NT
        jr nz,.t
        di
        ; ---- show
        ld a,12                         ; clear screen
        call CHPUT
        ld hl,s_head
        call prt
        ld a,(0x002B)                   ; bit 7: 50 Hz
        ld de,50
        rlca
        jr c,.hz
        ld de,60
.hz:    call pdec
        ld hl,s_hz
        call prt
        ld hl,names
        ld (nameptr),hl
        ld hl,TAB
        ld (tabptr),hl
        xor a
        ld (rowi),a
.row:   ld hl,(nameptr)
        call prt
        ld (nameptr),hl
        ld a,3
        ld (colc),a
.val:   ld hl,(tabptr)
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld (tabptr),hl
        call pdec
        ld a,(colc)
        dec a
        ld (colc),a
        jr nz,.val
        ld hl,s_crlf
        call prt
        ld a,(rowi)
        inc a
        ld (rowi),a
        cp NT
        jr nz,.row
        ld hl,s_foot
        call prt
        di
        ld de,750                       ; the table stays on the screen for 15 seconds
        call swait
        jp main

prt:    ld a,(hl)                       ; print a 0 terminated string
        inc hl
        or a
        ret z
        push hl
        call CHPUT
        pop hl
        jr prt

pdec:   xor a                           ; print DE as 5 digits, leading spaces, then a space
        ld (lead),a
        ex de,hl
        ld de,10000
        call .d
        ld de,1000
        call .d
        ld de,100
        call .d
        ld de,10
        call .d
        ld a,l
        add a,'0'
        call CHPUT
        ld a,' '
        jp CHPUT
.d:     ld c,'0'-1
.l:     inc c
        or a
        sbc hl,de
        jr nc,.l
        add hl,de
        ld a,c
        cp '0'
        jr nz,.p
        ld a,(lead)
        or a
        ld a,' '
        jr z,.o
        ld a,'0'
        jr .o
.p:     ld a,1
        ld (lead),a
        ld a,c
.o:     push hl
        call CHPUT
        pop hl
        ret

s_head: db "HZ ",0
s_hz:   db "  LOOPS PER FRAME",13,10,"TEST        AVG   MIN   MAX",13,10,0
s_crlf: db 13,10,0
s_foot: db "EACH TEST: 50 FRAMES",13,10,0
s_sw1:  db "STOPWATCH: 500 FRAMES",13,10,"START NOW",13,10,0
s_sw2:  db "DONE (50 HZ: 10 S, 60 HZ: 8.3 S)",13,10,"MEASURING...",13,10,0

names:  db "RAM LOOP   ",0
        db "ROM2 READ  ",0
        db "PSG OUT    ",0
        db "PPI IN     ",0
        db "BANK WRITE ",0
        db "ROM EXEC   ",0
        db "RAM READ   ",0
        db "RAM WRITE  ",0
        db "ROM1 READ  ",0

; ------------------------------------------------------------------------------------------------ in RAM
ramsrc:
        PHASE RAMC
tests:  dw tA, tB, tC, tD, tE, tF_rom, tG, tH, tI
meas:   ld (mtest),hl                   ; HL = test routine; DE = where the results go
        ld (mres),de
        ld c,0x99
        in a,(0x99)
.s0:    in f,(c)
        jp p,.s0                        ; a vblank: the first frame starts here
        ld hl,0
        ld (sumlo),hl
        xor a
        ld (sumhi),a
        ld hl,0xFFFF
        ld (vmin),hl
        ld hl,0
        ld (vmax),hl
        ld b,50
.fr:    ld de,0
        ld hl,(mtest)
        ld a,1                          ; (value for the writes of the tests)
        call jphl
        ld hl,(sumlo)                   ; sum += DE
        add hl,de
        ld (sumlo),hl
        jr nc,.nc
        ld a,(sumhi)
        inc a
        ld (sumhi),a
.nc:    ld hl,(vmin)
        or a
        sbc hl,de
        jr c,.nmin
        ld (vmin),de
.nmin:  ld hl,(vmax)
        or a
        sbc hl,de
        jr nc,.nmax
        ld (vmax),de
.nmax:  djnz .fr
        ld hl,(sumlo)                   ; avg = sum / 50
        ld a,(sumhi)
        ld de,0
.dv:    ld bc,50
        or a
        sbc hl,bc
        jr nc,.q
        or a
        jr z,.done
        dec a
.q:     inc de
        jr .dv
.done:  ld hl,(mres)
        ld (hl),e
        inc hl
        ld (hl),d
        inc hl
        ld de,(vmin)
        ld (hl),e
        inc hl
        ld (hl),d
        inc hl
        ld de,(vmax)
        ld (hl),e
        inc hl
        ld (hl),d
        ret
jphl:   jp (hl)
swait:  ld c,0x99                       ; DE vblanks
        in a,(0x99)
.l:     in f,(c)
        jp p,.l
        dec de
        ld a,d
        or e
        jr nz,.l
        ret
mtest:  dw 0
mres:   dw 0
sumlo:  dw 0
sumhi:  db 0
vmin:   dw 0
vmax:   dw 0

tA:     ld c,0x99                       ; pure loop
.l:     inc de
        in f,(c)
        jp p,.l
        ret
tB:     ld c,0x99                       ; + read of flash in page 2
        ld hl,0x8000
.l:     ld a,(hl)
        inc de
        in f,(c)
        jp p,.l
        ret
tC:     ld c,0x99                       ; + PSG write
.l:     out (0xA0),a
        inc de
        in f,(c)
        jp p,.l
        ret
tD:     ld c,0x99                       ; + keyboard matrix port read
.l:     in a,(0xA9)
        inc de
        in f,(c)
        jp p,.l
        ret
tE:     ld c,0x99                       ; + write of the bank register (bank 1: nothing changes)
.l:     ld (0x7000),a
        inc de
        in f,(c)
        jp p,.l
        ret
tF_rom: jp tF                           ; the same pure loop, but executed from the flash in page 1
tG:     ld c,0x99                       ; + RAM read
        ld hl,0xC000
.l:     ld a,(hl)
        inc de
        in f,(c)
        jp p,.l
        ret
tH:     ld c,0x99                       ; + RAM write
.l:     ld (0xC050),a
        inc de
        in f,(c)
        jp p,.l
        ret
tI:     ld c,0x99                       ; + read of flash in page 1
        ld hl,0x4100
.l:     ld a,(hl)
        inc de
        in f,(c)
        jp p,.l
        ret
        DEPHASE
ramend:

tF:     ld c,0x99                       ; (flash: executed in place)
.l:     inc de
        in f,(c)
        jp p,.l
        ret
        ASSERT $ < 0x8000
        SAVEBIN "timing.bin",0x4000,0x4000
