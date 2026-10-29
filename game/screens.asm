; ------------------------------------------------------------------------------------------------ start-up checks
hzdetect:                               ; v_hz = 50 or 60 (BIOS: bit 7 of 002Bh set = 50 Hz)
        ld a,(0x002B)
        rlca
        ld a,50
        jr c,.s
        ld a,60
.s:     ld (v_hz),a
        ret

selftest:                               ; the NEO16 mapper must switch the page 2 window: bank SELFTEST holds a signature, bank 0 starts with "AB"
        ld hl,SELFTEST
        call setbank
        ld hl,0x8000
        ld de,st_sig
        ld b,8
.c:     ld a,(de)
        cp (hl)
        jr nz,.bad
        inc hl
        inc de
        djnz .c
        ld hl,0
        call setbank
        ld a,(0x8000)
        cp 'A'
        jr nz,.bad
        ld a,(0x8001)
        cp 'B'
        jr nz,.bad
        jp wt_go                        ; the VDP wait state test (wtest.asm)
.bad:   call clrscr                     ; no NEO16 mapper: say so instead of showing a black screen
        ld hl,s_bad1
        ld d,6
        ld e,5
        call boldtext
        ld hl,s_bad2
        ld d,10
        ld e,2
        ld a,0xF1
        call text
        ld hl,s_bad3
        ld d,12
        ld e,2
        ld a,0xF1
        call text
        ld hl,s_bad4
        ld d,14
        ld e,2
        ld a,0xF1
        call text
        ld hl,s_bad5
        ld d,18
        ld e,2
        ld a,0x41
        call text
        di
.h:     jr .h

wt_go:                                  ; the VDP wait state test: out of the bank SELFTEST into the RAM, it runs there (wtest.asm; v_wait, v_tvd)
        ld hl,SELFTEST
        call setbank
        ld hl,0x8010
        ld de,WT_RAM
        ld bc,WT_LEN
        ldir
        ld hl,0
        call setbank
        jp WT_RAM

; ------------------------------------------------------------------------------------------------ wipes: full screen pictures, drawn with the block routines
wipe_clear:                             ; black wipe from the top and the bottom to the middle (12 frames)
        ld a,32
        ld (b_w),a
        ld a,1
        ld (b_h),a
        xor a
        ld (v_i),a
.l:     call mvsync
        ld a,(v_i)
        ld d,a
        ld e,0
        call blankblk
        ld a,23
        ld hl,v_i
        sub (hl)
        ld d,a
        ld e,0
        call blankblk
        ld hl,v_i
        inc (hl)
        ld a,(hl)
        cp 12
        jr nz,.l
        ret

wipe_in:                                ; HL = bank of a full screen picture: appears from the middle to the top and the bottom (12 frames)
        ld (v_dd),hl
        ld hl,256
        ld (b_ss8),hl
        ld hl,0x1800
        ld (b_cofs),hl
        ld a,32
        ld (b_w),a
        ld a,1
        ld (b_h),a
        xor a
        ld (v_i),a
.l:     call mvsync
        ld hl,(v_dd)
        call setbank
        ld a,11
        ld hl,v_i
        sub (hl)
        ld d,a
        add a,0x80
        ld h,a
        ld l,0
        ld e,0
        call blit
        ld a,12
        ld hl,v_i
        add a,(hl)
        ld d,a
        add a,0x80
        ld h,a
        ld l,0
        ld e,0
        call blit
        ld hl,v_i
        inc (hl)
        ld a,(hl)
        cp 12
        jr nz,.l
        ret

showpic:                                ; HL = bank of a full screen picture
        push hl
        ld a,PAL_TMS
        call need_pal
        pop hl
        ld a,(mus_on)
        or a
        jp nz,job_pic                   ; the music goes on: the picture builds up in the sample loop of the player
        call setbank
        ld hl,256
        ld (b_ss8),hl
        ld hl,0x1800
        ld (b_cofs),hl
        ld a,32
        ld (b_w),a
        ld a,24
        ld (b_h),a
        ld hl,0x8000
        ld de,0
        jp blit

; ------------------------------------------------------------------------------------------------ intro: FONY logo, title; help and credits
welcome:                                ; the FONY logo of the disk version with its jingle (SPACE skips), then the PUZZLE MANIA title until SPACE
        ld a,2                          ; track 2: the jingle (0.7 s of silence in front: it starts when the colours of the logo are in)
        ld c,0
        call music_play
        IF MSX2PAL
        ld a,(v_msx)
        or a
        jr z,.m1
        call intro                      ; MSX2 and later: the logo in SCREEN 5 with its colours coming in one by one (intro.asm), back in SCREEN 2
        call nametab
        call sprpat
        jr .go
.m1:
        ENDIF
        ld hl,FONY                      ; MSX1: the same picture in the 15 colours of the TMS9918A, with the wipe
        call wipe_in
        ld a,(v_hz)                     ; the logo stays 2.52 s from the start (the wipe is 12 frames)
        cp 50
        ld b,114
        jr z,.f
        ld b,139
.f:     push bc
        call mvsync
        call getfire
        pop bc
        jr nz,.sk
        djnz .f
.sk:    call music_stop
        call wait_release
        call wipe_clear
        jr title
.go:    call music_stop
        call wait_release
title:                                  ; the PUZZLE MANIA title for the length of the song (SPACE / fire skips it)
        IF TITLEVIDEO
        ld a,(v_tit)                    ; the video and the photo take turns
        or a
        jr nz,.photo
        inc a
        ld (v_tit),a
        ld a,PAL_TMS
        call need_pal
        ld hl,TITLEV
        call wipe_in
        IF SCC
        ld a,(v_sccm)
        or a
        jr z,.tvp
        call scc_tvstart                ; an SCC: its own stream, 16 kHz (tvplay16.inc, w_tvplay16 for a machine with a VDP wait state)
        ld a,(v_tvd)
        or a
        jr nz,.t16w
        call tvplay16
        jr .t16e
.t16w:  call w_tvplay16
.t16e:  call scc_off
        jp wait_release
.tvp:
        ENDIF
        ld a,(v_tvd)                    ; video and music in one stream (tvplay.inc, tv8_tvplay: 8 cycles less per iteration for a VDP wait state)
        or a
        jr nz,.tvw
        call tvplay
        jp wait_release
.tvw:   call tv8_tvplay
        jp wait_release
.photo: xor a
        ld (v_tit),a
        ENDIF
        ld hl,WELCOME
        ld a,PAL_TMS
        IF MSX2PAL
        ld c,a
        ld a,(v_msx)
        or a
        ld a,c
        jr z,.w1
        ld hl,WELCOME2                  ; MSX2: the title photo for its own palette
        ld a,PAL_TITLE
.w1:
        ENDIF
        push hl
        call need_pal
        pop hl
        call wipe_in
        xor a
        ld c,1
        call music_play
        ld a,(v_hz)                     ; 28.7 s, the length of the menu song
        cp 50
        ld hl,1435
        jr z,.t
        ld hl,1722
.t:     ld (v_tmp2),hl
.w:     call mvsync
        call selchk
        ld hl,(v_rng)
        inc hl
        ld (v_rng),hl
        call getfire
        jr nz,.d
        ld hl,(v_tmp2)
        dec hl
        ld (v_tmp2),hl
        ld a,h
        or l
        jr nz,.w
.d:     jp wait_release

; the help and the credits are drawn at once (a wipe would disturb the music); the wipes above only run while the music is not playing yet
howto:                                  ; two pages, SPACE = next, ESC = leave
        ld hl,HOWTO
        call .page
        ret c
        ld hl,HOWTO+1
.page:  call showpic
        call wait_release
.k:     call mvsync
        ld hl,(v_rng)
        inc hl
        ld (v_rng),hl
        call getesc
        jr z,.esc
        call getfire
        jr z,.k
        call wait_release
        or a                            ; NC: continue
        ret
.esc:   call wait_release
        scf
        ret

credits:                                ; outro, called with ESC in the main menu
        ld hl,CREDITS
        call showpic
        call wait_release
.k:     call mvsync
        call getesc
        jr z,.o
        call getfire
        jr z,.k
.o:     jp wait_release

; ------------------------------------------------------------------------------------------------ texts
st_sig:  db "NEO16OK!"
s_bad1:  db "NO NEO16 MAPPER",0
s_bad2:  db "PUZZLE MANIA NEEDS A CARTRIDGE",0
s_bad3:  db "WITH THE NEO16 MAPPER (16 KB",0
s_bad4:  db "BANKS).",0
s_bad5:  db "OPENMSX: -ROMTYPE NEO-16",0
