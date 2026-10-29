; ------------------------------------------------------------------------------------------------ VDP helpers

nametab: SETADDR 0x1800                 ; identity name table 0..255 three times
        ld d,3
.nt:    xor a
        ld b,0
.ntl:   out (0x98),a
        inc a
        nop
        djnz .ntl
        dec d
        jr nz,.nt
        ret

sprpat: SETADDR 0x3800                  ; four corner sprites (8x8), sprite 4 = end of the list
        ld hl,sprdata
        ld b,48
        ld c,0x98
.l:     outi
        nop
        jp nz,.l
        SETADDR 0x1B10
        ld a,0xD0
        out (0x98),a
        ret
sprdata: db 0xFF,0xFF,0xC0,0xC0,0xC0,0xC0,0xC0,0xC0
        db 0xFF,0xFF,0x03,0x03,0x03,0x03,0x03,0x03
        db 0xC0,0xC0,0xC0,0xC0,0xC0,0xC0,0xFF,0xFF
        db 0x03,0x03,0x03,0x03,0x03,0x03,0xFF,0xFF
        db 0x00,0x7E,0x7E,0x7E,0x7E,0x7E,0x7E,0x00      ; confetti: square, diamond
        db 0x18,0x3C,0x7E,0xFF,0xFF,0x7E,0x3C,0x18

clrscr: SETADDR 0x0000                  ; all patterns 0, all colours black on black
        ld de,6144
        xor a
.p:     out (0x98),a
        dec de
        ld c,a
        ld a,d
        or e
        ld a,c
        jr nz,.p
        SETADDR 0x2000
        ld de,6144
        ld a,0x11
.c:     out (0x98),a
        dec de
        ld c,a
        ld a,d
        or e
        ld a,c
        jr nz,.c
        ret

vsync:  in a,(0x99)
.w:     in a,(0x99)
        rlca
        jr nc,.w
        jp readkeys

setbank: ld a,l                         ; HL = ROM bank in the page 2 window (8000h)
        ld (0x7000),a
        ld a,h
        BANKHI 0x7001
        ret

setpb:  ld c,a                          ; A = photo, B = k -> bank 1 + 10 * photo + k
        add a,a
        add a,a
        add a,c
        add a,a
        add a,b
        inc a
        ld l,a
        ld h,0
        push de
        ld de,(v_pb)                    ; (the MSX2 version: the photos for their own palette)
        add hl,de
        pop de
        jr setbank

; blit: w*h chars (pattern + colour) from the page 2 window to the screen
; in: HL = source pattern pointer of the first char, D = dest char row, E = dest char column*8, b_w, b_h, b_ss8 (source row stride in bytes), b_cofs (colour offset)
blit:   ld a,(b_h)
        ld (b_rows),a
.row:   push hl
        push de
        ld a,(b_w)
        ld (b_cols),a
.chr:   push hl
        ld a,e
        out (0x99),a
        ld a,d
        or 0x40
        out (0x99),a
        ld b,8
        ld c,0x98
.p:     outi
        jp nz,.p
        pop hl
        push hl
        ld bc,(b_cofs)
        add hl,bc
        ld a,e
        out (0x99),a
        ld a,d
        add a,0x20
        or 0x40
        out (0x99),a
        ld b,8
        ld c,0x98
.c:     outi
        jp nz,.c
        pop hl
        ld bc,8
        add hl,bc
        ld a,e
        add a,8
        ld e,a
        ld a,(b_cols)
        dec a
        ld (b_cols),a
        jr nz,.chr
        pop de
        pop hl
        inc d
        ld bc,(b_ss8)
        add hl,bc
        ld a,(b_rows)
        dec a
        ld (b_rows),a
        jr nz,.row
        ret

; blankblk: black w*h chars at D = row, E = column*8
blankblk: ld a,(b_h)
        ld (b_rows),a
.row:   push de
        ld a,(b_w)
        ld (b_cols),a
.chr:   ld a,e
        out (0x99),a
        ld a,d
        or 0x40
        out (0x99),a
        ld b,8
        xor a
.p:     out (0x98),a
        nop
        djnz .p
        ld a,e
        out (0x99),a
        ld a,d
        add a,0x20
        or 0x40
        out (0x99),a
        ld b,8
        ld a,0x11
.c:     out (0x98),a
        nop
        djnz .c
        ld a,e
        add a,8
        ld e,a
        ld a,(b_cols)
        dec a
        ld (b_cols),a
        jr nz,.chr
        pop de
        inc d
        ld a,(b_rows)
        dec a
        ld (b_rows),a
        jr nz,.row
        ret

; text: HL = string, D = row, E = column, A = colour byte (foreground << 4 | background)
text:   ld (t_col),a
        ld a,e
        add a,a
        add a,a
        add a,a
        ld e,a
.next:  ld a,(hl)
        or a
        ret z
        inc hl
        push hl
        ld l,a
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        ld bc,(v_font)
        add hl,bc
        ld a,e
        out (0x99),a
        ld a,d
        or 0x40
        out (0x99),a
        ld b,8
        ld c,0x98
.p:     outi
        jp nz,.p
        ld a,e
        out (0x99),a
        ld a,d
        add a,0x20
        or 0x40
        out (0x99),a
        ld a,(t_col)
        ld b,8
.c:     out (0x98),a
        nop
        djnz .c
        ld a,e
        add a,8
        ld e,a
        pop hl
        jr .next

; boldtext: HL = string, D = row, E = column; 8x8 glyphs made bold, upper 4 pixel rows grey, lower 4 white
boldtext:
        ld a,e
        add a,a
        add a,a
        add a,a
        ld e,a
.next:  ld a,(hl)
        or a
        ret z
        inc hl
        push hl
        ld l,a
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        ld bc,(v_font)
        add hl,bc
        ld a,e
        out (0x99),a
        ld a,d
        or 0x40
        out (0x99),a
        ld b,8
.p:     ld a,(hl)
        ld c,a
        srl a
        or c
        out (0x98),a
        inc hl
        djnz .p
        ld a,e
        out (0x99),a
        ld a,d
        add a,0x20
        or 0x40
        out (0x99),a
        ld a,0xE1
        ld b,4
.c1:    out (0x98),a
        nop
        djnz .c1
        ld a,0xF1
        ld b,4
.c2:    out (0x98),a
        nop
        djnz .c2
        ld a,e
        add a,8
        ld e,a
        pop hl
        jr .next

; boldcol: like boldtext, but one colour byte (A = foreground << 4 | background) for all eight pixel rows
boldcol:
        ld (t_col),a
        ld a,e
        add a,a
        add a,a
        add a,a
        ld e,a
.next:  ld a,(hl)
        or a
        ret z
        inc hl
        push hl
        cp 1                            ; character 1 = the copyright sign (a circle with a C, one character)
        ld hl,gl_copy
        jr z,.g
        ld l,a
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        ld bc,(v_font)
        add hl,bc
.g:     ld a,e
        out (0x99),a
        ld a,d
        or 0x40
        out (0x99),a
        ld b,8
.p:     ld a,(hl)
        ld c,a
        srl a
        or c
        out (0x98),a
        inc hl
        djnz .p
        ld a,e
        out (0x99),a
        ld a,d
        add a,0x20
        or 0x40
        out (0x99),a
        ld a,(t_col)
        ld b,8
.c:     out (0x98),a
        nop
        djnz .c
        ld a,e
        add a,8
        ld e,a
        pop hl
        jr .next

gl_copy: db 0x3C,0x42,0x99,0xA1,0xA1,0x99,0x42,0x3C

fptr:   ld l,a                          ; A = character -> HL = its 8 font bytes
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        ld bc,(v_font)
        add hl,bc
        ret

; cursor: 4 corner sprites around the pixel rectangle v_cx,v_cy,v_cw,v_ch; written only when something changed (call right after vsync)
setcursor:
        ld a,(v_ccol)
        or a
        jr nz,.c
        ld a,(v_frame)
        and 0x10
        ld a,11
        jr z,.c
        ld a,9
.c:     ld e,a
        ld hl,sc_last
        ld a,(v_cx)
        cp (hl)
        jr nz,.upd
        inc hl
        ld a,(v_cy)
        cp (hl)
        jr nz,.upd
        inc hl
        ld a,(v_cw)
        cp (hl)
        jr nz,.upd
        inc hl
        ld a,(v_ch)
        cp (hl)
        jr nz,.upd
        inc hl
        ld a,e
        cp (hl)
        ret z
.upd:   ld hl,sc_last
        ld a,(v_cx)
        ld (hl),a
        inc hl
        ld a,(v_cy)
        ld (hl),a
        inc hl
        ld a,(v_cw)
        ld (hl),a
        inc hl
        ld a,(v_ch)
        ld (hl),a
        inc hl
        ld (hl),e
        SETADDR 0x1B00
        ld a,(v_cy)
        dec a
        ld d,a                          ; top Y
        ld a,(v_cy)
        ld hl,v_ch
        add a,(hl)
        sub 9
        ld h,a                          ; bottom Y
        ld a,(v_cx)
        ld b,a                          ; left X
        ld l,a
        ld a,(v_cw)
        add a,l
        sub 8
        ld c,a                          ; right X
        ld a,d
        VOUT
        ld a,b
        VOUT
        xor a
        VOUT
        ld a,e
        VOUT
        ld a,d
        VOUT
        ld a,c
        VOUT
        ld a,1
        VOUT
        ld a,e
        VOUT
        ld a,h
        VOUT
        ld a,b
        VOUT
        ld a,2
        VOUT
        ld a,e
        VOUT
        ld a,h
        VOUT
        ld a,c
        VOUT
        ld a,3
        VOUT
        ld a,e
        VOUT
        ret

hidecursor: SETADDR 0x1B00
        ld a,0xD0
        out (0x98),a
        ld a,0xFF
        ld (sc_last),a                  ; the next setcursor has to write again
        xor a
        ld (v_ccol),a
        ret

; ------------------------------------------------------------------------------------------------ keyboard (matrix, read once per frame: no BIOS)
row:    ld b,a                          ; A = keyboard row -> A = bits (0 = pressed)
        in a,(0xAA)
        and 0xF0
        or b
        out (0xAA),a
        in a,(0xA9)
        ret

readkeys:                               ; rows 8, 7, 3, 4, 5 -> k8, k7, k3, k4, k5 (about 90 us)
        push bc
        ld a,8
        call row
        ld (k8),a
        ld a,7
        call row
        ld (k7),a
        ld a,3
        call row
        ld (k3),a
        ld a,4
        call row
        ld (k4),a
        ld a,5
        call row
        ld (k5),a
        ld a,15                         ; joystick port 1: the same merge as in the slots of the player
        out (0xA0),a
        in a,(0xA2)
        and 0xBF
        out (0xA1),a
        ld a,14
        out (0xA0),a
        in a,(0xA2)
        ld (joy),a
        ld c,a
        and 0x14                        ; fire A + left together = ESC (row 7) and nothing else
        sub 1
        sbc a,a
        ld b,a
        and 4
        cpl
        ld d,a
        ld a,(k7)
        and d
        ld (k7),a
        ld a,b
        and 0x14
        or c
        ld c,a
        and 0x0F
        ld e,a
        ld d,0
        ld hl,jtabc
        add hl,de
        ld b,(hl)
        ld a,c
        rrca
        rrca
        rrca
        rrca
        or 0xFE
        and b
        ld b,a
        ld a,(k8)
        and b
        ld (k8),a
        ld a,c
        or 0xDF
        ld b,a
        ld a,(k3)
        and b
        ld (k3),a
        pop bc
        ret

jtabc:  REPT 16, d                      ; (the same table as jtab in the player)
        db 0x0F | ((((d >> 3) & 1) << 7) | (((d >> 1) & 1) << 6) | ((d & 1) << 5) | (((d >> 2) & 1) << 4))
        ENDR

getdir:                                 ; A = 1 (up), 3 (right), 5 (down), 7 (left) for one cursor key, else 0
        ld a,(k8)
        cpl
        and 0xF0
        cp 0x20
        jr z,.up
        cp 0x80
        jr z,.rt
        cp 0x40
        jr z,.dn
        cp 0x10
        jr z,.lf
        xor a
        ret
.up:    ld a,1
        ret
.rt:    ld a,3
        ret
.dn:    ld a,5
        ret
.lf:    ld a,7
        ret

getfire:                                ; NZ = SPACE or RETURN
        ld a,(k8)
        and 1
        jr z,.y
        ld a,(k7)
        and 0x80
        jr z,.y
        xor a
        ret
.y:     ld a,0xFF
        or a
        ret

getesc: ld a,(k7)
        and 4
        ret                             ; Z = pressed

getn:   ld a,(k4)
        and 8
        ret                             ; Z = pressed

geth:   ld a,(k3)
        and 0x20
        ret                             ; Z = pressed

keyedge:                                ; A = keys that went down since the last call: bit 0 L, bit 1 C, bit 2 T
        ld a,(mus_on)                   ; (with music the slots of the player collect them: mus_ke, latched)
        or a
        jr z,.slow
        ld a,(mus_ke)
        ld b,a
        xor a
        ld (mus_ke),a
        ld a,b
        ret
.slow:  ld c,0
        ld a,(k4)
        and 2
        jr nz,.nl
        set 0,c
.nl:    ld a,(k3)
        and 1
        jr nz,.nc
        set 1,c
.nc:    ld a,(k5)
        and 2
        jr nz,.nt
        set 2,c
.nt:    ld a,(p_ek)
        cpl
        and c
        ld b,a
        ld a,c
        ld (p_ek),a
        ld a,b
        ret

wait_release:                           ; until SPACE / RETURN / ESC / H are up
        call mvsync
        call getfire
        jr nz,wait_release
        call getesc
        jr z,wait_release
        call geth
        jr z,wait_release
        ret

; getkey: A = orthogonal direction (1,3,5,7) on press / auto-repeat, else 0
getkey: ld a,(mus_on)                   ; (with music the slots of the player have done this: mus_dkey)
        or a
        jr z,.slow
        ld a,(mus_dkey)
        ret
.slow:  call getdir
        ld b,a
        and 1
        ld a,b
        jr z,.none
        ld hl,v_pdir
        cp (hl)
        jr nz,.new
        ld hl,v_rep
        dec (hl)
        jr nz,.zero
        ld (hl),4
        ret
.new:   ld (v_pdir),a
        ld a,16
        ld (v_rep),a
        ld a,b
        ret
.zero:  xor a
        ret
.none:  xor a
        ld (v_pdir),a
        ret

; ------------------------------------------------------------------------------------------------ small helpers
rnd:    ld hl,(v_rng)                   ; xorshift16, A = high byte
        ld a,h
        rra
        ld a,l
        rra
        xor h
        ld h,a
        ld a,l
        rra
        ld a,h
        rra
        xor l
        ld l,a
        xor h
        ld h,a
        ld (v_rng),hl
        ret

mulbc:  ld hl,0                         ; HL = B * C
        ld a,b
        or a
        ret z
        ld d,0
        ld e,c
.l:     add hl,de
        djnz .l
        ret

dec16:                                  ; HL = number -> ASCII digits at (DE), no leading zeros, 0 terminated; DE ends on the terminator
        xor a
        ld (v_tmp),a
        ld bc,-10000
        call .dg
        ld bc,-1000
        call .dg
        ld bc,-100
        call .dg
        ld bc,-10
        call .dg
        ld a,l
        add a,'0'
        ld (de),a
        inc de
        xor a
        ld (de),a
        ret
.dg:    ld a,'0'-1
.l:     inc a
        add hl,bc
        jr c,.l
        sbc hl,bc
        ld b,a
        ld a,(v_tmp)
        or a
        jr nz,.w
        ld a,b
        cp '0'
        ret z
        ld a,1
        ld (v_tmp),a
.w:     ld a,b
        ld (de),a
        inc de
        ret
