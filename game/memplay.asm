; ------------------------------------------------------------------------------------------------ the memory game and the choice screen (overlay bank MEMB, assembled by mem.asm)
; The code bank (memory.asm) calls one routine per frame through the stubs of stub.inc (ovl_mm_init / ovl_mm_frame / ovl_mg_init / ovl_mg_frame), mvsync (the music) in between,
; and draws the cursor with setcursor (v_cx, v_cy, v_cw, v_ch).  5 x 4 cards of 40 x 40 pixels (5 x 5 characters) with a gap of one character: card (cx, cy) has its top left
; character at column 1 + 6 cx, row 1 + 6 cy; row 0 is the header.  The cards are in MEMDATA (tools/memory_cards.py): 13 per variant (12 photos, the back), 400 bytes each:
; 5 rows of 40 pattern bytes, 5 rows of 40 colour bytes.  The state is in the RAM of the puzzle permutation (C100h..C13Fh).
MEMDATA equ 0x4600
CARD    equ 400
MEMICON equ MEMDATA + 26 * CARD         ; the big cards of the choice screen (2080 bytes each: MSX1, MSX2)
ICONSZ  equ 2080

        MACRO CELLADDR row, col
        dw (row) * 256 + (col) * 8
        ENDM
ctab:   REPT 20, k                     ; the pattern address of the top left character of every card place
        CELLADDR 1 + (k / 5) * 6, 1 + (k % 5) * 6
        ENDR

; ---- the VRAM
vset:   ld a,l                          ; HL = address (write)
        out (0x99),a
        ld a,h
        or 0x40
        out (0x99),a
        ret

csrc:   ld l,d                          ; D = card image 0..12 -> HL = its bytes (the variant of the machine)
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl                       ; 16 d
        ld c,l
        ld b,h
        add hl,hl
        add hl,hl
        add hl,hl                       ; 128 d
        add hl,bc                       ; 144 d
        ld b,d
        ld c,0
        add hl,bc                       ; 400 d
        ld bc,MEMDATA
        IF MSX2PAL
        ld a,(v_msx)
        or a
        jr z,.b
        ld bc,MEMDATA + 13 * CARD
.b:
        ENDIF
        add hl,bc
        ret

dcard:  push de                         ; E = place, D = image
        call csrc
        pop de
        ld a,e
        add a,a
        ld e,a
        ld d,0
        push hl
        ld hl,ctab
        add hl,de
        ld c,(hl)
        inc hl
        ld b,(hl)
        pop hl
dcard_at:                               ; BC = pattern address of the top left character, HL = the card
        ld a,10
.row:   push af
        ld a,c
        out (0x99),a
        ld a,b
        or 0x40
        out (0x99),a
        push bc
        ld c,0x98
        ld b,40
.o:     outi
        jp nz,.o
        pop bc
        inc b                           ; the next character row
        pop af
        dec a
        cp 5
        jr nz,.nx
        ld a,b                          ; the colour table (2000h) for the other five rows
        add a,0x20 - 5
        ld b,a
        ld a,5
.nx:    or a
        jr nz,.row
        ret

qcard:  push de                         ; E = place, D = image: the card is drawn by the job engine of the player (the code bank: mem_jobs), the music goes on
        call csrc
        pop de
        push hl                         ; the source
        ld a,e
        add a,a
        ld e,a
        ld d,0
        ld hl,ctab
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)                       ; the destination
        ld a,(m_jn)
        add a,a
        add a,a
        ld c,a
        ld b,0
        ld hl,m_jq
        add hl,bc
        ld (hl),e
        inc hl
        ld (hl),d
        inc hl
        pop de
        ld (hl),e
        inc hl
        ld (hl),d
        ld hl,m_jn
        inc (hl)
        ret

mbold:  ld a,e                          ; HL = string, D = row, E = column: the bold letters of the game (boldtext in core.asm): the upper four pixel rows grey, the lower four white
        add a,a
        add a,a
        add a,a
        ld e,a
.next:  ld a,(hl)
        or a
        ret z
        inc hl
        push hl
        ld l,a
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        ld bc,(v_font)
        add hl,bc
        ld a,e
        out (0x99),a
        ld a,d
        or 0x40
        out (0x99),a
        ld b,8
.p:     ld a,(hl)
        ld c,a
        srl a
        or c
        out (0x98),a
        inc hl
        djnz .p
        ld a,e
        out (0x99),a
        ld a,d
        add a,0x20
        or 0x40
        out (0x99),a
        ld a,0xE1
        ld b,4
.c1:    out (0x98),a
        nop
        djnz .c1
        ld a,0xF1
        ld b,4
.c2:    out (0x98),a
        nop
        djnz .c2
        ld a,e
        add a,8
        ld e,a
        pop hl
        jr .next

dbig:   ld a,20                         ; BC = pattern address of the top left character, HL = the card of the choice screen (13 x 10 characters)
.row:   push af
        ld a,c
        out (0x99),a
        ld a,b
        or 0x40
        out (0x99),a
        push bc
        ld c,0x98
        ld b,104
.o:     outi
        jp nz,.o
        pop bc
        inc b
        pop af
        dec a
        cp 10
        jr nz,.nx
        ld a,b
        add a,0x20 - 10
        ld b,a
        ld a,10
.nx:    or a
        jr nz,.row
        ret

mnum:   ld hl,nbuf                      ; A = 0..255 -> "  7", " 17", "117" in nbuf
        ld b,0
        ld c,100
        call mdig
        ld c,10
        call mdig
        add a,'0'
        ld (hl),a
        inc hl
        ld (hl),0
        ret
mdig:   ld d,0
.s:     sub c
        jr c,.d
        inc d
        jr .s
.d:     add a,c
        ld e,a
        ld a,d
        or b
        jr nz,.p
        ld a,' '
        jr .w
.p:     ld a,d
        add a,'0'
        ld b,1
.w:     ld (hl),a
        inc hl
        ld a,e
        ret

; ---- random numbers (xorshift of 16 bits, v_rng is advanced by the menus: it starts from the time the player took)
rnd:    ld hl,(v_rng)
        ld a,r
        xor l
        ld l,a
        or h
        jr nz,.s
        inc l
.s:     ld a,h
        rra
        ld a,l
        rra
        xor h
        ld h,a
        ld a,l
        rra
        ld a,h
        rra
        xor l
        ld l,a
        xor h
        ld h,a
        ld (v_rng),hl
        ret
pick:   call rnd                        ; C = n, D = mask -> A = 0..n-1
        ld a,l
        and d
        cp c
        jr nc,pick
        ret

; ---- the keys of this frame: bit 0 SPACE / RETURN / fire, 1 ESC, 4 left, 5 up, 6 down, 7 right (only the keys that went down, and the cursor keys that are held: repeat)
mkeys:  ld a,(k8)
        cpl
        ld b,a
        ld a,(k7)
        cpl
        ld c,a
        and 0x80
        jr z,.nr
        set 0,b
.nr:    ld a,c
        and 4
        jr z,.ne
        set 1,b
.ne:    ld a,b
        and 0xF3
        ld b,a
        ld a,(m_prev)
        cpl
        and b
        ld c,a                          ; new
        ld a,b
        ld (m_prev),a
        and 0xF0
        jr z,.nrep
        ld a,c
        and 0xF0
        jr nz,.first
        ld a,(m_rep)                    ; a cursor key is held
        inc a
        cp 15
        jr c,.sv
        ld a,b
        and 0xF0
        or c
        ld c,a
        ld a,11
        jr .sv
.first: xor a
.sv:    ld (m_rep),a
        ld a,c
        ret
.nrep:  xor a
        ld (m_rep),a
        ld a,c
        ret

cursor: ld a,(m_cx)                     ; the rectangle of the sprite cursor around the card: x = 8 + 48 cx, y = 8 + 48 cy
        ld e,a
        add a,a
        add a,e
        add a,a
        add a,a
        add a,a
        add a,a
        add a,8
        ld (v_cx),a
        ld a,(m_cy)
        ld e,a
        add a,a
        add a,e
        add a,a
        add a,a
        add a,a
        add a,a
        add a,8
        ld (v_cy),a
        ld a,40
        ld (v_cw),a
        ld (v_ch),a
        ret

; ================================================================================================ the memory game
mg_init:xor a                           ; the cursor flashes as everywhere in the game (v_ccol = 0)
        ld (v_ccol),a
        ld hl,m_pic                     ; the 12 photos, shuffled: the first ten are the pairs
        xor a
.f:     ld (hl),a
        inc hl
        inc a
        cp 12
        jr nz,.f
        ld b,40
.s1:    push bc
        ld c,12
        ld d,15
        call pick
        ld e,a
        call pick
        call swap                       ; (swap changes BC: the counter is on the stack)
        pop bc
        djnz .s1
        ld hl,m_pic
        ld de,m_pic + 10
        ld bc,10
        ldir
        ld b,100                        ; all twenty places
.s2:    push bc
        ld c,20
        ld d,31
        call pick
        ld e,a
        call pick
        call swap
        pop bc
        djnz .s2
        ld hl,m_st
        ld b,20
        xor a
.z:     ld (hl),a
        inc hl
        djnz .z
        ld a,255
        ld (m_f1),a
        ld (m_f2),a
        xor a
        ld (m_cx),a
        ld (m_cy),a
        ld (m_wait),a
        ld (m_pairs),a
        ld (m_win),a
        ld (m_fr),a
        ld hl,0
        ld (m_moves),hl
        ld (p_secs),hl
        call mkeys                      ; (a key that is down now does not count)
        ld e,0
.d:     push de
        ld d,12
        call dcard
        pop de
        inc e
        ld a,e
        cp 20
        jr nz,.d
        ld hl,s_memory
        ld d,0
        ld e,1
        call mbold
        ld hl,s_pairs
        ld d,0
        ld e,9
        call mbold
        ld hl,s_of
        ld d,0
        ld e,18
        call mbold
        ld hl,s_mv
        ld d,0
        ld e,23
        call mbold
        call header
        jp cursor

swap:   ld hl,m_pic                     ; A, E = two places: swap their photos
        ld d,0
        ld c,a
        ld b,0
        add hl,bc
        push hl
        ld hl,m_pic
        add hl,de
        ld a,(hl)
        pop de
        ex de,hl
        ld c,(hl)
        ld (hl),a
        ex de,hl
        ld (hl),c
        ret

header: ld a,(m_pairs)                  ; the number of pairs and of moves
        call mnum
        ld hl,nbuf + 1
        ld d,0
        ld e,15
        call mbold
        ld a,(m_moves)
        call mnum
        ld hl,nbuf
        ld d,0
        ld e,29
        jp mbold

mg_frame:
        ld a,(m_wait)
        or a
        jr z,.in
        dec a
        ld (m_wait),a
        jr z,.over
        xor a
        ret
.over:  ld a,(m_win)
        or a
        jr z,.back
        ld a,1                          ; all the pairs: the caller goes on to the solved screen
        ret
.back:  ld a,(m_f1)                     ; a wrong pair: both cards turn back
        call turnback
        ld a,(m_f2)
        call turnback
        ld a,255
        ld (m_f1),a
        ld (m_f2),a
        xor a
        ret
.in:    ld a,(m_att)
        or a
        jr z,.real
        call bot                        ; the attract mode: a bot presses the keys (255 = a real key: stop)
        cp 255
        jr nz,.kk
        ld a,2
        ret
.real:  call mkeys
.kk:    ld b,a
        bit 1,b
        jr z,.ne
        ld a,2                          ; ESC
        ret
.ne:    ld a,(m_cx)
        bit 4,b
        jr z,.nl
        or a
        jr nz,.l1
        ld a,5
.l1:    dec a
.nl:    bit 7,b
        jr z,.nr
        inc a
        cp 5
        jr nz,.nr
        xor a
.nr:    ld (m_cx),a
        ld a,(m_cy)
        bit 5,b
        jr z,.nu
        or a
        jr nz,.u1
        ld a,4
.u1:    dec a
.nu:    bit 6,b
        jr z,.nd
        inc a
        cp 4
        jr nz,.nd
        xor a
.nd:    ld (m_cy),a
        call cursor
        bit 0,b
        jr nz,.fire
        xor a
        ret
.fire:  ld a,(m_cy)                     ; the place: 5 cy + cx
        ld e,a
        add a,a
        add a,a
        add a,e
        ld e,a
        ld a,(m_cx)
        add a,e
        ld (m_cur),a
        ld e,a
        ld d,0
        ld hl,m_st
        add hl,de
        ld a,(hl)
        and 0x7F                        ; (bit 7: the card has been seen)
        or a
        jr z,.turn
        xor a                           ; (a card that is turned already)
        ret
.turn:  ld (hl),0x81                     ; face up, seen
        ld hl,m_pic
        add hl,de
        ld d,(hl)                       ; D = the photo, E = the place
        call qcard
        ld a,(m_f1)
        cp 255
        jr nz,.second
        ld a,(m_cur)
        ld (m_f1),a
        xor a
        ret
.second:ld a,(m_cur)
        ld (m_f2),a
        ld hl,(m_moves)
        inc hl
        ld (m_moves),hl
        ld a,(m_f1)                     ; the same photo?
        ld e,a
        ld d,0
        ld hl,m_pic
        add hl,de
        ld b,(hl)
        ld a,(m_f2)
        ld e,a
        ld hl,m_pic
        add hl,de
        ld a,(hl)
        cp b
        jr nz,.wrong
        ld (m_last),a                   ; a pair: it stays
        ld a,(m_f1)
        call setfound
        ld a,(m_f2)
        call setfound
        ld a,255
        ld (m_f1),a
        ld (m_f2),a
        ld a,(m_pairs)
        inc a
        ld (m_pairs),a
        call header
        ld a,(m_pairs)
        cp 10
        jr nz,.more
        ld a,(v_hz)                     ; the last pair stays for a second
        ld (m_wait),a
        ld a,1
        ld (m_win),a
.more:  xor a
        ret
.wrong: call header
        ld a,(v_hz)                     ; they stay for a second
        ld (m_wait),a
        xor a
        ret

setfound:                               ; A = place: the pair is found
        ld e,a
        ld d,0
        ld hl,m_st
        add hl,de
        ld (hl),2
        ret

turnback:                               ; A = place: face down again
        ld e,a
        ld d,0
        ld hl,m_st
        add hl,de
        ld (hl),0x80                    ; face down again, but it has been seen
        ld d,12
        jp qcard

partner:ld c,a                          ; B = a photo, A = a place to leave out -> NC and A = the other place with that photo that is face down and has been seen, or carry
        ld e,0
.l:     ld a,e
        cp c
        jr z,.n
        ld d,0
        ld hl,m_st
        add hl,de
        ld a,(hl)
        cp 0x80
        jr nz,.n
        ld hl,m_pic
        add hl,de
        ld a,(hl)
        cp b
        jr nz,.n
        ld a,e
        or a
        ret
.n:     inc e
        ld a,e
        cp 20
        jr nz,.l
        scf
        ret

; ---- the attract mode: a bot plays the memory game (it moves the cursor and presses SPACE like a player and remembers what it has seen: a second card only when it has seen its partner)
bot:    ld a,(k8)                       ; a key of a real player stops it
        cpl
        and 0xF1
        ld b,a
        ld a,(k7)
        cpl
        and 0x84
        or b
        jr z,.nokey
        ld a,255
        ret
.nokey: ld a,(m_dl)
        or a
        jr z,.act
        dec a
        ld (m_dl),a
        xor a
        ret
.act:   ld a,(m_ph)
        and 1
        jr nz,.move
        ld a,(m_ph)                     ; 0: the first card, 2: the second card
        or a
        jr nz,.second
.first: ld e,0                          ; a pair that has been seen (two cards face down, turned before, the same photo): turn one of them
.fp:    ld d,0
        ld hl,m_st
        add hl,de
        ld a,(hl)
        cp 0x80                         ; face down and seen
        jr nz,.fpn
        ld hl,m_pic
        add hl,de
        ld b,(hl)
        ld a,e
        push de
        call partner
        pop de
        jr c,.fpn
        ld a,e
        ld (m_tgt),a
        jr .chosen
.fpn:   inc e
        ld a,e
        cp 20
        jr nz,.fp
.unseen:ld c,20                         ; else a card that nobody has seen
        ld d,31
        call pick
        ld e,a
        ld d,0
        ld hl,m_st
        add hl,de
        ld a,(hl)
        or a
        jr nz,.unseen
        ld a,e
        ld (m_tgt),a
        jr .chosen
.second:ld a,(m_f1)                     ; has the partner of the first card been seen? then that one, else a card that nobody has seen
        ld e,a
        ld d,0
        ld hl,m_pic
        add hl,de
        ld b,(hl)
        ld a,e
        call partner
        jr c,.unseen
        ld (m_tgt),a
.chosen:ld hl,m_ph
        inc (hl)                        ; 1 / 3: move to it
.move:  ld a,(m_tgt)                    ; the target: column = tgt mod 5 (C), row = tgt / 5 (B)
        ld b,0
.dv:    cp 5
        jr c,.dd
        sub 5
        inc b
        jr .dv
.dd:    ld c,a
        ld a,(m_cx)
        cp c
        ld a,0x80                       ; right
        jr c,.k
        ld a,(m_cx)
        cp c
        ld a,0x10                       ; left
        jr nz,.k
        ld a,(m_cy)
        cp b
        ld a,0x40                       ; down
        jr c,.k
        ld a,(m_cy)
        cp b
        ld a,0x20                       ; up
        jr nz,.k
        ld a,(m_ph)                     ; there: SPACE, then the next card
        inc a
        and 3
        ld (m_ph),a
        ld a,8                          ; (a moment before the next card: 8 calls of the bot = 64 frames)
        ld (m_dl),a
        ld a,1
        ret
.k:     ld b,a
        ld a,2                          ; the next step (2 calls of the bot = 16 frames)
        ld (m_dl),a
        ld a,b
        ret

; ================================================================================================ the choice: sliding puzzle or memory
mm_init:xor a                           ; the thumbnail and the card of the memory game on the choice screen (the logo and the texts are drawn by the code bank: memory.asm)
        ld (v_ccol),a
        ld (m_sel),a
        ld a,(m_ic)                     ; the thumbnail of photo (m_ic): MSX2 = coded for the choice palette (bank CHTH0 + photo), else the one of the photo bank (bank 10 photo + 1, at 3000h)
        ld e,a
        ld d,0
        IF MSX2PAL
        ld a,(v_msx)
        or a
        jr z,.t1
        ld hl,CHTH0
        add hl,de
        ld a,l
        ld (0x7000),a
        ld a,h
        BANKHI 0x7001
        ld hl,0x8000
        jr .td
.t1:
        ENDIF
        ld l,e
        ld h,0
        add hl,hl
        ld d,h
        ld e,l
        add hl,hl
        add hl,hl
        add hl,de                       ; 10 photo
        inc hl
        ld a,l
        ld (0x7000),a
        ld a,h
        BANKHI 0x7001
        ld hl,0xB000
.td:    ld bc,8 * 256 + 3 * 8
        call dbig
        ld hl,MEMICON
        IF MSX2PAL
        ld a,(v_msx)
        or a
        jr z,.b
        ld hl,MEMICON + ICONSZ
.b:
        ENDIF
        ld bc,8 * 256 + 16 * 8
        call dbig
        call mkeys
        jp mm_cursor

mm_cursor:
        ld a,(m_sel)
        or a
        ld a,24
        jr z,.x
        ld a,128
.x:     ld (v_cx),a
        ld a,64
        ld (v_cy),a
        ld a,104
        ld (v_cw),a
        ld a,80
        ld (v_ch),a
        ret

mm_frame:
        call mkeys
        ld b,a
        bit 1,b
        jr z,.ne
        ld a,3                          ; ESC: the credits
        ret
.ne:    ld a,b
        and 0x90                        ; left or right
        jr z,.nm
        ld a,(m_sel)
        xor 1
        ld (m_sel),a
        call mm_cursor
.nm:    bit 0,b
        jr z,.no
        ld a,(m_sel)
        inc a                           ; 1 = sliding puzzle, 2 = memory
        ret
.no:    xor a
        ret

s_memory: db "MEMORY",0
s_pairs: db "PAIRS",0
s_of:   db "/10",0
s_mv:   db "MOVES",0
