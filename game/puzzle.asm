; ------------------------------------------------------------------------------------------------ puzzle
puz_init:                               ; geometry of the field, tiles in the solved order, blank bottom right
        ld a,(v_size)
        sub 3
        add a,a
        add a,a
        ld e,a
        ld d,0
        ld hl,ptab
        add hl,de
        ld a,(hl)
        ld (p_tw),a
        inc hl
        ld a,(hl)
        ld (p_th),a
        inc hl
        ld a,(hl)
        ld (p_ox),a
        inc hl
        ld a,(hl)
        ld (p_oy),a
        ld a,(v_size)
        ld b,a
        ld c,a
        call mulbc
        ld a,l
        ld (p_n2),a
        ld b,a
        ld hl,perm
        xor a
.id:    ld (hl),a
        inc hl
        inc a
        djnz .id
        ld a,(v_size)
        dec a
        ld (p_bx),a
        ld (p_by),a
        ret

; move the blank in direction A (0 up, 1 right, 2 down, 3 left); carry = not possible
domove: ld c,a
        ld a,(p_bx)
        ld d,a
        ld a,(p_by)
        ld e,a
        ld a,(v_size)
        ld b,a
        ld a,c
        or a
        jr z,.up
        dec a
        jr z,.right
        dec a
        jr z,.down
.left:  ld a,d
        or a
        jr z,.bad
        dec d
        jr .ok
.up:    ld a,e
        or a
        jr z,.bad
        dec e
        jr .ok
.right: ld a,d
        inc a
        cp b
        jr nc,.bad
        ld d,a
        jr .ok
.down:  ld a,e
        inc a
        cp b
        jr nc,.bad
        ld e,a
.ok:    ld a,(p_bx)
        ld (m_ox),a
        ld a,(p_by)
        ld (m_oy),a
        ld a,d
        ld (p_bx),a
        ld a,e
        ld (p_by),a
        ld a,(m_ox)
        ld (d_x),a
        ld a,(m_oy)
        ld (d_y),a
        call posidx
        ld (m_i0),a
        ld a,(p_bx)
        ld (d_x),a
        ld a,(p_by)
        ld (d_y),a
        call posidx
        ld (m_i1),a
        ld a,(m_i0)
        ld e,a
        ld d,0
        ld hl,perm
        add hl,de
        push hl
        ld a,(m_i1)
        ld e,a
        ld hl,perm
        add hl,de
        pop de
        ld a,(de)
        ld b,(hl)
        ld (hl),a
        ld a,b
        ld (de),a
        or a
        ret
.bad:   scf
        ret

posidx: ld a,(d_y)                      ; A = d_y * N + d_x
        ld b,a
        ld a,(v_size)
        ld c,a
        call mulbc
        ld a,(d_x)
        add a,l
        ret

shuffle:                                ; random walk of the blank from the solved position: always solvable
        ld a,(p_n2)
        ld c,a
        ld b,0
        ld hl,0
        ld d,12
.m:     add hl,bc
        dec d
        jr nz,.m
        ld (p_cnt),hl
        ld a,0xFF
        ld (p_last),a
.l:     call rnd
        and 3
        ld b,a
        ld a,(p_last)
        xor 2                           ; not the opposite of the last move
        cp b
        jr z,.l
        ld a,b
        push af
        call domove
        pop bc
        jr c,.l
        ld a,b
        ld (p_last),a
        ld hl,(p_cnt)
        dec hl
        ld (p_cnt),hl
        ld a,h
        or l
        jr nz,.l
        ret

solved: ld a,(p_n2)                     ; Z = solved
        ld b,a
        ld hl,perm
        ld c,0
.l:     ld a,(hl)
        cp c
        jr nz,.no
        inc hl
        inc c
        djnz .l
        xor a
        ret
.no:    or 1
        ret

; draw the tile at position B = x, C = y
drawpos:
        ld a,b
        ld (d_x),a
        ld a,c
        ld (d_y),a
        ld b,c
        ld a,(p_th)
        ld c,a
        call mulbc
        ld a,(p_oy)
        add a,l
        ld (d_dy),a
        ld a,(d_x)
        ld b,a
        ld a,(p_tw)
        ld c,a
        call mulbc
        ld a,(p_ox)
        add a,l
        add a,a
        add a,a
        add a,a
        ld (d_dx8),a
        call posidx
        ld e,a
        ld d,0
        ld hl,perm
        add hl,de
        ld a,(hl)
        ld (d_t),a
        ld a,(p_tw)
        ld (b_w),a
        ld a,(p_th)
        ld (b_h),a
        ld a,(p_n2)
        dec a
        ld b,a
        ld a,(d_t)
        cp b
        jr nz,.img
        ld a,(d_dy)                     ; the blank: black, with the moves and the time while N is held
        ld d,a
        ld a,(d_dx8)
        ld e,a
        call blankblk
        ld a,(p_nshow)
        or a
        ret z
        jp draw_stats
.img:   ld a,(d_only)                   ; only the number box (N pressed): the tile is on the screen already
        or a
        jr nz,.nsh
        ld b,0                          ; source tile: sy = t / N, sx = t mod N
        ld a,(v_size)
        ld c,a
        ld a,(d_t)
.dv:    cp c
        jr c,.dd
        sub c
        inc b
        jr .dv
.dd:    ld (d_sx),a
        ld a,b
        ld (d_sy),a
        ld a,(p_th)
        ld c,a
        call mulbc                      ; B = sy still
        ld a,(p_oy)
        add a,l
        add a,0x80
        ld (d_sh),a
        ld a,(d_sx)
        ld b,a
        ld a,(p_tw)
        ld c,a
        call mulbc
        ld a,(p_ox)
        add a,l
        add a,a
        add a,a
        add a,a
        ld (d_sl),a
        ld hl,256
        ld (b_ss8),hl
        ld hl,0x1800
        ld (b_cofs),hl
        ld a,(d_sh)
        ld h,a
        ld a,(d_sl)
        ld l,a
        ld a,(d_dy)
        ld d,a
        ld a,(d_dx8)
        ld e,a
        call blit
.nsh:   ld a,(p_nshow)                  ; N held: the tile number (position when solved + 1)
        or a
        ret z
        ld a,(d_t)
        inc a
        ld l,a
        ld h,0
        ld de,lbl
        call dec16
        ld a,(d_dx8)
        srl a
        srl a
        srl a
        ld e,a
        ld a,(d_dy)
        ld d,a
        ld hl,lbl
        jp numtext

; moves and time in the blank tile (N held): 4 lines of up to 5 characters, so it fits in every size
draw_stats:
        ld a,(d_dx8)                    ; first column of the blank tile
        srl a
        srl a
        srl a
        ld (v_t2),a
        ld a,(p_th)                     ; the 4 lines are centred in the tile: first row = tile row + (height - 4) / 2
        sub 4
        jr nc,.h
        xor a
.h:     srl a
        ld hl,d_dy
        add a,(hl)
        ld (hl),a
        ld a,(d_dy)
        ld d,a
        ld hl,s_moves
        ld a,0xE1
        call statline
        ld hl,(p_moves)
        ld de,lbl
        call dec16
        ld a,(d_dy)
        inc a
        ld d,a
        ld hl,lbl
        ld a,0xF1
        call statline
        ld a,(d_dy)
        add a,2
        ld d,a
        ld hl,s_time
        ld a,0xE1
        call statline
        ld de,lbl
        call timestr
        ld a,(d_dy)
        add a,3
        ld d,a
        ld hl,lbl
        ld a,0xF1
        jp statline

; statline: HL = string, D = row, A = colour byte: bold text, centred in the blank tile (first column v_t2, width p_tw); a leftover of a
; half character is a shift of 4 pixels (SCREEN 2 has no character grid for the pixels)
statline:
        push af
        push hl
        ld b,0
.l:     ld a,(hl)
        or a
        jr z,.e
        inc hl
        inc b
        jr .l
.e:     ld a,(p_tw)
        sub b
        jr nc,.p
        xor a
.p:     ld c,a
        srl a
        ld hl,v_t2
        add a,(hl)
        ld e,a
        pop hl
        pop af
        bit 0,c
        jp z,boldcol
        jp boldcol4

; boldcol4: like boldcol, but the text is shifted 4 pixels to the right (one cell more is drawn for the right half of the last character)
boldcol4:
        ld (t_col),a
        ld a,d
        ld (b4_r),a
        ld a,e
        add a,a
        add a,a
        add a,a
        ld e,a
        push hl
        pop ix                          ; IX = the string
        ld iy,blank0                    ; the character on the left of the first one: nothing
.cell:  xor a
        ld (b4_f),a
        ld a,(ix+0)
        or a
        jr nz,.g
        inc a
        ld (b4_f),a                     ; after the last character: the cell with its right half
        ld hl,blank0
        jr .h
.g:     inc ix
        ld l,a
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        ld bc,(v_font)
        add hl,bc
.h:     ld (b4_cur),hl
        ld a,e
        out (0x99),a
        ld a,(b4_r)
        or 0x40
        out (0x99),a
        ld b,8
.p:     ld a,(iy+0)                     ; right half of the previous character (bold) -> left half of the cell
        ld c,a
        srl a
        or c
        and 0x0F
        rlca
        rlca
        rlca
        rlca
        ld c,a
        ld a,(hl)                       ; left half of this character (bold) -> right half of the cell
        ld d,a
        srl a
        or d
        rrca
        rrca
        rrca
        rrca
        and 0x0F
        or c
        out (0x98),a
        inc hl
        inc iy
        djnz .p
        ld a,e
        out (0x99),a
        ld a,(b4_r)
        add a,0x20
        or 0x40
        out (0x99),a
        ld a,(t_col)
        ld b,8
.c:     out (0x98),a
        nop
        djnz .c
        ld iy,(b4_cur)
        ld a,e
        add a,8
        ld e,a
        ld a,(b4_f)
        or a
        jr z,.cell
        ret

timestr:                                ; "m:ss" of p_secs at (DE), 0 terminated
        push de
        ld hl,(p_secs)
        ld de,0                         ; minutes
.mn:    ld bc,60
        or a
        sbc hl,bc
        jr c,.md
        inc de
        jr .mn
.md:    add hl,bc                       ; HL = seconds
        ld a,l
        ld (v_tmp2),a
        ex de,hl                        ; HL = minutes
        ld a,h
        or a
        jr nz,.cap
        ld a,l
        cp 100
        jr c,.ok
.cap:   ld hl,99
.ok:    pop de
        call dec16
        ld a,':'
        ld (de),a
        inc de
        ld a,(v_tmp2)
        ld b,'0'
.s10:   cp 10
        jr c,.sd
        sub 10
        inc b
        jr .s10
.sd:    ld c,a
        ld a,b
        ld (de),a
        inc de
        ld a,c
        add a,'0'
        ld (de),a
        inc de
        xor a
        ld (de),a
        ret

