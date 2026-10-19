; ------------------------------------------------------------------------------------------------ video player: set up the clip, then run the overlay (A = clip)
play:   ld l,a
        ld h,0
        add hl,hl
        add hl,hl
        ld de,cliptab
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld c,(hl)
        inc hl
        ld b,(hl)
        ld (vbank),de
        ld (vleft),bc
        ld (vbase),de
        ld (vnf),bc
        ld a,(vextra)
        ld (v_xtra),a
        jp ovl_video                    ; the player itself runs in its own ROM bank (ovl.asm, video.asm)
