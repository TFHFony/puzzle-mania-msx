; PUZZLE MANIA - MSXdev26 - MSX1 (16 KB RAM, TMS9918A, PSG), NEO16 cartridge.
; Page 1 (4000h) = this code, bank 0, never switched.  Page 2 (8000h) = NEO16 window, registers 7000h/7001h: pictures, music and video.
; ROM banks (tools/build_game.py): 0 code | 1 + 10 p + k: photo p (k = 0 plain image + thumbnail, 1 size buttons, 2..5 thick tile lines 3x3..6x6,
; 6..9 thin tile lines) | WELCOME, FONY, HOWTO (3), CREDITS, SELFTEST | jingle, menu music, puzzle music | VIDEO0 ...: video frames, one per bank
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
        call job_reset                  ; the job engine of the player (alternate registers, queue): the power-on state of a real machine is garbage
        xor a
        ld (0x6000),a                   ; page 1 window = bank 0
        BANKHI 0x6001
        call 0x0138                     ; RSLREG: page 2 = our cartridge slot (same as page 1)
        rrca
        rrca
        and 3
        ld c,a
        ld b,0
        ld hl,0xFCC1
        add hl,bc
        or (hl)
        ld c,a
        inc hl
        inc hl
        inc hl
        inc hl
        ld a,(hl)
        and 0x0C
        or c
        ld h,0x80
        call 0x0024                     ; ENASLT
        di
        call player_load                ; (page 2 is our cartridge now)
        ld hl,(0x0004)                  ; BIOS font
        ld (v_font),hl
        ld a,2
        call CHGMOD                     ; SCREEN 2
        di
        ld a,0xC0                       ; 16K, display on, no interrupt, 8x8 sprites
        out (0x99),a
        ld a,0x81
        out (0x99),a
        ld a,0x01                       ; backdrop black
        out (0x99),a
        ld a,0x87
        out (0x99),a
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
        dec a
        ld (k8),a
        ld (k7),a
        ld (k3),a
        ld (k4),a
        ld (k5),a
        ld (sc_last),a
        call hzdetect
        call selftest
        IF TIETONLY
.tt:     call welcome                    ; test ROM: the logo and the title video, again and again
        jr .tt
        ENDIF
        IF DIAG
        jp diag
        ENDIF
        call welcome
.menu:  xor a
        ld c,1
        call music_play                 ; menu music (carries on if it already plays)
        call draw_menu
        call menu_loop                  ; NC = photo chosen, C = ESC
        jr nc,.size
        call credits
        jr .menu
.size:  call draw_size
        call size_loop                  ; carry = ESC, else A = N
        jr c,.menu
        ld (v_size),a
        call music_fadeout
        call puzzle                     ; carry = ESC (back to the menu), NC = solved
        push af
        xor a
        ld (p_hint),a
        pop af
        jr c,.menu
        call win
        jr .menu

        INCLUDE "core.asm"
        INCLUDE "music.asm"
        INCLUDE "screens.asm"
        INCLUDE "menu.asm"
        INCLUDE "puzzle.asm"
        INCLUDE "puzzle2.asm"
        INCLUDE "job.asm"
        INCLUDE "vplay.asm"
        INCLUDE "diag.asm"
        IF TITLEVIDEO
        INCLUDE "tvplay.inc"
        ENDIF
player_load:                            ; the player block from its ROM bank into the RAM
        ld hl,PLR_BANK
        call setbank
        ld hl,0x8000
        ld de,PLAYER_RAM
        ld bc,PLR_SIZE
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
