; ------------------------------------------------------------------------------------------------ extras: the attract mode, the confetti
anykey:                                 ; NZ = a key that the game uses, or the joystick, is down
        ld a,(mus_on)                   ; (with music the slots of the player have done this: mus_any)
        or a
        jr z,.slow
        ld a,(mus_any)
        or a
        ret
.slow:  ld a,(k8)
        or 0x0E
        ld b,a
        ld a,(k7)
        or 0x7B
        and b
        ld b,a
        ld a,(k3)
        or 0xDE
        and b
        ld b,a
        ld a,(k4)
        or 0xF5
        and b
        ld b,a
        ld a,(k5)
        or 0xFD
        and b
        ld b,a
        ld a,(joy)
        or 0xC0
        and b
        inc a
        ret

; ---- attract mode: a photo that has not been solved yet (NPHOTO photos, then the list starts again)
att_pick:
        ld hl,v_rng                     ; the time spent in the menu is the seed
        ld a,r
        xor (hl)
        ld (hl),a
.go:    call rnd
        and 15
        cp NPHOTO
        jr nc,.go
        ld e,a
        ld d,0
        ld hl,att_d
        add hl,de
        ld a,(hl)
        or a
        jr nz,.go
        ld (hl),1
        ld a,e
        ld (v_photo),a
        ld (v_sel),a
        ld hl,att_d
        ld b,NPHOTO
.c:     ld a,(hl)
        or a
        jr z,.ok
        inc hl
        djnz .c
        ld hl,att_d                     ; all done: start again (the photo of now stays marked)
        ld b,NPHOTO
        xor a
.z:     ld (hl),a
        inc hl
        djnz .z
        ld hl,att_d
        add hl,de
        inc (hl)
.ok:    call rnd                        ; the size: 3x3 or 4x4
        and 1
        add a,3
        ld (att_sz),a
        ld a,1
        ld (att_on),a
        ld (att_t),a
        ret

att_step:                               ; one frame of the attract mode in the puzzle: A = 0 go on, 1 a key was pressed, 2 solved
        call anykey
        ld a,1
        ret nz
        ld hl,att_t
        dec (hl)
        ld a,0                          ; (ld keeps the flags of the dec)
        ret nz
        ld a,(v_hz)                     ; 1 move per second
        cp 50
        ld a,ATT_DELAY
        jr z,.d
        ld a,ATT_DELAY60
.d:     ld (hl),a
        ld hl,(att_p)
        ld de,ATT_BUF
        or a
        sbc hl,de
        jr z,.fin
        ld hl,(att_p)
        dec hl
        ld (att_p),hl
        ld a,(hl)
        xor 2                           ; the opposite move
        call do_move
        call solved
        ld a,0
        ret nz
.fin:   ld a,2
        ret

; ---- confetti: sprites 4..4+NCONF-1 fall over the solved picture
crnd:   push hl
        call rnd
        pop hl
        ret

conf_init:
        ld hl,CONF
        ld b,NCONF
.i:     call crnd                       ; y
        cp 192
        jr c,.y
        sub 64
.y:     ld (hl),a
        inc hl
        call crnd                       ; x
        ld (hl),a
        inc hl
        call crnd                       ; speed 2..5
        and 3
        add a,2
        ld (hl),a
        inc hl
        call crnd                       ; drift -2..1
        and 3
        sub 2
        ld (hl),a
        inc hl
        call crnd                       ; colour 2..15
        and 15
        cp 2
        jr nc,.c
        add a,8
.c:     ld (hl),a
        inc hl
        djnz .i
        SETADDR 0x1B10+4*NCONF          ; end of the sprite list
        ld a,0xD0
        out (0x98),a
        ret

conf_step:
        ld hl,CONF
        ld b,NCONF
        SETADDR 0x1B10
.s:     ld a,(hl)                       ; y
        inc hl
        ld c,(hl)                       ; x
        inc hl
        add a,(hl)                      ; + speed
        cp 192
        jr c,.ok
        cp 0xE0
        jr nc,.ok
        ld a,0xF0                       ; below the screen: back to the top
.ok:    dec hl
        dec hl
        ld (hl),a
        VOUT
        inc hl
        inc hl
        inc hl
        ld a,c
        add a,(hl)                      ; + drift
        dec hl
        dec hl
        ld (hl),a
        VOUT                            ; (x was stored with the drift: the sprite shows the new x)
        inc hl
        inc hl
        inc hl
        ld a,b
        and 1
        add a,4                         ; pattern 4 or 5
        VOUT
        ld a,(hl)                       ; colour
        inc hl
        VOUT
        djnz .s
        ret

conf_park:                              ; the four flash sprites go below the screen (they must not end the sprite list)
        SETADDR 0x1B00
        ld b,4
.p:     ld a,0xC0
        VOUT
        xor a
        VOUT
        VOUT
        VOUT
        djnz .p
        ret

conf_end:
        SETADDR 0x1B10
        ld a,0xD0
        out (0x98),a
        ret

jwait:                                  ; about one frame, counted (a lost vertical blanking flag cannot stretch it); the keys are read
        call readkeys
        ld a,(v_hz)
        cp 50
        ld bc,JW_PAL
        jr z,.w
        ld bc,JW_NTSC
.w:     dec bc
        ld a,b
        or c
        jr nz,.w
        ret

; ---- the attract mode starts when the menu song has been played to its end without a key in its second half (about the last 15 s)
att_half:                               ; NC = the song is in its second half (the bank index in the track >= half of the number of banks)
        ld hl,(mus_e)
        ld de,(mus_s)
        or a
        sbc hl,de
        srl h
        rr l
        ex de,hl                        ; DE = half the length
        ld hl,(mus_bank)
        ld bc,(mus_s)
        or a
        sbc hl,bc
        or a
        sbc hl,de
        ret

att_init:                               ; (the menu is entered: that counts as a key; the second half counts from the next one)
        ld hl,(mus_e)                   ; att_hb = the first bank of the second half of the song (att_check compares with it in every frame)
        ld de,(mus_s)
        or a
        sbc hl,de
        srl h
        rr l
        add hl,de
        ld (att_hb),hl
        ld a,1
        ld (att_act),a
        call att_half
        ld a,1
        jr nc,.s
        xor a
.s:     ld (att_wo),a
        ret

att_check:                              ; every frame without a key: carry = the last 512 samples of the song and no key in its second half
        ld a,(mus_on)
        or a
        ret z
        ld hl,(mus_bank)                ; (the same as att_half, without its arithmetic: this runs in every idle frame, and the time counts as a gap of the music)
        ld de,(att_hb)
        or a
        sbc hl,de
        jr c,.first
        ld a,(att_wo)
        or a
        jr nz,.open
        inc a
        ld (att_wo),a                   ; the second half begins: from now on a key counts
        xor a
        ld (att_act),a
        ret
.open:  ld a,(att_act)
        or a
        ret nz                          ; a key: the song goes round again
        ld hl,(mus_e)
        dec hl
        ld de,(mus_bank)
        or a
        sbc hl,de
        jr nz,.no                       ; not the last bank
        ld a,(mus_ptr+1)
        cp 0xBE                         ; the last 512 samples are the fade-out of the track
        ccf
        ret
.no:    or a
        ret
.first: xor a
        ld (att_wo),a
        ret

att_mute:                               ; the song goes on at volume 0 (the player keeps drawing: the screen work needs it)
        ld a,4
        ld (mus_gs),a
        ld (mus_gt),a
        ld a,TABHI+12
        ld (mus_tab),a
        jp scc_gain

att_unmute:
        xor a
        ld (mus_gs),a
        ld (mus_gt),a
        ld a,TABHI
        ld (mus_tab),a
        jp scc_gain
