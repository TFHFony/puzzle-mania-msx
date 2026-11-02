; ------------------------------------------------------------------------------------------------ jigsaw outro player (runs in the overlay bank, entry 4003h)
; The picture of the title falls apart as a jigsaw (tools/jigsaw.py).  (vbank) = the first bank of the stream, which holds the VRAM bytes that change per frame:
;   n, address low, address high | 40h, n * 8 bytes   a record (n = 1..250 cells: the pattern table at 0, the colour table at 2000h)
;   0, e                                               the end of a frame: one vertical blanking, then e more
;   255 = the next bank, 254 = the end.   Out: carry = a key (SPACE, RETURN, fire) stopped it.
; The loop writes 26 cycles per byte, the same as the clip player.
ov_jig: ld hl,0x8000
        call vsetb
        ld c,0x98
jrec:   ld a,(hl)
        inc hl
        or a
        jr z,jfend
        cp 254
        jr nc,jspec
        ld e,a
        ld a,(hl)
        inc hl
        out (0x99),a
        ld a,(hl)
        inc hl
        out (0x99),a
jcell:  ld b,8
jp8:    outi
        jp nz,jp8
        dec e
        jr nz,jcell
        jr jrec
jspec:  inc a                           ; 255 -> 0: the next bank, 254 -> 255: the end
        jr nz,jend
        ld hl,(vbank)
        inc hl
        ld (vbank),hl
        call vsetb
        ld hl,0x8000
        jr jrec
jend:   or a
        ret
jfend:  ld d,(hl)
        inc hl
        call ov_vsync
        call jkeys
        ret c
jx:     ld a,d
        or a
        jr z,jrec
        dec d
        call ov_vsync
        call jkeys
        ret c
        jr jx

jkeys:  ld a,8                          ; SPACE, RETURN or the fire button of a joystick: carry
        call ov_row
        and 1
        jr z,.p
        ld a,7
        call ov_row
        and 0x80
        jr z,.p
        ld a,15
        out (0xA0),a
        in a,(0xA2)
        and 0xBF
        out (0xA1),a
        ld a,14
        out (0xA0),a
        in a,(0xA2)
        and 0x10
        jr z,.p
        or a
        ret
.p:     scf
        ret
