; ------------------------------------------------------------------------------------------------ VDP wait state test (runs from the RAM, copied out of the bank SELFTEST)
; Does this machine add a wait state to every write to the VDP (the T9769 of some MSX2+ and the turbo R)?  The title video loop (8 VDP writes per iteration of 446 cycles) then
; runs 1.8 % slow and its music is too low.  Two loops of identical code and cycle count: B writes 8 bytes to the VDP data port per iteration (outi), A does the same with
; ini from port 2Eh (unused).  Both run for NF frames (counted by the VDP interrupt, hook H.TIMI) and count their iterations: a wait state makes B do fewer.  The interrupt
; costs and the clock are the same for A and B and drop out of the ratio.  Test: a pair to warm up, NP pairs A, B, the best run of each counts (a long interrupt routine of the
; BIOS can only make a run slower).  Result: v_wait = extra cycles per iteration (0 or 8), v_tvd = 1 when 5 or more.
; The screen is off during the test (R#1), nothing can be seen; the VRAM bytes go to 2000h.. (the colour table: 2 frames x 8 bytes x ~230 iterations, all black afterwards).
; tools/build_game.py assembles this file and puts it in the bank SELFTEST behind the signature.
        DEVICE NOSLOT64K
        INCLUDE "wtequ.inc"
NF      equ 2                           ; frames per run
NP      equ 4                           ; pairs
NOM     equ 309                         ; cycles of one iteration (without waits of the VDP)
fc      equ WT_VARS                     ; frame counter (the interrupt)
fcend   equ WT_VARS + 1
hsave   equ WT_VARS + 2                 ; 3 bytes: the original hook
res     equ WT_VARS + 8                 ; NP pairs of words: the iterations of A, B
mA      equ WT_VARS + 0x30
mB      equ WT_VARS + 0x32
zbuf    equ WT_VARS + 0x40              ; 8 bytes
        ORG WT_RAM
wt_run: di
        ld hl,0xFD9F                    ; H.TIMI: count the frames
        ld de,hsave
        ld bc,3
        ldir
        ld a,0xC3
        ld (0xFD9F),a
        ld hl,wt_tick
        ld (0xFDA0),hl
        ld a,0xA0                       ; R#1: display off, interrupt on
        out (0x99),a
        ld a,0x81
        out (0x99),a
        ld a,(0x002D)
        or a
        jr z,.m1
        xor a                           ; MSX2 and later: R#15 = 0 (status register 0), R#14 = 0
        out (0x99),a
        ld a,0x8F
        out (0x99),a
        xor a
        out (0x99),a
        ld a,0x8E
        out (0x99),a
.m1:    xor a
        ld (fc),a
        ld hl,res
        ld de,res+1
        ld bc,0x37
        ld (hl),0
        ldir
        call runA                       ; a pair to warm up (the first runs after the start can be disturbed), not used
        jr c,.fail
        call runB
        ld ix,res
        ld b,NP
.p:     push bc
        call runA
        jr c,.fp
        ld (ix+0),e
        ld (ix+1),d
        call runB
        ld (ix+2),e
        ld (ix+3),d
        ld bc,4
        add ix,bc
        pop bc
        djnz .p
        di
        ld ix,res
        call maxw
        ld (mA),hl
        ld ix,res+2
        call maxw
        ld (mB),hl
        ex de,hl
        ld hl,(mA)
        call calc
        ld a,h
        or a
        ld a,l
        jr z,.ok
        ld a,255
        jr .ok
.fp:    pop bc
.fail:  xor a                           ; no interrupts: the loop of 446 cycles
.ok:    ld (v_wait),a
        cp 5
        ld a,0
        jr c,.s
        inc a
.s:     ld (v_tvd),a
        di
        ld hl,hsave
        ld de,0xFD9F
        ld bc,3
        ldir
        ld a,0x80                       ; R#1: 16K, display off, no interrupt: the test has dirtied the colour table, the game puts it right and then switches the display on (pm.asm)
        out (0x99),a
        ld a,0x81
        out (0x99),a
        ret

wt_tick:                                ; H.TIMI: one more frame
        push af
        ld a,(fc)
        inc a
        ld (fc),a
        pop af
        ret

maxw:   ld hl,0                         ; IX = the first of NP words (4 bytes apart) -> HL = the largest
        ld b,NP
        ld de,4
.m:     push bc
        ld c,(ix+0)
        ld b,(ix+1)
        push hl
        or a
        sbc hl,bc
        pop hl
        jr nc,.k
        ld h,b
        ld l,c
.k:     add ix,de
        pop bc
        djnz .m
        ret

calc:   or a                            ; HL = A (iterations), DE = B -> HL = (A - B) * NOM / B, 0 when A <= B
        sbc hl,de
        jr c,.z
        jr z,.z
        push de
        ld b,h
        ld c,l
        ld hl,0
        ld de,NOM
.m:     add hl,de                       ; HL = (A - B) * NOM
        dec bc
        ld a,b
        or c
        jr nz,.m
        pop de                          ; DE = B
        ld bc,0
.d:     or a
        sbc hl,de
        jr c,.dn
        inc bc
        jr .d
.dn:    ld h,b
        ld l,c
        ret
.z:     ld hl,0
        ret

sync:   ld hl,fc                        ; wait for the next frame tick; C = interrupts do not come
        ld a,(hl)
        ld bc,0
.s:     cp (hl)
        jr nz,.ok
        dec bc
        ld a,b
        or c
        ld a,(fc)
        jr nz,.s
        scf
        ret
.ok:    or a
        ret

runB:   ld de,0x2000                    ; VRAM write address 2000h
        ld a,e
        out (0x99),a
        ld a,d
        or 0x40
        out (0x99),a
        ei
        call sync
        ret c
        ld a,(fc)
        add a,NF
        ld (fcend),a
        ld de,0
.it:    ld hl,zbuf
        ld b,8
        ld c,0x98
        outi
        ld a,r
        outi
        ld a,r
        outi
        ld a,r
        outi
        ld a,r
        outi
        ld a,r
        outi
        ld a,r
        outi
        ld a,r
        outi
        inc de
        ld a,(fcend)
        ld hl,fc
        cp (hl)
        jr nz,.it
        di
        or a
        ret

runA:   ei
        call sync
        ret c
        ld a,(fc)
        add a,NF
        ld (fcend),a
        ld de,0
.it:    ld hl,zbuf
        ld b,8
        ld c,0x2E
        ini
        ld a,r
        ini
        ld a,r
        ini
        ld a,r
        ini
        ld a,r
        ini
        ld a,r
        ini
        ld a,r
        ini
        ld a,r
        ini
        inc de
        ld a,(fcend)
        ld hl,fc
        cp (hl)
        jr nz,.it
        di
        or a
        ret

wt_end:
        ASSERT wt_end - WT_RAM <= WT_LEN
        SAVEBIN "wtest.bin",WT_RAM,wt_end - WT_RAM
