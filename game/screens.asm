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
        ret z
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
welcome:                                ; FONY logo for 3 s (SPACE skips), then the PUZZLE MANIA title until SPACE
        ld hl,FONY
        call wipe_in
        ld a,(v_hz)                     ; 3 seconds
        ld e,a
        ld d,0
        ld hl,0
        ld b,3
.mul:   add hl,de
        djnz .mul
        ld (v_tmp2),hl
.f:     call vsync
        call getfire
        jr nz,.go
        ld hl,(v_tmp2)
        dec hl
        ld (v_tmp2),hl
        ld a,h
        or l
        jr nz,.f
.go:    call wait_release
        call wipe_clear
        ld hl,WELCOME
        call wipe_in
        IF TITLEVIDEO
        call tvplay                     ; video and music in one stream until SPACE / fire (tvplay.inc)
        jp wait_release
        ELSE
        xor a
        ld c,1
        call music_play
.w:     call mvsync
        ld hl,(v_rng)
        inc hl
        ld (v_rng),hl
        call getfire
        jr z,.w
        jp wait_release
        ENDIF

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
