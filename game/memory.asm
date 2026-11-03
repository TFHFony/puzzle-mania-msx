; ------------------------------------------------------------------------------------------------ the choice (sliding puzzle / memory) and the memory game: the code bank side
; The choice screen has the layout of the photo menu (menu.asm): the logo, a thumbnail of a photo (the sliding puzzle), the card of the memory game (the memory bank draws both), the
; footer; the menu music plays.  The game itself is in the memory bank (memplay.asm, through the stubs: one routine per frame, mvsync keeps the music going); the solved screen is that
; of the puzzle (win).  The attract mode: when the song is over and nobody pressed a key, the two puzzles take turns (att_k).
mode_loop:                              ; the choice after the title: A = 0 sliding puzzle, 1 memory, 2 the attract mode plays memory
        ld a,(mus_on)                   ; the same as the menu (pm.asm .menu): the music plays already (carries on), or it starts muted while the screen is drawn, then it fades in
        or a
        jr z,.fresh
        ld a,(mus_trk)
        or a
        jr z,.cont
.fresh: xor a
        ld c,1
        call music_play
        ld a,4
        ld (mus_gt),a
        call draw_choice
        call music_stop
        ld c,1
        xor a
        call music_play
        jr .go
.cont:  xor a
        ld c,1
        call music_play
        call draw_choice
.go:    call wait_release
        call att_init
        call mvsync                     ; the cursor is there at once (not only after a key)
        call setcursor
.l:     call mvsync
        call anykey
        jr z,.ni
        ld a,1
        ld (att_act),a
        jr .bz
.ni:    call att_check
        jr c,.att
.bz:    ld a,(mus_busy)                 ; nothing to do: the gap of the music stays short (as in the menu)
        or a
        jr z,.l
        call ovl_mm_frame               ; A = 0 nothing, 1 sliding puzzle, 2 memory, 3 ESC
        push af
        call setcursor
        pop af
        or a
        jr nz,.pick
        call geth                       ; H = how to play
        jr nz,.l
        call hidecursor
        call howto
        jp mode_loop
.att:   call hidecursor                 ; the song is over: the attract mode plays the other puzzle than the last time
        ld a,(att_k)
        xor 1
        ld (att_k),a
        jr nz,.am
        ld a,1                          ; the sliding puzzle: the photo menu starts its attract mode at once
        ld (att_pd),a
        xor a
        ret
.am:    ld a,2                          ; memory
        ret
.pick:  push af
        call hidecursor
        call wait_release
        pop af
        cp 3
        jr z,.esc
        dec a                           ; 0 sliding puzzle (its menu draws itself), 1 memory
        ret
.esc:   call credits
        jp mode_loop

draw_choice:                            ; like draw_menu
        call job_reset
        ld a,CHOICEPAL                  ; MSX2: the palette of the menu with a blue (the card of the memory game); the thumbnail is coded for it (an MSX1 ignores it)
        call need_pal
        call job_logo
        call job_flush
        call menu_footer
        ld hl,s_choose                  ; "CHOOSE YOUR PUZZLE" above the pictures, SLIDING and MEMORY below them (centred under their picture); all of it centred between the logo and the footer
        ld d,6
        ld e,7
        call boldtext
        ld hl,s_slide
        ld d,19
        ld e,6
        call boldtext
        ld hl,s_memory
        ld d,19
        ld e,19
        call boldtext
        ld a,(v_rng)                    ; the thumbnail of a photo, at random
        and 15
        cp NPHOTO
        jr c,.p
        sub NPHOTO
.p:     ld (m_ic),a
        jp ovl_mm_init                  ; the thumbnail and the card of the memory game (the memory bank), the cursor

s_choose: db "CHOOSE YOUR PUZZLE",0
s_slide: db "SLIDING",0
s_memory: db "MEMORY",0

memory_att:                             ; the attract mode plays memory (a bot): carry = a key stopped it
        ld a,1
        ld (m_att),a
        call memory
        push af
        xor a
        ld (m_att),a
        pop af
        ret

memory:                                 ; the memory game; when it is won: the solved screen of the puzzle with the photo of the last pair.  Carry = ESC (or a key in the attract mode)
        call music_fadeout
        call job_reset
        ld a,MEMPAL
        call need_pal
        call clrscr
        call ovl_mg_init
        ld a,1                          ; the puzzle music
        ld c,1
        call music_play
.l:     call mvsync
        ld hl,m_tk
        inc (hl)
        ld a,(hl)
        and 7
        jr nz,.nt
        ld a,(m_att)                    ; the attract mode: the bot only runs every 8th frame (a call of the memory bank costs samples: the music stays as clean as the idle puzzle)
        or a
        jr nz,.go
.nt:    ld a,(mus_busy)                 ; only a frame with something to do (a key, the cursor, a wait) calls the memory bank: the idle gap of the music is only 2 samples
        ld hl,m_wait
        or (hl)
        jr z,.l
.go:    call ovl_mg_frame               ; A = 0 on, 1 won, 2 ESC
        push af
        call setcursor
        call mem_jobs
        pop af
        or a
        jr z,.l
        push af
        call hidecursor
        pop af
        cp 2
        jr z,.out
        ld a,(m_last)                   ; won: the board stays (all the cards are up), the jingle, the confetti over it, then the video of the last pair
        ld (v_photo),a
        call job_flush                  ; (the last card is drawn)
        ld a,(m_att)
        ld (att_on),a                   ; the attract mode: the clip plays once and it goes on
        call win_go
        xor a
        ld (att_on),a
        ret
.out:   call music_stop
        ld a,PAL_TMS
        call need_pal
        scf
        ret

mem_jobs:                               ; the cards that the memory bank wants drawn (m_jq: destination, source; m_jn): jobs of the player's sample loop, the music goes on
        ld a,(m_jn)
        or a
        ret z
        ld b,a
        xor a
        ld (m_jn),a
        ld hl,m_jq
.e:     push bc
        push hl
        call job_room
        pop hl
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld c,(hl)
        inc hl
        ld b,(hl)
        inc hl
        push hl                         ; the next entry
        push bc                         ; the source
        push de                         ; the destination
        ld hl,MEMB
        ld (q_bank),hl
        ld hl,0
        ld (q_adj),hl
        pop de
        pop hl
        ld a,d
        or 0x40
        ld d,a
        push de
        push hl
        ld b,40                         ; the patterns: 5 rows of 40 bytes
        ld c,5
        call jq_put
        pop hl
        ld bc,200
        add hl,bc                       ; the colours: 200 bytes further, 2000h further in the VRAM
        pop de
        ld a,d
        add a,0x20
        ld d,a
        ld b,40
        ld c,5
        call jq_put
        pop hl
        pop bc
        djnz .e
        ret
