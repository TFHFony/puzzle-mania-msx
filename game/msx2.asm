; ------------------------------------------------------------------------------------------------ MSX2 and later: a palette per photo (128 MB ROM)
; The photos are coded twice: for the fixed TMS9918A palette (MSX1) and for a palette of their own (tools/palette_opt.py).  On an MSX2 or later the second set
; (v_pb = offset of its banks) is shown and the palette registers of the V9938 are loaded: TMS (own screens, videos), menu (the four thumbnails), photo p, title photo.
PAL_TMS    equ 0
PAL_MENU   equ 1
PAL_PHOTO0 equ 2                        ; 2 .. 2 + NPHOTO - 1
PAL_TITLE  equ PAL_PHOTO0 + NPHOTO
PAL_SIZE0  equ PAL_TITLE + 1            ; PAL_TITLE + 1 ..: the size menu of photo p (the four buttons: a palette without the colours of the puzzle screen)
        IF MSX2PAL
msx_init:                               ; MSX version (BIOS 002Dh): 0 = MSX1
        ld a,(0x002D)
        ld (v_msx),a
        ld a,0xFF
        ld (v_pal),a
        ld a,(v_msx)
        or a
        ret z
        ld hl,PBOFFS
        ld (v_pb),hl
        ld a,0x28                       ; R#8: TP = 1: colour 0 is black, not transparent (the border colour flashes in the solved screen: the black of the photo must stay black)
        out (0x99),a
        ld a,0x88
        out (0x99),a
        ld a,PAL_TMS
        jr setpal

setpal:                                 ; A = palette 0..11 (the V9938 palette registers: R#16 = 0, 16 x (R<<4 | B, G))
        ld (v_pal),a
        ld l,a
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl
        ld de,pal_tab
        add hl,de
        xor a
        out (0x99),a
        ld a,0x90
        out (0x99),a
        ld b,32
        ld c,0x9A
        otir
        ret

need_pal:                               ; A = palette: load it if it is not the one in use (the screen is black first, while the music plays)
        ld c,a
        ld a,(v_msx)
        or a
        ret z
        ld a,(v_pal)
        cp c
        ret z
        ld a,(mus_on)
        or a
        jr z,.nb
        push bc
        call job_black
        call job_flush
        pop bc
.nb:    ld a,c
        jr setpal
        ELSE
msx_init:
need_pal:
        ret
        ENDIF
