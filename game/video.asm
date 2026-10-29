; ------------------------------------------------------------------------------------------------ video player (runs in the overlay bank)
; vbank, vleft, vbase, vnf and v_xtra are set by play (vplay.asm, code bank)
ov_main: ld hl,0x8000
        ld (vptr),hl
vframe: ld a,(v_xtra)                   ; 8 fps ROM: one extra vertical blanking per frame (6 fields at 50 Hz, 7 at 60 Hz)
        or a
        jr z,.ne
        call ov_vsync
.ne:    ld a,8                          ; SPACE?
        call ov_row
        and 1
        ret z
        ld a,7                          ; ESC?
        call ov_row
        and 4
        ret z
        ld a,15                         ; joystick fire A?
        out (0xA0),a
        in a,(0xA2)
        and 0xBF
        out (0xA1),a
        ld a,14
        out (0xA0),a
        in a,(0xA2)
        and 0x10
        ret z
        call vsetb
        in a,(0x99)
.wv:    in a,(0x99)
        rlca
        jr nc,.wv
        ld hl,(vptr)
        ld c,0x98
        SETADDR 0x0000
        REPT BURST
        outi
        ENDR
        call wr256
        call wr256
        call wr256
        call wr256
        ld b,2048-BURST-1024
        ld a,b
.rest:  outi
        jp nz,.rest
        call bchk
        SETADDR 0x2000
        call blk2k
        call bchk
        SETADDR 0x0800
        call blk2k
        call bchk
        SETADDR 0x2800
        call blk2k
        call bchk
        SETADDR 0x1000
        call blk2k
        call bchk
        SETADDR 0x3000
        call blk2k
        call bchk
        ld (vptr),hl
        ld hl,(vleft)
        dec hl
        ld (vleft),hl
        ld a,h
        or l
        jp nz,vframe
        ld a,(att_on)                   ; attract mode: the clip plays once
        or a
        ret nz
        ld hl,(vbase)
        ld (vbank),hl
        ld hl,0x8000
        ld (vptr),hl
        ld hl,(vnf)
        ld (vleft),hl
        jp vframe

vsetb:  ld a,(vbank)
        ld (0x7000),a
        ld a,(vbank+1)
        BANKHI 0x7001
        ret

bchk:   ld a,h                          ; the frames are packed: a bank holds 8 blocks of 2 KB and a frame takes 6
        cp 0xC0
        ret nz
        push hl
        ld hl,(vbank)
        inc hl
        ld (vbank),hl
        ld a,l
        ld (0x7000),a
        ld a,h
        BANKHI 0x7001
        pop hl
        ld hl,0x8000
        ret

wr256:  ld b,0
.l:     outi
        jp nz,.l
        ret

blk2k:  call wr256
        call wr256
        call wr256
        call wr256
        call wr256
        call wr256
        call wr256
        jp wr256


ov_row: ld b,a                          ; keyboard row A -> A (0 = pressed)
        in a,(0xAA)
        and 0xF0
        or b
        out (0xAA),a
        in a,(0xA9)
        ret

ov_vsync:
        in a,(0x99)
.w:     in a,(0x99)
        rlca
        jr nc,.w
        ret
