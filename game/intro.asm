; ------------------------------------------------------------------------------------------------ MSX2 and later: the FONY logo of the disk version in SCREEN 5 (runs in the overlay bank)
; The old disk (Puzzle Mania v1.04) draws the logo with palette registers black, then loads the 16 colours one by one (2 frames per colour) and shows it for 2 s; the jingle starts 0.7 s
; after the first colour; the colours go to black one by one (1 frame each).  The same here: the jingle is track 2 of the player (it has the 0.7 s of silence in front, music_play was
; called by the caller), every frame is one call of mvsync, the palette steps follow the frame counter.  Runs in the code bank (the player puts page 1 back to the code bank at the end of every frame, so no overlay); comes back in SCREEN 2.
        IF MSX2PAL
FONY_X  equ 4                           ; the logo starts at x = 8 (4 bytes), y = 20 (COPY "FONY.PZL" TO (8,20))
FONY_Y  equ 20
FONY_W  equ 119                         ; bytes per line of the picture in the bank (237 pixels + 1)
FONY_H  equ 66

i_vdp: out (0x99),a                    ; A = value, B = register
        ld a,b
        or 0x80
        out (0x99),a
        ret

intro:
        call i_setup
        xor a
        ld (v_i),a
        ld a,(v_hz)
        cp 50
        ld a,126                        ; the colours go away after 2.52 s
        jr z,.hz
        ld a,151
.hz:    ld (i_van),a
.fr:    call mvsync
        call getfire                    ; SPACE ends the logo at once
        jr nz,.end
        ld a,(v_i)
        ld c,a
        cp 28                           ; in: colour 2 + n every 2 frames (n = 0..13)
        jr nc,.nin
        and 1
        jr nz,.nxt
        ld a,c
        rrca
        and 0x7F
        add a,2
        call i_col
        jr .nxt
.nin:   ld a,(i_van)                    ; out: colour 2 + n to black every frame
        ld b,a
        ld a,c
        sub b
        jr c,.nxt
        cp 14
        jr nc,.nout
        add a,2
        call i_black
        jr .nxt
.nout:  ld a,b                          ; some black frames, then the title
        add a,24
        cp c
        jr z,.end
.nxt:   ld hl,v_i
        inc (hl)
        jr .fr
.end:   jp i_back

i_setup:                                ; SCREEN 5, 212 lines, palette black, the screen cleared, the logo in
        xor a
        ld b,1                          ; display off
        call i_vdp
        ld a,0x06                       ; R#0: SCREEN 5
        ld b,0
        call i_vdp
        ld a,0x3F                       ; R#2: the picture is on page 1 (0x8000..): the player writes the colour of the cursor sprites into the sprite attribute table of SCREEN 2 (0x1B03..) every frame, on page 0 that would be four dots in the logo
        ld b,2
        call i_vdp
        xor a
        ld b,7
        call i_vdp
        ld a,0x2A                       ; R#8: colour 0 is black, 64K VRAM, no sprites
        ld b,8
        call i_vdp
        ld a,(0xFFE8)
        or 0x80                         ; 212 lines
        ld b,9
        call i_vdp
        ld a,2                          ; R#14: VRAM address bits 16..14 = 010: 0x8000
        ld b,14
        call i_vdp
        xor a                           ; palette: all black
        ld b,16
        call i_vdp
        ld b,32
.p:     xor a
        out (0x9A),a
        djnz .p
        ld a,36                         ; HMMV: clear 256 x 212 with colour 0
        ld b,17
        call i_vdp
        ld hl,.cmd
        ld bc,0x0B9B
        otir
        ld a,2                          ; wait for the end of the command (status register 2, bit 0)
        ld b,15
        call i_vdp
.w:     in a,(0x99)
        rrca
        jr c,.w
        xor a
        ld b,15
        call i_vdp
        ld hl,FONY5B
        call setbank
        ld hl,0x8000
        ld de,FONY_Y * 128 + FONY_X
        ld a,FONY_H
        ld (v_i),a
.l:     ld a,e
        out (0x99),a
        ld a,d
        or 0x40
        out (0x99),a
        ld bc,FONY_W << 8 | 0x98
        otir
        ld a,e
        add a,128
        ld e,a
        jr nc,.nc
        inc d
.nc:    ld a,(v_i)
        dec a
        ld (v_i),a
        jr nz,.l
        xor a                           ; R#14 = 0 again
        ld b,14
        call i_vdp
        ld a,0x40                       ; display on
        ld b,1
        jp i_vdp
.cmd:   db 0,0,0,1,0,1,212,0,0,0,0xC0  ; DX, DY (256 = page 1), NX, NY, CLR, ARG, HMMV

i_col:                                  ; A = colour: its value from the table
        ld c,a
        add a,a
        ld e,a
        ld d,0
        ld hl,fony_pal
        add hl,de
        ld a,c
        out (0x99),a
        ld a,0x90
        out (0x99),a
        ld a,(hl)
        out (0x9A),a
        inc hl
        ld a,(hl)
        out (0x9A),a
        ret

i_black:                                ; A = colour: black
        out (0x99),a
        ld a,0x90
        out (0x99),a
        xor a
        out (0x9A),a
        out (0x9A),a
        ret

i_back:                                 ; the screen of the game again: SCREEN 2, the palette of the TMS9918A
        ld a,2
        call CHGMOD
        di
        ld a,0xC0
        ld b,1
        call i_vdp
        ld a,1
        ld b,7
        call i_vdp
        ld a,0x28
        ld b,8
        call i_vdp
        ld a,(0xFFE8)
        ld b,9
        call i_vdp
        xor a
        ld (v_pal),a
        ld b,16
        call i_vdp
        ld hl,tms_pal
        ld bc,0x209A
        otir
        ret

        ENDIF
