; ------------------------------------------------------------------------------------------------ SCC (Konami sound cartridge): the win jingle (and later the music)
; The SCC sits in page 2 (9800h..98FFh after 3Fh has been written to 9000h) of the slot of its cartridge; our own ROM window is in page 2 as well, so page 2 is
; switched to the SCC slot for as long as the SCC plays and back to our slot afterwards (the bank registers are in page 1: they stay where they are).
        IF SCC
scc_scan:                               ; look for an SCC in all slots but our own: v_scc = 1, v_sccslot = its slot
        xor a
        ld (v_scc),a
        ld (v_i),a
.lp:    ld a,(v_i)
        and 3
        ld e,a
        ld d,0
        ld hl,0xFCC1
        add hl,de
        ld a,(hl)
        and 0x80
        ld c,a                          ; 80h if the primary slot is expanded
        ld a,(v_i)
        rrca
        rrca
        and 3                           ; sub slot
        jr z,.s0
        ld b,a
        ld a,c
        or a
        jr z,.skip                      ; sub slots exist in expanded slots only
        ld a,b
.s0:    add a,a
        add a,a
        or c
        ld c,a
        ld a,(v_i)
        and 3
        or c
        ld (v_tmp),a
        ld hl,v_own
        cp (hl)
        jr z,.skip
        call scc_try
        jr z,.found
.skip:  ld a,(v_i)
        inc a
        ld (v_i),a
        cp 16
        jr c,.lp
        jr .done
.found: ld a,(v_tmp)
        ld (v_sccslot),a
        ld a,1
        ld (v_scc),a
.done:  ld a,(v_own)                    ; our cartridge in page 2 again
        ld h,0x80
        call 0x0024
        di
        ret

scc_try:                                ; Z = the slot (v_tmp) has an SCC in page 2
        ld a,(v_tmp)
        ld h,0x80
        call 0x0024
        di
        ld a,(0xA000)                   ; RAM? (it would give the complement back)
        ld b,a
        cpl
        ld c,a
        ld (0xA000),a
        ld a,(0xA000)
        cp c
        jr nz,.nr
        ld a,b
        ld (0xA000),a
        or 1                            ; NZ
        ret
.nr:    ld a,0x3F                       ; Konami SCC mapper: bank 3Fh = the SCC registers
        ld (0x9000),a
        ld a,0x55
        ld (0x9800),a
        ld a,(0x9800)
        cp 0x55
        ret nz
        ld a,0xAA
        ld (0x9800),a
        ld a,(0x9800)
        cp 0xAA
        ret

; ---- the music on the SCC: our player block for the SCC (tools/gen_slots.py --scc) switches page 2 to the SCC slot with port A8h for the two writes of every sample.
; That only works when both slots are primary slots that are not expanded (the secondary slot register would have to be changed for every sample).
scc_mode_init:
        ld a,(v_scc)
        or a
        ret z
        ld a,(v_own)
        ld b,a
        ld a,(v_sccslot)
        or b
        and 0x8C                        ; one of them expanded (bit 7) or in a sub slot (bits 2, 3): the PSG
        ret nz
        ld a,FI_PAL_SCC                 ; the sample clock of the SCC player
        ld (fi_p),a
        ld a,FI_NTSC_SCC
        ld (fi_n),a
        in a,(0xA8)                     ; page 2 is our cartridge now
        ld (cart_pg),a
        and 0xCF
        ld b,a
        ld a,(v_sccslot)
        and 3
        add a,a
        add a,a
        add a,a
        add a,a
        or b
        ld (scc_pg),a
        ld a,1
        ld (v_sccm),a
        ld a,(scc_pg)                   ; the SCC: SCC mode, everything silent
        out (0xA8),a
        ld a,0x3F
        ld (0x9000),a
        xor a
        ld (0x988F),a
        ld hl,0x988A
        ld b,5
.v:     ld (hl),a
        inc hl
        djnz .v
        ld a,(cart_pg)
        out (0xA8),a
        ret

scc_minit:                              ; (music_play) channel 1 plays the samples: the wave restarts at every frequency write, period 0F00h + the sample (nearly silent: never reaches entry 1)
        ld a,(v_sccm)
        or a
        ret z
        ld a,(scc_pg)
        out (0xA8),a
        ld a,0x20
        ld (0x98E0),a
        ld a,0x0F
        ld (0x9881),a
        xor a
        ld (0x9880),a
        ld (0x988B),a
        ld (0x988C),a
        ld (0x988D),a
        ld (0x988E),a
        ld a,1
        ld (0x988F),a
        ld a,(cart_pg)
        out (0xA8),a
        ret

scc_gain_s:                             ; the same inside a slot of the player (page 2 is the SCC): no switching
        ld a,(mus_gs)
        add a,a
        add a,a
        ld d,a
        ld a,15
        sub d
        jr nc,.v
        xor a
.v:     ld (0x988A),a
        ret

scc_gain:                               ; the volume of channel 1 for the gain step mus_gs: 15, 11, 7, 3, 0 (keeps HL and C)
        ld a,(v_sccm)
        or a
        ret z
        ld a,(mus_gs)
        add a,a
        add a,a
        ld d,a
        ld a,15
        sub d
        jr nc,scc_vol
        xor a
scc_vol:                                ; A = volume of channel 1
        ld d,a
        ld a,(scc_pg)
        out (0xA8),a
        ld a,d
        ld (0x988A),a
        ld a,(cart_pg)
        out (0xA8),a
        ret

scc_off:
        ld a,(v_sccm)
        or a
        ret z
        xor a
        jr scc_vol

scc_tvstart:                            ; the title video of the SCC: channel 1 at full volume
        call scc_minit
        ld a,15
        jr scc_vol
        ENDIF

        IF SCC = 0
scc_minit:
scc_gain:
scc_gain_s:
scc_off:
scc_tvstart:
        ret
        ENDIF
