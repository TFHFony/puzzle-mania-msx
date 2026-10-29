; ------------------------------------------------------------------------------------------------ 50 / 60 Hz and the specs screen
; The game starts at 50 Hz where the VDP allows it (MSX2 and later: R#9 bit 1 = PAL), the SELECT key switches between 50 and 60 Hz (MSX2 and later only).
hz_init:
        ld a,0x40
        ld (sel_prev),a                 ; (SELECT is up)
        ld a,(0x002D)                   ; MSX version: 0 = MSX1 (a TMS9918A: 50 or 60 Hz is a fact of the machine)
        or a
        jp z,hzdetect
        ld a,50
        ld (v_hz),a
        ld a,(0xFFE8)                   ; the BIOS copy of register 9
        or 2
hz_write:
        ld (0xFFE8),a
        out (0x99),a
        ld a,0x89
        out (0x99),a
        ret

        MACRO MSXVER                    ; the MSX version the game behaves as: the machine, unless FORCE MSX1 is on (specs screen)
        IF MSX2PAL
        ld a,(v_msx)
        ELSE
        ld a,(0x002D)
        ENDIF
        ENDM

hz_toggle:
        MSXVER
        or a
        ret z
        ld a,(v_hz)
        cp 50
        ld a,(0xFFE8)
        jr z,.to60
        or 2
        ld b,50
        jr .w
.to60:  and 0xFD
        ld b,60
.w:     call hz_write
        ld a,b
        ld (v_hz),a
        ld a,(mus_on)                   ; the music has to start again: the length of a frame in samples is different
        or a
        ret z
        ld a,(mus_trk)
        push af
        call music_stop
        pop af
        ld c,0
        jp music_play

selchk:                                 ; SELECT (row 7 bit 6): once per press
        ld a,(mus_on)                   ; (with music the slots of the player look at it: mus_sel, latched)
        or a
        jr z,.slow
        ld a,(mus_sel)
        or a
        ret z
        xor a
        ld (mus_sel),a
        jp hz_toggle
.slow:  ld a,(k7)
        and 0x40
        ld b,a
        ld a,(sel_prev)
        ld c,a
        ld a,b
        ld (sel_prev),a
        or a
        ret nz
        ld a,c
        or a
        ret z
        jp hz_toggle

; ---- S held at the start: the specs
spec_check:
        ld a,5
        call row
        bit 0,a                         ; S (row 5, bit 0)
        ret nz
        ld a,0x20
        ld (pk_prev),a
        ld a,1
        ld (ck_prev),a
spec_screen:
        call clrscr
        ld hl,sp_title
        ld d,0
        ld e,7
        ld a,0xB1
        call boldcol
        ld hl,sp_specs
        ld d,2
        ld e,2
        ld a,0xF1
        call boldcol
        ld b,4                          ; MSX generation
        ld hl,sp_l1
        call .lab
        ld a,(0x002D)
        ld hl,sp_gen
        call .pick
        ld b,4
        call .val
        ld b,6                          ; the video chip
        ld hl,sp_l2
        call .lab
        ld hl,sp_tms
        ld a,(0x002D)
        or a
        jr z,.vd
        ld a,1                          ; S#1 holds the chip: bits 5..1 = 0 for a V9938, 2 for a V9958
        out (0x99),a
        ld a,0x8F
        out (0x99),a
        in a,(0x99)
        ld c,a
        xor a
        out (0x99),a
        ld a,0x8F
        out (0x99),a
        ld a,c
        and 0x3E
        ld hl,sp_v38
        jr z,.vd
        ld hl,sp_v58
.vd:    ld b,6
        call .val
        ld b,8                          ; the wait state of the VDP: the loop of the title video, 446 or 438 cycles (the test at the start, C toggles)
        ld hl,sp_l9
        call .lab
        ld hl,sp_446
        ld a,(v_tvd)
        or a
        jr z,.wt
        ld hl,sp_438
.wt:    ld b,8
        call .val
        ld b,10                         ; the sound chip
        ld hl,sp_l3
        call .lab
        ld hl,sp_psg
        IF SCC
        ld a,(v_sccm)
        or a
        jr z,.ns
        ld hl,sp_scc
        jr .sd
.ns:    ld a,(v_scc)
        or a
        jr z,.sd
        ld hl,sp_psg2
.sd:
        ENDIF
        ld b,10
        call .val
        ld b,12                         ; the refresh rate
        ld hl,sp_l4
        call .lab
        IF MSX2PAL
        ld a,(0x002D)
        or a
        jr z,.nopal
        ld b,14                         ; the palette: MSX2 (own palette per photo) or the MSX1 colours
        ld hl,sp_l8
        call .lab
        call .palval
.nopal:
        ENDIF
        ld a,(v_hz)                     ; (an MSX2 or later: SELECT switches, said on the line)
        cp 50
        ld hl,sp_50
        jr z,.h1
        ld hl,sp_60
.h1:    MSXVER
        or a
        jr z,.hz
        ld de,16                        ; the strings with "(SELECT)" follow
        add hl,de
        add hl,de
.hz:    ld b,12
        call .val
        ld b,16                         ; the slot of the SCC
        ld hl,sp_l6
        call .lab
        ld hl,sp_none
        ld a,(v_scc)
        or a
        jr z,.sn
        ld a,(v_sccslot)
        call .slot
        ld b,16
        call .valbuf
        jr .rom
.sn:    ld b,16
        call .val
.rom:   ld b,18                         ; the ROM
        ld hl,sp_l7
        call .lab
        ld a,BUILDID
        ld hl,sp_rom
        call .pick
        ld b,18
        call .val
        ld hl,sp_build                  ; "/ 65": the build number of the full 128 MB builds (game/buildno.inc, tools/build_number.txt)
        ld d,18
        ld e,25
        ld a,0xF1
        call boldcol
        ld hl,sp_eyes
        ld d,20
        ld e,13
        ld a,0xA1
        call boldcol
        ld hl,sp_url
        ld d,21
        ld e,2
        ld a,0xF1
        call boldcol
        ld hl,sp_esc
        ld d,23
        ld e,11
        ld a,0xE1
        call boldcol
.w:     call vsync
        IF MSX2PAL
        call palkey
        jp c,spec_screen                ; FORCE MSX1 changed: the whole screen again
        ENDIF
        call ckey
        jp c,spec_screen                ; the title video loop changed
        call selkey
        jp c,spec_screen                ; 50 / 60 Hz changed
        call getesc
        jr nz,.w
        jp wait_release

        IF MSX2PAL
.palval:ld hl,sp_pal2
        ld a,(v_msx)
        or a
        jr nz,.pv
        ld hl,sp_pal1
.pv:    ld b,14
        jp .val

        ENDIF

.lab:   ld d,b                          ; label: HL, row B, column 2
        ld e,2
        ld a,0xE1
        jp boldcol
.val:   ld d,b                          ; value: HL, row B, column 18
        ld e,18
        ld a,0xF1
        jp boldcol
.valbuf:
        ld hl,nbuf
        jr .val
.pick:  and 3                           ; A = index: the A-th string of the table HL (16 bytes each)
        add a,a
        add a,a
        add a,a
        add a,a
        ld e,a
        ld d,0
        add hl,de
        ret
.slot:  ld c,a                          ; A = slot (ENASLT format) -> text in nbuf: "1" or "3-1"
        ld hl,nbuf
        and 3
        add a,'0'
        ld (hl),a
        inc hl
        ld a,c
        rlca
        jr nc,.s1
        ld (hl),'-'
        inc hl
        ld a,c
        rrca
        rrca
        and 3
        add a,'0'
        ld (hl),a
        inc hl
.s1:    ld (hl),0
        ret

sp_title: db "PUZZLE MANIA XXXL",0
sp_specs: db "SPECS:",0
sp_l1:  db "MSX GENERATION:",0
sp_l2:  db "VIDEO CHIP:",0
sp_l3:  db "SOUND CHIP:",0
sp_l4:  db "SCREEN:",0
sp_l9:  db "WAIT STATE:",0
sp_446: db "446 (C)",0
sp_438: db "438 (C)",0
sp_l6:  db "SCC SLOT:",0
sp_l7:  db "ROM / BUILD:",0
        IF MSX2PAL
sp_l8:  db "FORCE MSX1:",0
sp_pal2: db "OFF (P)",0
sp_pal1: db "ON (P)",0
        ENDIF
sp_gen: db "MSX1",0,0,0,0,0,0,0,0,0,0,0,0
        db "MSX2",0,0,0,0,0,0,0,0,0,0,0,0
        db "MSX2+",0,0,0,0,0,0,0,0,0,0,0
        db "MSX TURBO R",0,0,0,0,0
sp_tms: db "TMS9918A",0,0,0,0,0,0,0,0
sp_v38: db "V9938",0,0,0,0,0,0,0,0,0,0,0
sp_v58: db "V9958",0,0,0,0,0,0,0,0,0,0,0
sp_psg: db "PSG",0,0,0,0,0,0,0,0,0,0,0,0,0
sp_psg2: db "PSG (SCC NOT USED)",0
sp_scc: db "SCC 16 KHZ",0
sp_50:  db "50 HZ",0,0,0,0,0,0,0,0,0,0,0
sp_60:  db "60 HZ",0,0,0,0,0,0,0,0,0,0,0
        db "50 HZ (SELECT)",0,0
        db "60 HZ (SELECT)",0,0
sp_none: db "NONE",0
sp_rom: db "64 MB",0,0,0,0,0,0,0,0,0,0,0
        db "128 MB",0,0,0,0,0,0,0,0,0,0
        db "15 MB TEST",0,0,0,0,0,0
        db "?",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
        INCLUDE "buildno.inc"
sp_eyes: db "(.)(.)",0
sp_url: db "HTTPS://WWW.FILE-HUNTER.COM",0
sp_esc: db "ESC = BACK",0

ckey:                                   ; C (row 3 bit 0), once per press: the title video loop 446 <-> 438 cycles (C = changed)
        ld a,3
        call row
        and 1
        ld b,a
        ld a,(ck_prev)
        ld c,a
        ld a,b
        ld (ck_prev),a
        or a
        ret nz
        ld a,c
        or a
        ret z
        ld a,(v_tvd)
        xor 1
        ld (v_tvd),a
        scf
        ret

selkey:                                 ; SELECT (row 7 bit 6), once per press: 50 / 60 Hz (an MSX2 or later; C = pressed)
        ld a,7
        call row
        and 0x40
        ld b,a
        ld a,(sel_prev)
        ld c,a
        ld a,b
        ld (sel_prev),a
        or a
        ret nz
        ld a,c
        or a
        ret z
        call hz_toggle
        scf
        ret

        IF MSX2PAL
palkey:                                 ; P (row 4 bit 5), once per press, on an MSX2 or later: the MSX1 colours instead of the palette per photo
        ld a,(0x002D)
        or a
        ret z                           ; (NC)
        ld a,4
        call row
        and 0x20
        ld b,a
        ld a,(pk_prev)
        ld c,a
        ld a,b
        ld (pk_prev),a
        or a
        ret nz
        ld a,c
        or a
        ret z
        ld a,(v_msx)
        or a
        jr z,.on
        xor a                           ; the MSX1 look: no palettes, the photos for the fixed colours
        ld (v_msx),a
        ld hl,0
        ld (v_pb),hl
        jr .d
.on:    ld a,(0x002D)
        ld (v_msx),a
        ld hl,PBOFFS
        ld (v_pb),hl
.d:     scf
        ret
        ENDIF
