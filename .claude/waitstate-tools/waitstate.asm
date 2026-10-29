; VDP wait state test (16 KB ROM): does this machine add a wait state to every write to the VDP (T9769 of the MSX2+ / turbo R)?
; Two loops of identical code and cycle count: B writes 8 bytes to the VDP data port per iteration (outi, like the title video of Puzzle Mania),
; A does the same with ini from a port nobody uses (2Eh).  Both run for NF frames, counted by the VDP interrupt (hook H.TIMI), the number of iterations
; is the result: a machine with a wait state on the VDP does fewer iterations of B (8 cycles per iteration of about 309).  The interrupt cost and the clock
; are the same for A and B and drop out of the ratio.  Two pairs A,B,A,B; SPACE runs the test again.
        DEVICE NOSLOT64K
NF      equ 4                           ; frames per run
NOM     equ 309                         ; cycles of one iteration (without waits of the VDP)
fc      equ 0xC000                      ; frame counter (the interrupt)
fcend   equ 0xC001
zbuf    equ 0xC010                      ; 8 bytes
res     equ 0xC020                      ; NP pairs of words: the iterations of A, B
mA      equ 0xC050
mB      equ 0xC052
et      equ 0xC054
NP      equ 4
        ORG 0x4000
        db "AB"
        dw init
        dw 0,0,0,0,0,0
        ORG 0x4010
init:   di
        ld sp,0xF380
        ld a,0xC3                       ; the hook of the interrupt: the frame counter
        ld (0xFD9F),a
        ld hl,tick
        ld (0xFDA0),hl
        call txmode
main:   di
        xor a
        ld (fc),a
        ld hl,res
        ld de,res+1
        ld bc,39
        ld (hl),0
        ldir
        call runA                       ; a pair to warm up (the first runs after the start of the machine can be disturbed), not used
        call runB
        ld ix,res                       ; NP pairs A, B: a run can only be slower (a long interrupt routine of the BIOS), so the best run of each counts
        ld b,NP
.p:     push bc
        call runA
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
        ld (et),hl
        call show
.w1:    call space
        jr z,.w1
.w2:    call space
        jr nz,.w2
        jp main

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

space:  in a,(0xAA)                     ; NZ = SPACE pressed
        and 0xF0
        or 8
        out (0xAA),a
        in a,(0xA9)
        cpl
        and 1
        ret

tick:   push af                         ; H.TIMI: one more frame
        ld a,(fc)
        inc a
        ld (fc),a
        pop af
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

; ---------------------------------------------------------------------------------- the two loops (identical code, B: outi to the VDP, A: ini from port 2Eh)

runB:   ld de,0x2000                    ; VRAM write address 2000h: the 8 bytes per iteration stay away from the screen
        call vset
        ei
        ld hl,fc
        ld a,(hl)
.s:     cp (hl)
        jr z,.s                         ; the next frame: the start
        ld a,(hl)
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
        ret

runA:   ei
        ld hl,fc
        ld a,(hl)
.s:     cp (hl)
        jr z,.s
        ld a,(hl)
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
        ret

; ---------------------------------------------------------------------------------- the screen
vregs:  ld b,8                          ; HL = 8 register values
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

msx2regs:                               ; MSX2 and later: R#15 = 0 (status register 0) and R#14 = 0 (VRAM address bits 16..14)
        ld a,(0x002D)
        or a
        ret z                           ; (a TMS9918A would take these writes for R#7 / R#6)
        xor a
        out (0x99),a
        ld a,0x8F
        out (0x99),a
        xor a
        out (0x99),a
        ld a,0x8E
        out (0x99),a
        ret

txmode: ld hl,txregs                    ; text mode, name table at 0, font at 0800h, the interrupt on
        call vregs
        call msx2regs
        ld de,0x0800
        call vset
        ld hl,(0x0004)                  ; the font of the BIOS
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

pdec5:  ld e,0                          ; HL = number: 5 digits at the VRAM address, no leading zeros
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

num:    push hl                         ; HL = number, DE = VRAM address
        call vset
        pop hl
        jp pdec5

show:   call msx2regs
        ld hl,s_0
        ld de,0*40+1
        call puts
        ld hl,s_1
        ld de,2*40+1
        call puts
        ld hl,s_2
        ld de,4*40+1
        call puts
        ld hl,s_3
        ld de,6*40+1
        call puts
        ld ix,res
        ld b,NP
        ld de,4*40+14
.r:     push bc
        push de
        ld l,(ix+0)
        ld h,(ix+1)
        call num
        pop de
        push de
        ld hl,2*40
        add hl,de
        ex de,hl
        ld l,(ix+2)
        ld h,(ix+3)
        call num
        pop de
        ld hl,6
        add hl,de
        ex de,hl
        ld bc,4
        add ix,bc
        pop bc
        djnz .r
        ld hl,s_4
        ld de,9*40+1
        call puts
        ld hl,(mA)
        ld de,9*40+14
        call num
        ld hl,(mB)
        ld de,9*40+22
        call num
        ld hl,s_5
        ld de,11*40+1
        call puts
        ld hl,(et)
        ld de,11*40+25
        call num
        ld hl,s_6
        ld de,13*40+1
        call puts
        ld hl,(et)                      ; 5 or more extra cycles: yes, 2 or less: no, between: maybe
        ld a,h
        or a
        ld hl,s_yes
        jr nz,.pr
        ld a,(et)
        cp 5
        jr nc,.pr
        cp 3
        ld hl,s_no
        jr c,.pr
        ld hl,s_maybe
.pr:    ld de,13*40+22
        call puts
        ld hl,s_7
        ld de,16*40+1
        call puts
        ld a,(0x002D)
        add a,'0'
        out (0x98),a
        ld hl,s_8
        ld de,18*40+1
        call puts
        ld hl,s_9
        ld de,20*40+1
        call puts
        ret

txregs: db 0x00,0xF0,0x00,0x00,0x01,0x00,0x00,0xF4
s_0:    db "VDP WAIT STATE TEST",0
s_1:    db "ITERATIONS IN 4 FRAMES, 4 RUNS EACH",0
s_2:    db "A (NO VDP)",0
s_3:    db "B (VDP)",0
s_4:    db "BEST A / B",0
s_5:    db "EXTRA CYCLES PER LOOP:",0
s_6:    db "VDP WAIT STATE:",0
s_7:    db "MSXVER: ",0
s_8:    db "0=MSX1 1=MSX2 2=MSX2+ 3=TURBO R",0
s_9:    db "SPACE = AGAIN",0
s_yes:  db "YES",0
s_no:   db "NO   ",0
s_maybe: db "MAYBE",0
        ASSERT $ < 0x8000
        ds 0x8000-$,0xFF
        SAVEBIN "waitstate.bin",0x4000,0x4000
