; PUZZLE MANIA - MSXdev26 - MSX1 (16 KB RAM, TMS9918A, PSG), NEO16 cartridge.
; Page 1 (4000h) = this code, bank 0, never switched.  Page 2 (8000h) = NEO16 window, registers 7000h/7001h: pictures, music and video.
; ROM banks (tools/build_game.py): 0 code | 1 + 10 p + k: photo p (k = 0 plain image + thumbnail, 1 size buttons, 2..5 thick tile lines 3x3..6x6,
; 6..9 thin tile lines) | WELCOME, HOWTO (3), CREDITS, SELFTEST | jingle, menu music, puzzle music | VIDEO0 ...: video frames, one per bank
        DEVICE NOSLOT64K
        ORG 0x4000
        db "AB"
        dw init
        dw 0,0,0,0,0,0
        db "ROM_NE16"
        ORG 0x4020

        INCLUDE "equ.inc"
        INCLUDE "heads.inc"             ; length of the work slots of the player (tools/tune_slots.py)
        INCLUDE "clk.inc"               ; MDELAY, FI_PAL, FI_NTSC (generated)
        INCLUDE "plrsize.inc"           ; PLR_SIZE (generated)

init:   di
        ld sp,0xF380                    ; the stack below the BIOS work area: the job engine and the RAM copy of the picture use 0C200h..0F2FFh
        ld hl,0xC000                    ; all variables and counters (moves, time, music, job queue) start at 0: the RAM of a real machine holds garbage
        ld de,0xC001
        ld bc,0x02FF
        ld (hl),0
        ldir
        ld hl,att_d                     ; (the list of attract photos lies outside the cleared area)
        ld de,att_d+1
        ld bc,8
        ld (hl),0
        ldir
        call job_reset                  ; the job engine of the player (alternate registers, queue): the power-on state of a real machine is garbage
        xor a
        ld (0x6000),a                   ; page 1 window = bank 0
        BANKHI 0x6001
        call 0x0138                     ; RSLREG: page 2 = our cartridge slot (same as page 1)
        rrca
        rrca
        and 3
        ld c,a                          ; primary slot
        ld b,0
        ld hl,0xFCC1
        add hl,bc
        ld a,(hl)
        and 0x80                        ; EXPTBL: expanded?  Only then SLTTBL means something (it is FFh for an unexpanded slot on some machines, e.g. the OneChipMSX)
        jr z,.ne
        or c
        ld c,a
        inc hl
        inc hl
        inc hl
        inc hl
        ld a,(hl)
        and 0x0C
        or c
        ld c,a
.ne:    ld a,c
        ld (v_own),a                    ; the slot of our cartridge
        ld h,0x80
        call 0x0024                     ; ENASLT
        di
        xor a
        ld (v_sccm),a                   ; (the RAM above 0C300h is not cleared: not the SCC player until the scan says so)
        ld a,FI_PAL                     ; sample clock fractions of the PSG player (the SCC player has its own, see scc_mode_init)
        ld (fi_p),a
        ld a,FI_NTSC
        ld (fi_n),a
        IF SCC
        call scc_scan                   ; an SCC cartridge in another slot?
        call scc_mode_init              ; (then the music goes to the SCC and the player block for the SCC is loaded)
        ENDIF
        call player_load                ; (page 2 is our cartridge now)
        ld hl,(0x0004)                  ; BIOS font
        ld (v_font),hl
        ld a,(0xF3E6)                   ; RG7SAV: the colour of the screen that the MSX started with (the background of SCREEN 0 is the low nibble)
        and 0x0F
        ld (v_bc),a
        ld a,2
        call CHGMOD                     ; SCREEN 2
        di
        ld a,0xC0                       ; 16K, display on, no interrupt, 8x8 sprites
        out (0x99),a
        ld a,0x81
        out (0x99),a
        call start_col                  ; the screen and the border keep the colour of the start (black: backdrop black); start_black wipes it away
        call nametab
        call sprpat
        ld hl,0x1234
        ld (v_rng),hl
        xor a
        ld (v_photo),a
        ld (v_sel),a
        ld (v_pdir),a
        ld (v_win),a
        ld (v_lines),a
        ld a,2                          ; no tile lines at the start (L cycles thick, thin, none)
        ld (v_lines),a
        xor a
        ld (v_ctl),a
        ld (v_ccol),a
        ld (mus_on),a
        ld (p_ek),a
        ld (p_hint),a
        ld (p_shadow),a
        ld (mus_sel),a                  ; (the keys that the slots of the player derive: no SELECT press, no key, no direction, no L / C / T)
        ld (mus_any),a
        ld (mus_dk),a
        ld (mus_dkey),a
        ld (mus_ke),a
        dec a
        ld (k8),a
        ld (k7),a
        ld (k3),a
        ld (k4),a
        ld (k5),a
        ld (sc_last),a
        call msx_init
        call hz_init                    ; 50 Hz (a TMS9918A machine: as it is)
        call selftest
        call start_col                  ; (the VDP test leaves the colour table dirty and the display off: the colour of the start again, then the display on)
        ld a,0xC0
        out (0x99),a
        ld a,0x81
        out (0x99),a
        call spec_check                 ; S held: the specs
        call start_black                ; the screen of the start (the colour of the BIOS, the bytes of the VDP test) goes away: a black wipe before the FONY logo
        IF FONYTEST
.ft:    IF SCC
        ld a,(v_sccm)
        or a
        jr z,.ftn
        call scc_tvstart
.ftn:
        ENDIF
        call ovl_fony                   ; test ROM: the film again and again (tools/tune_fony.py)
        jr .ft
        ENDIF
        IF JNGTEST
.jt:    ld c,0                          ; test ROM: the jingle again and again (tools/tune_snd.py)
        call ovl_snd
        jr .jt
        ENDIF
        IF TIETONLY
.tt:     call welcome                    ; test ROM: the logo and the title video, again and again
        jr .tt
        ENDIF
        IF DIAG
        jp diag
        ENDIF
        call welcome
.mode:  call mode_loop                   ; the choice: sliding puzzle or memory (A = 0 sliding, 1 memory, 2 the attract mode plays memory)
        or a
        jr z,.menu
        cp 2
        jr z,.matt
        call memory
        jp .mode
.matt:  call memory_att                 ; carry = a key stopped it
        jp c,.mode
        call wipe_clear
        call title
        jp .mode
.menu:  xor a
        ld (att_on),a
        ld a,(mus_on)                   ; the menu music plays already (back from the credits, the size menu, the puzzle): the menu is drawn over it
        or a
        jr z,.fresh
        ld a,(mus_trk)
        or a
        jr z,.cont
.fresh: xor a                           ; a new start:
        ld c,1                          ; (the track 0) the player runs silent while the menu is drawn, then the music starts from its beginning
        call music_play
        ld a,4
        ld (mus_gt),a
        call draw_menu
        call music_stop
        ld c,1
        xor a
        call music_play                 ; (fades in)
        jr .mm
.cont:  xor a
        ld c,1
        call music_play                 ; (carries on)
        call draw_menu
.mm:    call menu_loop                  ; NC = photo chosen, C = ESC
        jr nc,.size
        call credits
        jp .menu
.size:  ld a,(att_on)
        or a
        jr z,.ns
        call draw_size                  ; attract mode: the song has been muted since the attract mode started (att_mute), the size menu, the cursor goes to 3x3 or 4x4
        ld a,(att_sz)
        sub 3
        ld (v_ssel),a
        ld b,ATT_SHOW
.sf:    push bc
        call mvsync
        call size_cursor
        call anykey
        pop bc
        jr nz,.sk
        djnz .sf
        call hidecursor
        ld a,(att_sz)
        jr .go
.sk:    call hidecursor
        call wait_release
        call att_unmute                 ; (a key: the song goes on)
        jp .menu
.ns:    call draw_size
        call size_loop                  ; carry = ESC, else A = N
        jp c,.menu
.go:    ld (v_size),a
        call music_fadeout
        call puzzle                     ; carry = ESC (back to the menu), NC = solved
        push af
        xor a
        ld (p_hint),a
        pop af
        jp c,.menu
        call win
        ld a,(att_on)
        or a
        jp z,.menu
        xor a                           ; the attract mode: after the clip the title again (video and photo alternate), then the menu
        ld (att_on),a
        call wipe_clear
        call title
        jp .mode                        ; (the choice: the attract mode alternates between the two puzzles)

        INCLUDE "core.asm"
        INCLUDE "music.asm"
        INCLUDE "screens.asm"
        INCLUDE "menu.asm"
        INCLUDE "puzzle.asm"
        INCLUDE "puzzle2.asm"
        INCLUDE "memory.asm"
        INCLUDE "extra.asm"
        INCLUDE "msx2.asm"
        IF MSX2PAL
        ENDIF
        INCLUDE "spec.asm"
        INCLUDE "scc.asm"
        INCLUDE "job.asm"
        INCLUDE "vplay.asm"
        INCLUDE "diag.asm"
        IF TITLEVIDEO
        INCLUDE "tvplay.inc"
        INCLUDE "tvplay8.inc"            ; the same for a machine with a VDP wait state (v_tvd, wtest.asm)
        IF SCC
        INCLUDE "tvplay16.inc"
        INCLUDE "tvplay16w.inc"
        ENDIF
        ENDIF
player_load:                            ; the player block from its ROM bank into the RAM
        ld hl,PLR_BANK
        ld bc,PLR_SIZE
        IF SCC
        ld a,(v_sccm)
        or a
        jr z,.pl
        ld hl,PLR_BANK_SCC
        ld bc,PLR_SIZE_SCC
.pl:
        ENDIF
        push bc
        call setbank
        pop bc
        ld hl,0x8000
        ld de,PLAYER_RAM
        ldir
        ret
        INCLUDE "gen.inc"               ; bank numbers, tracks, clips, tile geometry, arrows (generated)
        ASSERT $ < 0x7EE0
        ds 0x7EE0-$,0xFF
        jp row                          ; the jump table of the player (fixed addresses, see equ.inc)
        jp fadestep
        jp setbank
        jp vsync
        jp tick
        ds 0x7F00-$,0xFF
        INCLUDE "stub.inc"                 ; the same bytes in the overlay bank
        ds 0x8000-$,0xFF
        SAVEBIN "pm.bin",0x4000,0x4000
