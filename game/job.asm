; ------------------------------------------------------------------------------------------------ VDP job queue (screen work while the music plays)
; The sample loop of the player (player.asm) copies queued rows to the VRAM, 4 bytes per sample, so that drawing does not stop the music.
; An entry (16 bytes): source (word), VRAM address | 4000h (word), bytes per row, rows, source step at the end of a row (word), ROM bank of the source
; (word: page 1 shows it while the loop runs; 0 = the code bank), 6 unused.  A tile is two entries (pattern rows, colour rows).

job_reset:
        xor a
        ld (j_qn),a
        ld (j_go),a
        ld (j_bank),a
        ld (j_bank+1),a
        ld a,0x40
        ld (j_dend),a
        ld a,0x98
        ld (j_lc),a
        ld hl,JQ
        ld (j_qp),hl
        ld (j_qa),hl
        exx
        ld hl,0
        ld de,0x4040                    ; = the last row of an empty phase (j_dend)
        ld b,0
        ld c,0x98
        exx
        xor a
        ex af,af'
        ret

job_room:                               ; the music goes on: one frame (announced to the player: the queue work after it gets the action pause), until the ring has room
.w:     ld a,2
        ld (mus_hint),a
        call mvsync
        ld a,(j_qn)
        cp 13
        jr nc,.w
        ret

job_idle:                               ; Z = the engine has nothing left to do
        ld a,(j_qn)
        or a
        ret nz
        exx
        ld a,b
        exx
        ld c,a                          ; C = bytes left of the run
        exx
        ld a,d
        exx
        ld b,a                          ; B = VRAM row of the engine
        ld a,c
        or a
        ret nz
        ld a,(j_dend)
        cp b
        ret nz
        ex af,af'
        ld c,a
        ex af,af'
        ld a,c
        or a
        ret

job_flush:                              ; wait until everything queued is on the screen
.w:     call job_idle
        ret z
        ld a,(mus_on)
        or a
        jr z,.x
        ld a,2                          ; (the engine work of a PAL frame needs the action pause)
        ld (mus_hint),a
        call mvsync
        jr .w
.x:     jp job_reset                    ; no music, no engine: forget the queue


; ---- queue entries
        MACRO ENTRY adjhi, bankvar, bankhi
        ld (hl),c
        inc l
        ld (hl),b
        inc l
        ld (hl),e
        inc l
        ld (hl),d
        inc l
        ld a,(j_ln)
        ld (hl),a
        inc l
        ld a,(p_th)
        ld (hl),a
        inc l
        ld a,(j_nl)
        ld (hl),a
        inc l
        ld (hl),adjhi
        inc l
        ld a,(bankvar)
        ld (hl),a
        inc l
        ld a,(bankhi)                   ; (the banks of the MSX2 photos are above 255)
        ld (hl),a
        ld a,l
        add a,7
        ld l,a
        ENDM

        MACRO ENTRYC lenv, rowsv, adjlo, adjhi
        ld (hl),c
        inc l
        ld (hl),b
        inc l
        ld (hl),e
        inc l
        ld (hl),d
        inc l
        ld (hl),lenv
        inc l
        ld (hl),rowsv
        inc l
        ld (hl),adjlo
        inc l
        ld (hl),adjhi
        inc l
        xor a
        ld (hl),a
        inc l
        ld (hl),a
        ld a,l
        add a,7
        ld l,a
        ENDM

; jq_put: HL = source, DE = VRAM address | 4000h, B = bytes per row, C = rows; q_adj (source step at the end of a row) and q_bank (ROM bank) set by the caller
jq_put: push ix
        ld ix,(j_qa)
        ld (ix+0),l
        ld (ix+1),h
        ld (ix+2),e
        ld (ix+3),d
        ld (ix+4),b
        ld (ix+5),c
        ld hl,(q_adj)
        ld (ix+6),l
        ld (ix+7),h
        ld hl,(q_bank)
        ld (ix+8),l
        ld (ix+9),h
        ld a,(j_qa)
        add a,16
        ld (j_qa),a
        ld hl,j_qn
        inc (hl)
        pop ix
        ret

job_put_tile:                           ; A = tile, B = position (cell): the picture of the tile on that cell (pattern rows, colour rows), from the ROM bank p_bank
        ld c,a
        ld a,b
        add a,a
        ld e,a
        ld d,0
        ld hl,JT
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        set 6,d                         ; DE = the cell on the screen | 4000h
        push de
        ld a,c
        add a,a
        ld e,a
        ld d,0
        ld hl,JT
        add hl,de
        ld c,(hl)
        inc hl
        ld b,(hl)
        ld hl,0x4000                    ; the bank is shown in page 1 while the loop runs
        add hl,bc
        ld b,h
        ld c,l
        pop de
        ld hl,(j_qa)
        ENTRY 0,p_bank,p_bank+1
        ld a,b
        add a,0x18
        ld b,a
        ld a,d
        add a,0x20
        ld d,a
        ENTRY 0,p_bank,p_bank+1
        ld (j_qa),hl
        ld a,(j_qn)
        add a,2
        ld (j_qn),a
        ret

job_put_blank:                          ; A = position (cell): black (from the code bank)
        add a,a
        ld e,a
        ld d,0
        ld hl,JT
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        set 6,d
        ld hl,(j_qa)
        ld bc,blank0
        ENTRY 0xFF,j_zero,j_zero
        ld bc,blank1
        ld a,d
        add a,0x20
        ld d,a
        ENTRY 0xFF,j_zero,j_zero
        ld (j_qa),hl
        ld a,(j_qn)
        add a,2
        ld (j_qn),a
        ret

job_move:                               ; the tile that has moved (perm[m_i0]) goes to cell m_i0, the blank to cell m_i1
        ld a,(m_i0)
        ld e,a
        ld d,0
        ld hl,perm
        add hl,de
        ld a,(hl)
        ld b,e
        call job_put_tile
        ld a,(m_i1)
        jp job_put_blank

job_black:                              ; the whole screen black: 4 entries of 24 rows of 128 bytes
        call job_room
        ld hl,(j_qa)
        ld de,0x4000
        ld bc,blank0
        ENTRYC 128,24,0x80,0xFF
        ld de,0x4080
        ENTRYC 128,24,0x80,0xFF
        ld de,0x6000
        ld bc,blank1
        ENTRYC 128,24,0x80,0xFF
        ld de,0x6080
        ENTRYC 128,24,0x80,0xFF
        ld (j_qa),hl
        ld a,(j_qn)
        add a,4
        ld (j_qn),a
        ret

job_drawall:                            ; all tiles, queued as the ring has room: the picture builds up while the music goes on
        xor a
        ld (g_i),a
.l:     call job_room
        ld a,(g_i)
        ld e,a
        ld d,0
        ld hl,perm
        add hl,de
        ld c,(hl)
        ld a,(p_n2)
        dec a
        cp c
        ld a,e
        jr z,.bl
        ld b,a
        ld a,c
        call job_put_tile
        jr .n
.bl:    call job_put_blank
.n:     ld a,(g_i)
        inc a
        ld (g_i),a
        ld hl,p_n2
        cp (hl)
        jr nz,.l
        ret

; N released: the number boxes (3 cells, two rows) at the top left of a tile come back from the picture (ROM, page 2); the blank is black again
hidenums:
        call job_flush
        call puzlined                   ; the picture bank in the window
        xor a
        ld (g_i),a
.pos:   ld a,(g_i)
        ld e,a
        ld d,0
        ld hl,perm
        add hl,de
        ld b,(hl)
        ld a,(p_n2)
        dec a
        cp b
        jr z,.blank
        ld a,b
        add a,a
        ld e,a
        ld hl,JT
        add hl,de
        ld c,(hl)
        inc hl
        ld b,(hl)
        ld hl,0x8000
        add hl,bc
        push hl
        ld a,(g_i)
        add a,a
        ld e,a
        ld hl,JT
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        pop hl
        push hl
        push de
        call .row                       ; the number box is two character rows high
        pop de
        pop hl
        inc h
        inc d
        call .row
        jr .next
.blank: ld a,(g_i)
        add a,a
        ld e,a
        ld d,0
        ld hl,JT
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        ld a,(p_tw)
        ld (b_w),a
        ld a,(p_th)
        ld (b_h),a
        call blankblk
.next:  ld a,(g_i)
        inc a
        ld (g_i),a
        ld hl,p_n2
        cp (hl)
        jp nz,.pos
        ret
.row:   ld a,e                          ; 3 characters (24 bytes) of pattern and of colour: HL = source, DE = VRAM
        out (0x99),a
        ld a,d
        or 0x40
        out (0x99),a
        ld b,24
        ld c,0x98
.p:     outi
        jp nz,.p
        ld bc,0x1800-24
        add hl,bc
        ld a,e
        out (0x99),a
        ld a,d
        add a,0x20
        or 0x40
        out (0x99),a
        ld b,24
        ld c,0x98
.c:     outi
        jp nz,.c
        ret

; offsets of the cells of the puzzle: (row * 256 + column * 8) of the first character of the tile, one word per cell (JT)
build_jt:
        ld hl,JT
        ld a,(p_oy)
        ld d,a
        ld a,(v_size)
        ld b,a
.ty:    push bc
        ld a,(p_ox)
        ld e,a
        ld a,(v_size)
        ld b,a
.tx:    ld a,e
        add a,a
        add a,a
        add a,a
        ld (hl),a
        inc hl
        ld (hl),d
        inc hl
        ld a,(p_tw)
        add a,e
        ld e,a
        djnz .tx
        ld a,(p_th)
        add a,d
        ld d,a
        pop bc
        djnz .ty
        ld a,(p_tw)
        add a,a
        add a,a
        add a,a
        ld (j_ln),a
        neg
        ld (j_nl),a
        ret

; ---- screens as jobs (music goes on).  The sources are ROM banks (page 1 shows the bank while the loop copies), the layout is the one of the screen.
job_pic:                                ; HL = ROM bank of a full screen picture (pattern 6 KB, colour 6 KB): 12 entries, from the top to the bottom
        ld (q_bank),hl
        ld hl,0x0080                    ; source step at the end of a row: 256 - 128
        ld (q_adj),hl
        xor a
        ld (g_i),a
.c:     call job_room
        ld a,(g_i)
        add a,a
        add a,a
        add a,a                         ; first row of the chunk (8 rows)
        or 0x40
        ld d,a
        ld h,a                          ; pattern: the source (page 1: 4000h + row * 256) and the VRAM address have the same high byte
        call .put
        ld a,d
        add a,0x18                      ; colour: 1800h further in the bank ...
        ld h,a
        ld a,d
        add a,0x20                      ; ... and 2000h further in the VRAM
        ld d,a
        call .put
        ld a,(g_i)
        inc a
        ld (g_i),a
        cp 3
        jr nz,.c
        ret
.put:   ld a,h
        ld (j_t),a
        ld l,0
        ld e,0
        ld b,128
        ld c,8
        call jq_put
        ld a,(j_t)                      ; (jq_put used HL)
        ld h,a
        ld l,0x80
        ld e,0x80
        ld b,128
        ld c,8
        jp jq_put

job_thumb:                              ; HL = ROM bank of a photo (thumbnail at 3000h in it, 13 x 10 characters), D = row, E = column * 8
        ld (q_bank),hl
        ld hl,0                         ; the rows follow each other in the bank
        ld (q_adj),hl
        ld a,d
        or 0x40
        ld d,a
        push de
        ld hl,0x7000
        ld b,104
        ld c,10
        call jq_put
        pop de
        ld a,d
        add a,0x20
        ld d,a
        ld hl,0x7410
        ld b,104
        ld c,10
        jp jq_put

job_arrow:                              ; HL = arrow (2 x 4 characters: pattern 64 bytes, colour 64 bytes) in the code bank, DE = row, column * 8
        xor a
        ld (q_bank),a
        ld (q_bank+1),a
        ld (q_adj),a
        ld (q_adj+1),a
        ld a,d
        or 0x40
        ld d,a
        push hl
        push de
        ld b,16
        ld c,4
        call jq_put
        pop de
        pop hl
        ld bc,64
        add hl,bc
        ld a,d
        add a,0x20
        ld d,a
        ld b,16
        ld c,4
        jp jq_put

job_logo:                               ; PUZZLE MANIA XXXL on the tile rows 0..1 (the 16 pixels above the thumbnails); two halves of 14 tiles from the code bank
        call job_room
        xor a
        ld (q_bank),a
        ld (q_bank+1),a
        ld (q_adj),a
        ld (q_adj+1),a
        ld hl,logo_dat
        ld de,0x4010
        call .h
        call job_room
        ld hl,logo_dat+448
        ld de,0x4080
.h:     push hl
        push de
        ld b,112
        ld c,2
        call jq_put
        pop de
        pop hl
        ld bc,224
        add hl,bc
        ld a,d
        add a,0x20
        ld d,a
        ld b,112
        ld c,2
        jp jq_put

job_rect:                               ; black: D = row, E = column * 8, B = bytes per row (up to 128), C = rows
        push bc
        call job_room
        pop bc
        xor a
        ld (q_bank),a
        ld (q_bank+1),a
        ld a,b
        neg
        ld l,a
        ld h,0xFF                       ; the block of black is read again for every row
        ld (q_adj),hl
        ld a,d
        or 0x40
        ld d,a
        push de
        push bc
        ld hl,blank0
        call jq_put
        pop bc
        pop de
        ld a,d
        add a,0x20
        ld d,a
        ld hl,blank1
        jp jq_put

job_mmargins:                           ; the menu: everything around the four thumbnails
        ld b,24
        ld c,24
        ld de,0
        call job_rect
        ld b,24
        ld c,24
        ld de,232
        call job_rect
        ld b,104
        ld c,2
        ld de,24
        call job_rect
        ld b,104
        ld c,2
        ld de,128
        call job_rect
        ld b,104
        ld c,2
        ld de,0x1618
        call job_rect
        ld b,104
        ld c,2
        ld de,0x1680
        jp job_rect

job_pmargins:                           ; the margins of the puzzle field black (after the whole photo has been shown)
        ld a,(p_ox)
        or a
        jr z,.nl
        add a,a
        add a,a
        add a,a
        ld b,a
        ld c,24
        ld de,0
        call job_rect
.nl:    ld a,(v_size)
        ld b,a
        ld a,(p_tw)
        ld c,a
        call mulbc
        ld a,(p_ox)
        add a,l                         ; first column right of the field
        cp 32
        jr nc,.nt
        ld c,a
        ld a,32
        sub c
        add a,a
        add a,a
        add a,a
        ld b,a                          ; width in pixels
        ld a,c
        add a,a
        add a,a
        add a,a
        ld e,a
        ld d,0
        ld c,24
        call job_rect
.nt:    ld a,(p_oy)
        or a
        jr z,.nb
        ld c,a
        ld b,128
        ld de,0
        push bc
        call job_rect
        pop bc
        ld b,128
        ld de,128
        call job_rect
.nb:    ld a,(v_size)
        ld b,a
        ld a,(p_th)
        ld c,a
        call mulbc
        ld a,(p_oy)
        add a,l                         ; first row under the field
        cp 24
        ret nc
        ld d,a
        ld c,a
        ld a,24
        sub c
        ld c,a
        ld b,128
        ld e,0
        push bc
        push de
        call job_rect
        pop de
        pop bc
        ld b,128
        ld e,128
        jp job_rect

        ALIGN 128
blank0: ds 128,0x00                     ; black: pattern and colour rows (the source of the black jobs)
blank1: ds 128,0x11
