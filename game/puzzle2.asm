; numtext: tile number box, HL = string (1 or 2 digits), D = row, E = column of the tile's top left cell.
; The black box is 2 cells high and 2 (one digit) or 3 (two digits) cells wide, 2 px right and 2 px down from the corner: the two top pixel
; rows stay photo, a 2 px white strip on the left continues the tile border, the digits are centred in the black part.  Only whole cell
; rows are touched below the first two pixel rows, so there is no colour clash with the photo.
numtext:
        ld a,e
        add a,a
        add a,a
        add a,a
        ld e,a
        push de
        ld a,(hl)
        ld (n_d1),a
        inc hl
        ld a,(hl)
        ld (n_d2),a
        ld a,(n_d1)
        call fptr
        ld (g_fp),hl
        ld a,(n_d2)
        or a
        ld b,2
        jr z,.nd
        call fptr
        ld (g_fp2),hl
        ld b,3
.nd:    ld a,b
        ld (n_nc),a
        ld hl,nbuf                      ; clear, then the white strip on cell 0 for pixel rows 2..15
        ld b,48
        xor a
.cl:    ld (hl),a
        inc hl
        djnz .cl
        ld hl,nbuf+2
        ld b,14
        ld a,0xC0
.st:    ld (hl),a
        inc hl
        djnz .st
        xor a
        ld (g_r),a
.gl:    ld a,(g_r)                      ; glyph row i goes to pixel row 5 + i
        ld c,a
        ld b,0
        ld hl,nbuf+5
        add hl,bc
        push hl
        ld hl,(g_fp)
        ld a,(hl)
        inc hl
        ld (g_fp),hl
        pop hl
        ld b,a                          ; B = glyph row of digit 1
        ld a,(n_nc)
        cp 3
        jr z,.two
        ld a,b                          ; one digit: starts at pixel 6
        rlca
        rlca
        and 3
        or (hl)
        ld (hl),a
        ld de,16
        add hl,de
        ld a,b
        add a,a
        add a,a
        or (hl)
        ld (hl),a
        jr .nx
.two:   push hl                         ; two digits: start at pixels 7 and 13
        ld hl,(g_fp2)
        ld c,(hl)
        inc hl
        ld (g_fp2),hl
        pop hl
        ld a,b
        rlca
        and 1
        or (hl)
        ld (hl),a
        ld de,16
        add hl,de
        ld a,b
        add a,a
        ld b,a
        ld a,c
        rlca
        rlca
        rlca
        and 7
        or b
        or (hl)
        ld (hl),a
        add hl,de
        ld a,c
        add a,a
        add a,a
        add a,a
        or (hl)
        ld (hl),a
.nx:    ld a,(g_r)
        inc a
        ld (g_r),a
        cp 7
        jr nz,.gl
        pop de
        ld hl,nbuf
        ld a,(n_nc)
        ld (g_r),a
.out:   push hl
        push de
        ld bc,2
        add hl,bc
        ld a,e
        add a,2
        out (0x99),a
        ld a,d
        or 0x40
        out (0x99),a
        ld b,6
.o1:    ld a,(hl)
        out (0x98),a
        inc hl
        nop
        djnz .o1
        ld a,e
        add a,2
        out (0x99),a
        ld a,d
        add a,0x20
        or 0x40
        out (0x99),a
        ld a,0xF1
        ld b,6
.o2:    out (0x98),a
        nop
        djnz .o2
        inc d
        ld a,e
        out (0x99),a
        ld a,d
        or 0x40
        out (0x99),a
        ld b,8
.o3:    ld a,(hl)
        out (0x98),a
        inc hl
        nop
        djnz .o3
        ld a,e
        out (0x99),a
        ld a,d
        add a,0x20
        or 0x40
        out (0x99),a
        ld a,0xF1
        ld b,8
.o4:    out (0x98),a
        nop
        djnz .o4
        pop de
        pop hl
        ld bc,16
        add hl,bc
        ld a,e
        add a,8
        ld e,a
        ld a,(g_r)
        dec a
        ld (g_r),a
        jr nz,.out
        ret

drawall:
        call job_flush
        xor a
        ld (g_y),a
.row:   xor a
        ld (g_x),a
.col:   ld a,(g_x)
        ld b,a
        ld a,(g_y)
        ld c,a
        call drawpos
        ld a,(g_x)
        inc a
        ld (g_x),a
        ld hl,v_size
        cp (hl)
        jr nz,.col
        ld a,(g_y)
        inc a
        ld (g_y),a
        ld hl,v_size
        cp (hl)
        jr nz,.row
        ret

showfull:                               ; the whole plain photo (a job: the music goes on)
        ld a,(v_photo)
        ld c,a
        add a,a
        add a,a
        add a,c
        add a,a
        inc a
        ld l,a
        ld h,0
        push de
        ld de,(v_pb)
        add hl,de
        pop de
        jp job_pic

puzlined:                               ; select the puzzle image bank: size, line style (thick, thin, off = plain photo)
        ld a,(v_lines)
        cp 2
        ld b,0
        jr z,.go
        add a,a
        add a,a
        ld b,a
        ld a,(v_size)
        sub 3
        add a,2
        add a,b
        ld b,a
.go:    ld a,(v_photo)
        call setpb
        ld (p_bank),hl                  ; (setpb leaves the bank number in HL)
        ret

tick:                                   ; one frame of the timer
        ld a,(p_fr)
        inc a
        ld hl,v_hz
        cp (hl)
        jr c,.s
        xor a
        ld hl,(p_secs)
        inc hl
        ld (p_secs),hl
.s:     ld (p_fr),a
        ret

; move the blank in direction A; if it works, redraw the two tiles and count the move.  Carry = no move.
do_move:
        call domove
        ret c
        ld a,(p_hint)
        or a
        jr z,.nh
        xor a
        ld (p_hint),a
        call hidecursor
.nh:
        ld a,(p_nshow)                  ; numbers on the tiles: draw at once
        or a
        jr nz,.dir
        ld a,(p_shadow)
        or a
        jr z,.dir
        ld a,(mus_on)
        or a
        jr z,.dir
        call job_room                   ; the job engine of the player draws the two tiles while the music goes on
        call job_move
        jr .cnt
.dir:   call puzlined
        ld a,(m_ox)
        ld b,a
        ld a,(m_oy)
        ld c,a
        call drawpos
        ld a,(p_bx)
        ld b,a
        ld a,(p_by)
        ld c,a
        call drawpos
.cnt:   ld hl,(p_moves)
        inc hl
        ld (p_moves),hl
        or a
        ret

; hint: the tile that belongs on the square where the blank is now (if the blank is home: the first tile that is out of place)
hint_start:
        ld a,(p_by)
        ld b,a
        ld a,(v_size)
        ld c,a
        call mulbc
        ld a,(p_bx)
        add a,l
        ld (v_t2),a
        ld a,(p_n2)
        dec a
        ld hl,v_t2
        cp (hl)
        jr z,.fb
        ld hl,perm
        ld a,(v_t2)
        ld b,a
        ld c,0
        ld a,(p_n2)
        ld d,a
.f1:    ld a,(hl)
        cp b
        jr z,.got
        inc hl
        inc c
        dec d
        jr nz,.f1
        ret
.fb:    ld hl,perm
        ld c,0
        ld a,(p_n2)
        ld d,a
.f2:    ld a,(hl)
        cp c
        jr nz,.got
        inc hl
        inc c
        dec d
        jr nz,.f2
        ret
.got:   ld a,c                          ; position index -> x = j mod N, y = j / N
        ld b,0
        ld hl,v_size
        ld e,(hl)
.dv:    cp e
        jr c,.dd
        sub e
        inc b
        jr .dv
.dd:    ld (v_tmp2),a
        ld a,b
        ld (v_tmp2+1),a
        ld a,(v_tmp2)
        ld b,a
        ld a,(p_tw)
        ld c,a
        call mulbc
        ld a,(p_ox)
        add a,l
        add a,a
        add a,a
        add a,a
        ld (h_x),a
        ld a,(v_tmp2+1)
        ld b,a
        ld a,(p_th)
        ld c,a
        call mulbc
        ld a,(p_oy)
        add a,l
        add a,a
        add a,a
        add a,a
        ld (h_y),a
        ld a,(p_tw)
        add a,a
        add a,a
        add a,a
        ld (h_w),a
        ld a,(p_th)
        add a,a
        add a,a
        add a,a
        ld (h_h),a
        ld a,80
        ld (p_hint),a
        ret

cursor_rect:                            ; sprite rectangle of the puzzle cursor (control 1)
        ld a,(v_pcx)
        ld b,a
        ld a,(p_tw)
        ld c,a
        call mulbc
        ld a,(p_ox)
        add a,l
        add a,a
        add a,a
        add a,a
        ld (v_cx),a
        ld a,(v_pcy)
        ld b,a
        ld a,(p_th)
        ld c,a
        call mulbc
        ld a,(p_oy)
        add a,l
        add a,a
        add a,a
        add a,a
        ld (v_cy),a
        ld a,(p_tw)
        add a,a
        add a,a
        add a,a
        ld (v_cw),a
        ld a,(p_th)
        add a,a
        add a,a
        add a,a
        ld (v_ch),a
        ret

hint_update:                            ; sprites: the hint while it lasts, else the cursor of control 1
        ld a,(p_hint)
        or a
        jr z,.nohint
        dec a
        ld (p_hint),a
        jr nz,.show
        jp hidecursor
.show:  ld a,(h_x)
        ld (v_cx),a
        ld a,(h_y)
        ld (v_cy),a
        ld a,(h_w)
        ld (v_cw),a
        ld a,(h_h)
        ld (v_ch),a
        ld a,(v_frame)
        and 8
        ld a,3
        jr z,.c
        ld a,12
.c:     ld (v_ccol),a
        jp setcursor
.nohint: ld a,(v_ctl)
        or a
        ret z
        call cursor_rect
        xor a
        ld (v_ccol),a
        jp setcursor

slide_cursor:                           ; A = blank direction that moves the tile under the cursor, 0FFh = not next to the blank
        ld a,(v_pcx)
        ld hl,p_bx
        sub (hl)
        ld b,a
        ld a,(v_pcy)
        ld hl,p_by
        sub (hl)
        ld c,a
        ld a,b
        or a
        jr nz,.hx
        ld a,c
        cp 0xFF
        ld a,0
        ret z
        ld a,c
        cp 1
        ld a,2
        ret z
        ld a,0xFF
        ret
.hx:    ld a,c
        or a
        jr z,.hy
        ld a,0xFF
        ret
.hy:    ld a,b
        cp 1
        ld a,1
        ret z
        ld a,b
        cp 0xFF
        ld a,3
        ret z
        ld a,0xFF
        ret

; ------------------------------------------------------------------------------------------------ the game
puzzle: call hidecursor
        call job_reset
        xor a
        ld (p_shadow),a
        call puz_init
        call build_jt
        ld hl,(v_rng)                   ; seed from the time spent in the menus
        ld a,r
        xor l
        ld l,a
        or h
        jr nz,.sd
        inc l
.sd:    ld (v_rng),hl
        call puzlined
        ld a,1
        ld c,1
        call music_play                 ; the player runs (silent) while its sample loop builds the screen: the music starts when the puzzle is on the screen
        ld a,4
        ld (mus_gt),a
        call job_black
        ld a,(v_photo)                  ; MSX2: the palette of the photo
        add a,PAL_PHOTO0
        call need_pal
.sh:    call shuffle
        call solved                     ; never start from a solved puzzle
        jr z,.sh
        call job_drawall
        ld a,1                          ; (the picture bank is known: jobs allowed)
        ld (p_shadow),a
        xor a
        ld (p_hshow),a
        ld (p_nshow),a
        ld (v_pdir),a
        ld (p_hint),a
        ld (v_pf),a
        ld hl,0
        ld (p_moves),hl
        ld a,(p_bx)
        ld (v_pcx),a
        ld a,(p_by)
        ld (v_pcy),a
        call job_flush                  ; the puzzle is on the screen: now the music (from its start)
        call music_stop
        ld a,1
        ld c,1
        call music_play
        call wait_release
        call keyedge
        call hint_update                ; (the loop only runs when something happens: the sprite cursor has to be there at the start)
        xor a                           ; the time starts now, when the puzzle can be played (not while the picture is built up)
        ld (p_fr),a
        ld hl,0
        ld (p_secs),hl
.l:     call mvsync
        call selchk
        ld a,(att_on)
        or a
        jr z,.nat
        call att_step                   ; 0 = go on, 1 = a key was pressed, 2 = solved
        or a
        jr z,.l
        dec a
        jr z,.esc
        or a                            ; NC = solved
        ret
.nat:   ld a,(mus_busy)                 ; nothing to do (no key change, no cursor flash, no hint): counters and timer run in the slots
        or a
        jr z,.l
        ld a,(mus_on)                   ; fast path: only an arrow key (press, auto repeat, release) with the arrow control, no other key, no hint, no N / H held:
        or a                            ; the keys ESC, N, H, L, C, T and the hint need no look, the frame goes straight to the move (half of the work of a key frame)
        jr z,.full
        ld hl,mus_pr
        ld a,(hl)
        ld hl,p_hint
        or (hl)
        ld hl,p_nshow
        or (hl)
        ld hl,p_hshow
        or (hl)
        ld hl,v_ctl
        or (hl)
        jp z,.k0
.full:  call getesc
        jr nz,.noesc
.esc:   call job_flush
        call hidecursor
        call music_fadeout
        call wait_release
        scf
        ret
.noesc: call getn
        jr nz,.nup
        ld a,(p_nshow)                  ; N held: numbers on the tiles, moves and time in the blank
        or a
        jp nz,.l
        inc a
        ld (p_nshow),a
        ld a,1                          ; only the number boxes on top of the tiles
        ld (d_only),a
        call drawall
        xor a
        ld (d_only),a
        jp .l
.nup:   ld a,(p_nshow)
        or a
        jr z,.hchk
        xor a
        ld (p_nshow),a
        call hidenums
        jp .l
.hchk:  call geth
        jr nz,.hup
        ld a,(p_hshow)                  ; H held: show the solution
        or a
        jp nz,.l
        inc a
        ld (p_hshow),a
        call showfull
        jp .l
.hup:   ld a,(p_hshow)
        or a
        jr z,.keys
        xor a
        ld (p_hshow),a
        ld a,(mus_on)
        ld b,a
        ld a,(p_shadow)
        and b
        jr z,.hdir
        call job_pmargins               ; the photo covered the margins: black again ...
        call job_drawall                ; ... and the tiles come back while the music goes on
        call keyedge
        jp .l
.hdir:  call puzlined
        call clrscr
        call drawall
        jp .l
.keys:  call keyedge                    ; L = tile lines, C = control, T = hint
        ld (v_t2),a
        bit 0,a
        jr z,.nl
        ld a,(v_lines)
        inc a
        cp 3
        jr c,.sl
        xor a
.sl:    ld (v_lines),a
        ld a,(mus_on)
        or a
        jr z,.ldir
        call job_flush
        call puzlined                   ; the new picture (bank p_bank) builds up while the music goes on
        call job_drawall
        call keyedge                    ; (the keys were scanned meanwhile: L, C, T edges must not be missed)
        jr .nl
.ldir:  call puzlined
        call clrscr
        call drawall
        ld a,1
        ld (p_shadow),a
.nl:    ld a,(v_t2)
        bit 1,a
        jr z,.nc
        ld a,(v_ctl)
        xor 1
        ld (v_ctl),a
        call hidecursor
.nc:    ld a,(v_t2)
        bit 2,a
        jr z,.nt
        call hint_start
.nt:    call hint_update
        ld a,(v_ctl)
        or a
        jr nz,.mode1
.k0:    call getkey                     ; control 0: the arrow key slides the tile next to the blank
        or a
        jp z,.l
        cp 1                            ; key direction -> blank direction (opposite of the tile slide)
        ld b,2
        jr z,.go
        cp 3
        ld b,3
        jr z,.go
        cp 5
        ld b,0
        jr z,.go
        ld b,1
.go:    ld a,b
        call do_move
        jp c,.l
        jp .moved
.mode1: call getkey                     ; control 1: the cursor sprites go to a tile, SPACE slides it
        or a
        jr z,.m1f
        cp 7
        jr z,.m1l
        cp 3
        jr z,.m1r
        cp 1
        jr z,.m1u
        ld a,(v_pcy)                    ; down
        inc a
        ld hl,v_size
        cp (hl)
        jr nc,.m1f
        ld (v_pcy),a
        jr .m1f
.m1u:   ld a,(v_pcy)
        or a
        jr z,.m1f
        dec a
        ld (v_pcy),a
        jr .m1f
.m1l:   ld a,(v_pcx)
        or a
        jr z,.m1f
        dec a
        ld (v_pcx),a
        jr .m1f
.m1r:   ld a,(v_pcx)
        inc a
        ld hl,v_size
        cp (hl)
        jr nc,.m1f
        ld (v_pcx),a
.m1f:   call getfire                    ; SPACE (edge)
        ld b,0
        jr z,.nf
        inc b
.nf:    ld a,(v_pf)
        ld c,a
        ld a,b
        ld (v_pf),a
        or a
        jp z,.l
        ld a,c
        or a
        jp nz,.l
        call slide_cursor
        cp 0xFF
        jp z,.l
        call do_move
        jp c,.l
.moved: call solved
        jp nz,.l
        or a                            ; NC = solved
        ret

; ------------------------------------------------------------------------------------------------ solved: jingle, flourish, the video
win:
        call showfull
        call job_flush                  ; the banner goes on the bottom row of the picture
        call win_banner
        call music_stop                 ; the jingle: the FONY jingle of the disk version as a sample, a plain loop on a quiet screen (sndplay.asm): over the SCC if there is one, else the PSG
        call wait_release               ; (the last move may have been SPACE)
        ld c,1                          ; (SPACE skips it, but not in the first second)
        call ovl_snd
        jr c,.end
.jd:    call music_stop
        call conf_init                  ; then the confetti and the flashing, without sound: the length of the old jingle (46 rows of 5 / 6 frames)
        xor a
        ld (v_frame),a
        ld hl,0
        ld (v_tmp2),hl
        ld a,(v_hz)
        cp 50
        ld hl,230
        jr z,.he
        ld hl,276
.he:    ld (v_tmp3),hl
.l:     call jwait
        call conf_step
        ld hl,v_frame
        inc (hl)
        ld hl,(v_tmp2)
        inc hl
        ld (v_tmp2),hl
        ld a,h
        or a
        jr nz,.chk
        ld a,l
        cp 80
        jr c,.fl
        jr nz,.chk
        call flash_off
        call conf_park
        jr .chk
.fl:    call flash_on
.chk:   ld hl,(v_tmp2)
        ld de,(v_tmp3)
        or a
        sbc hl,de
        jr z,.end
        ld hl,(v_tmp2)
        ld a,h
        or a
        jr nz,.cf
        ld a,l
        cp 60
        jr c,.l
.cf:    call getfire
        jr z,.l
.end:   call flash_off
        call conf_end
        call music_stop
        ld a,PAL_TMS                    ; MSX2: the videos are coded for the TMS9918A palette
        call need_pal
        ld a,(v_photo)
        call play
        jp wait_release

flash_on:                               ; border colour and the four corner sprites flash
        ld a,(v_frame)
        srl a
        and 15
        cp 14
        jr c,.ok
        sub 14
.ok:    add a,2
        out (0x99),a
        ld a,0x87
        out (0x99),a
        ld a,255
        ld (v_cw),a
        ld a,191
        ld (v_ch),a
        xor a
        ld (v_cx),a
        ld (v_cy),a
        ld a,(v_frame)
        and 7
        add a,8
        ld (v_ccol),a
        jp setcursor

flash_off:
        ld a,1
        out (0x99),a
        ld a,0x87
        out (0x99),a
        jp hidecursor

win_banner:                             ; "SOLVED! MOVES n TIME m:ss" on the bottom row
        ld a,32
        ld (b_w),a
        ld a,1
        ld (b_h),a
        ld d,23
        ld e,0
        call blankblk
        ld de,nbuf
        ld hl,s_solved
        call strcpy
        ld hl,(p_moves)
        call dec16
        ld hl,s_wtime
        call strcpy
        call timestr
        ld hl,nbuf
        ld d,23
        ld e,1
        jp boldtext

strcpy:                                 ; HL -> DE, without the terminator; DE ends after the text
        ld a,(hl)
        or a
        ret z
        ld (de),a
        inc hl
        inc de
        jr strcpy

s_moves: db "MOVES",0
s_time:  db "TIME",0
s_solved: db "SOLVED! MOVES ",0
s_wtime: db "  TIME ",0
