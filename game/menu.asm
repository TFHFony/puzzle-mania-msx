; ------------------------------------------------------------------------------------------------ main menu
; carousel: 9 photos in 5 columns of 2; two columns (4 photos, 104x80 px each) are visible, v_win = first visible column (0..3)
draw_menu:
        call job_reset                  ; (jobs of the screen before are dropped)
        call job_mmargins               ; the music goes on: everything is drawn by the sample loop of the player
        call job_flush
        call menu_footer
        jp draw_page

menu_footer:                            ; bottom line: (C) FONY purple, (.)(.) bright yellow, [H]ELP white; all bold
        ld hl,s_copy
        ld d,23
        ld e,0
        ld a,0xD1
        call boldcol
        ld hl,s_eyes
        ld d,23
        ld e,13
        ld a,0xA1
        call boldcol
        ld hl,s_help
        ld d,23
        ld e,26
        ld a,0xF1
        jp boldcol

draw_page:                             ; the four thumbnails and the arrows (jobs)
        xor a
        ld (v_i),a                      ; 0..3 = window column * 2 + row
.t:     call job_room
        ld a,(v_win)
        ld b,a
        ld a,(v_i)
        srl a
        add a,b
        add a,a
        ld b,a
        ld a,(v_i)
        and 1
        add a,b                         ; photo
        ld (v_tmp),a
        ld a,(v_i)
        and 1
        ld d,2
        jr z,.r
        ld d,12
.r:     ld a,(v_i)
        and 2
        ld e,24
        jr z,.c
        ld e,128
.c:     ld a,(v_tmp)
        cp 9
        jr nc,.bl
        ld c,a                          ; bank of the photo = 1 + 10 * photo
        add a,a
        add a,a
        add a,c
        add a,a
        inc a
        ld l,a
        ld h,0
        call job_thumb
        jr .nx
.bl:    ld b,104
        ld c,10
        call job_rect
.nx:    ld a,(v_i)
        inc a
        ld (v_i),a
        cp 4
        jr nz,.t
        call job_room
        ld a,(v_win)
        or a
        ld de,0x0A00
        jr z,.nl
        ld hl,arrow_l
        call job_arrow
        jr .rr
.nl:    ld b,16
        ld c,4
        call job_rect
.rr:    call job_room
        ld a,(v_win)
        cp 3
        ld de,0x0AF0
        jr z,.nr
        ld hl,arrow_r
        jp job_arrow
.nr:    ld b,16
        ld c,4
        jp job_rect

menu_cursor:
        ld a,(v_sel)
        srl a
        ld hl,v_win
        sub (hl)
        ld a,24
        jr z,.c
        ld a,128
.c:     ld (v_cx),a
        ld a,(v_sel)
        and 1
        ld a,16
        jr z,.r
        ld a,96
.r:     ld (v_cy),a
        ld a,104
        ld (v_cw),a
        ld a,80
        ld (v_ch),a
        jp setcursor

menu_loop:                              ; NC = photo chosen (v_photo), C = ESC
        call wait_release
        call menu_cursor                ; (the loop only runs when something happens: the cursor has to be there at the start)
.l:     call mvsync
        ld a,(mus_busy)                 ; nothing to do: the counters run in the slots of the player, the gap stays short
        or a
        jr z,.l
        call menu_cursor
        call getesc
        jr nz,.noesc
        call hidecursor
        scf
        ret
.noesc: call geth                       ; H = how to play
        jr nz,.nh
        call hidecursor
        call howto
        call draw_menu
        jr .l
.nh:    call getfire
        jp nz,.pick
        call getkey
        or a
        jr z,.l
        cp 7
        jr z,.left
        cp 3
        jr z,.right
        cp 1
        jr z,.up
.down:  ld a,(v_sel)
        and 1
        jp nz,.l
        ld a,(v_sel)
        inc a
        cp 9
        jp nc,.l
        ld (v_sel),a
        jp .l
.up:    ld a,(v_sel)
        and 1
        jp z,.l
        ld hl,v_sel
        dec (hl)
        jp .l
.right: ld a,(v_sel)
        srl a
        ld b,a
        ld a,(v_win)
        cp b
        jr z,.rr1                       ; left column: move to the right column
        cp 3
        jp nc,.l
        inc a                           ; right column: scroll one column
        ld (v_win),a
        ld a,(v_sel)
        add a,2
        cp 9
        jr c,.s1
        ld a,8
.s1:    ld (v_sel),a
        call draw_page
        jp .l
.rr1:   ld a,(v_sel)
        add a,2
        cp 9
        jr c,.s2
        ld a,8
.s2:    ld (v_sel),a
        jp .l
.left:  ld a,(v_sel)
        srl a
        ld b,a
        ld a,(v_win)
        cp b
        jr nz,.ll1
        or a
        jp z,.l
        dec a
        ld (v_win),a
        ld a,(v_sel)
        sub 2
        ld (v_sel),a
        call draw_page
        jp .l
.ll1:   ld a,(v_sel)
        sub 2
        ld (v_sel),a
        jp .l
.pick:  ld a,(v_sel)
        ld (v_photo),a
        call hidecursor
        or a
        ret

; ------------------------------------------------------------------------------------------------ size menu (3x3 .. 6x6), tile lines, control
draw_size:
        call job_reset
        call job_black                  ; the music goes on: the screen is drawn by the sample loop of the player
        call job_flush
        ld hl,s_size
        ld d,0
        ld e,10
        call boldtext
        ld hl,s_hint3
        ld d,23
        ld e,4
        call boldtext
        call draw_sizestat
        ld a,(v_photo)                  ; the size buttons: bank 2 + 10 * photo
        ld c,a
        add a,a
        add a,a
        add a,c
        add a,a
        add a,2
        ld l,a
        ld h,0
        ld (q_bank),hl
        ld hl,0
        ld (q_adj),hl
        ld hl,0x4000
        ld (v_src),hl
        xor a
        ld (v_i),a
.s:     call job_room
        ld a,(v_i)
        srl a
        ld d,1
        jr z,.r0
        ld d,11                         ; second row of buttons: label on row 20, the option lines below
.r0:    ld a,(v_i)
        and 1
        ld e,24
        jr z,.c0
        ld e,136
.c0:    ld (v_dd),de
        ld hl,(v_src)
        ld a,d
        or 0x40
        ld d,a
        push de
        ld b,96
        ld c,9
        call jq_put
        pop de
        ld a,d
        add a,0x20
        ld d,a
        ld hl,(v_src)
        ld bc,864
        add hl,bc
        ld b,96
        ld c,9
        call jq_put
        ld a,(v_i)                      ; label "nXn" under the button
        add a,'3'
        ld (lbl),a
        ld (lbl+2),a
        ld a,'X'
        ld (lbl+1),a
        xor a
        ld (lbl+3),a
        ld de,(v_dd)
        ld a,d
        add a,9
        ld d,a
        ld a,e
        srl a
        srl a
        srl a
        add a,4
        ld e,a
        ld hl,lbl
        call boldtext
        ld hl,(v_src)
        ld bc,1728
        add hl,bc
        ld (v_src),hl
        ld a,(v_i)
        inc a
        ld (v_i),a
        cp 4
        jr nz,.s
        ret

draw_sizestat:                          ; the two option lines: L = tile lines, C = how a tile is moved
        ld hl,s_lines
        ld d,22
        ld e,1
        call boldtext
        ld hl,s_ctl
        ld d,22
        ld e,17
        call boldtext
        ld a,(v_lines)
        add a,a
        add a,a
        add a,a
        ld l,a
        ld h,0
        ld de,s_lnn
        add hl,de
        ld d,22
        ld e,9
        call boldtext
        ld a,(v_ctl)
        add a,a
        add a,a
        add a,a
        ld l,a
        ld h,0
        ld de,s_ctn
        add hl,de
        ld d,22
        ld e,24
        jp boldtext

size_cursor:
        ld a,(v_ssel)                   ; cursor
        srl a
        ld a,8
        jr z,.y
        ld a,88
.y:     ld (v_cy),a
        ld a,(v_ssel)
        and 1
        ld a,24
        jr z,.x
        ld a,136
.x:     ld (v_cx),a
        ld a,96
        ld (v_cw),a
        ld a,72
        ld (v_ch),a
        call setcursor
        ret

size_loop:
        xor a
        ld (v_ssel),a
        call wait_release
        call keyedge
        call size_cursor
.l:     call mvsync
        ld a,(mus_busy)
        or a
        jr z,.l
        call size_cursor
        call getesc
        jr nz,.noesc
        call hidecursor
        call wait_release
        scf
        ret
.noesc: call keyedge
        ld (v_t2),a
        bit 0,a
        jr z,.nol
        ld a,(v_lines)
        inc a
        cp 3
        jr c,.sl
        xor a
.sl:    ld (v_lines),a
        call draw_sizestat
.nol:   ld a,(v_t2)
        bit 1,a
        jr z,.noc
        ld a,(v_ctl)
        xor 1
        ld (v_ctl),a
        call draw_sizestat
.noc:   call getfire
        jr nz,.pick
        call getkey
        or a
        jp z,.l
        ld hl,v_ssel
        cp 7
        jr z,.left
        cp 3
        jr z,.right
        cp 1
        jr z,.up
.down:  ld a,(hl)
        cp 2
        jp nc,.l
        add a,2
        jr .s
.up:    ld a,(hl)
        cp 2
        jp c,.l
        sub 2
        jr .s
.left:  ld a,(hl)
        and 1
        jp z,.l
        ld a,(hl)
        dec a
        jr .s
.right: ld a,(hl)
        and 1
        jp nz,.l
        ld a,(hl)
        inc a
.s:     ld (hl),a
        jp .l
.pick:  ld a,(v_ssel)
        add a,3
        push af
        call hidecursor
        pop af
        or a                            ; NC
        ret

s_size:  db "CHOOSE SIZE",0
s_hint3: db "SPACE: START   ESC: BACK",0
s_lines: db "L LINES:",0
s_ctl:   db "C MOVE:",0
s_lnn:   db "THICK  ",0
         db "THIN   ",0
         db "OFF    ",0
s_ctn:   db "ARROWS ",0
         db "CURSOR ",0
s_copy: db 1," 2026 FONY",0
s_eyes: db "(.)(.)",0
s_help: db "[H]ELP",0
