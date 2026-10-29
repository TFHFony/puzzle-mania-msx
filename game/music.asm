; ------------------------------------------------------------------------------------------------ PSG sample player
; 8 kHz, 3 channels summed: one byte per sample, an index into three 256 byte tables (volume of channel A, B, C); 5 table sets give the gain
; steps of the fades.  There is no timer on an MSX1, so the waiting loops of the game (mvsync) output the samples themselves, at an exact
; 8000 Hz clock.  The music is locked to the frame: a frame is exactly mus_f samples long, the samples that were not played because the
; screen work took time are skipped, so pitch and phase stay right.  While big pieces of the screen are drawn the music pauses.
; tracks: 0 menu, 1 puzzle
music_play:                             ; A = track, C = 1: fade in.  A track that is already playing keeps going.
        ld b,a
        ld a,(mus_on)
        or a
        jr z,.go
        ld a,(mus_trk)
        cp b
        ret z
.go:    ld a,b
        ld (mus_trk),a
        add a,a
        add a,a
        add a,a
        ld e,a
        ld d,0
        ld hl,mustab
        IF SCC
        ld a,(v_sccm)                   ; the SCC player has its own music (16 kHz)
        or a
        jr z,.mt
        ld hl,mustab_scc
.mt:
        ENDIF
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld (mus_s),de
        ld (mus_bank),de
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld (mus_e),de
        ld a,(hl)
        ld (mus_lp),a
        inc hl
        ld a,(hl)                       ; fixed number of skipped samples of the track (the music is coded for it), 0 = adapt
        ld (mus_kt),a
        inc hl
        ld a,(hl)                       ; the same for a frame in which the game has work to do after the block (busy)
        ld (mus_kbt),a
        inc hl
        ld a,(hl)                       ; ... and for an action frame (a key was pressed, the cursor key repeats)
        ld (mus_kct),a
        xor a
        ld (mus_done),a
        ld (mus_fz),a
        ld (mus_gt),a
        ld (mus_gs),a
        ld hl,0x8000
        ld (mus_ptr),hl
        ld a,(mus_kt)
        ld c,a
        ld a,0xFF                       ; mask of the adaptation
        ld (mus_am),a
        ld a,c
        or a
        jr nz,.fk
        ld a,8
        jr .fk2
.fk:    xor a
        ld (mus_am),a
        ld a,c
.fk2:   ld (mus_k),a
        ld a,(mus_am)                   ; skipped samples of a busy frame
        or a
        ld a,(mus_k)
        jr nz,.kb
        ld a,(mus_kbt)
.kb:    ld (mus_kb),a
        ld a,(mus_am)
        or a
        ld a,(mus_k)
        jr nz,.kc
        ld a,(mus_kct)
.kc:    ld (mus_kc),a
        ld a,1
        ld (mus_busy),a
        ld a,(v_hz)                     ; frame length in samples
        cp 50
        ld a,160
        ld b,0
        jr z,.fr
        ld a,133
        inc b
.fr:    ld (mus_f),a
        ld (mus_fl2),a
        ld c,a                          ; plan of the first frame
        ld a,(mus_k)
        ld (mus_k2),a
        ld d,a
        ld a,c
        sub d
        ld (mus_n2),a
        ld a,(mus_kb)
        ld (mus_kb2),a
        ld d,a
        ld a,c
        sub d
        ld (mus_nb2),a
        ld a,(mus_kb)                   ; the cursor moves a little slower than idle: two samples more than a busy frame
        add a,2
        cp 17
        jr c,.km
        ld a,16
.km:    ld (mus_km),a
        MACRO PLN idx, kvar
        ld a,(kvar)
        ld d,a
        ld (mus_kp+idx),a
        ld a,c
        sub d
        ld (mus_np+idx),a
        ENDM
        PLN 0,mus_k                     ; plan of the first frame, by busy level
        PLN 1,mus_kb
        PLN 2,mus_kc
        PLN 3,mus_kc
        PLN 4,mus_km
        PLN 5,mus_km
        PLN 6,mus_kc
        PLN 7,mus_kc
        ld a,b
        ld (mus_fx),a
        ld a,(fi_p)
        bit 0,b
        jr z,.fi
        ld a,(fi_n)
.fi:    ld (mus_fi),a
        xor a
        ld (mus_fc),a
        ld a,TABHI
        ld (mus_tab),a
        ld a,c
        or a
        jr z,.nf
        ld a,4                          ; start silent and fade in
        ld (mus_gs),a
        ld a,TABHI+12
        ld (mus_tab),a
.nf:    ld a,1
        ld (mus_on),a
        call scc_minit                  ; (the SCC: channel 1 for the samples)
        call scc_gain
        ld a,7                          ; mixer: tone and noise off, the channels only give their volume
        out (0xA0),a
        ld a,0xBF
        out (0xA1),a
        ret

music_stop:
        call scc_off
        xor a
        ld (mus_on),a
        ld (mus_gs),a
        ld (mus_gt),a
        dec a
        ld (mus_trk),a
        IF SCC
        ld a,(v_sccm)
        or a
        jr nz,.zero                     ; (the SCC plays the music: the PSG is idle)
        ENDIF
        ld a,8                          ; the PSG stays at the level of silence (the first entries of the constant tables of gain step 4): a step to volume 0 is a click
        out (0xA0),a
        ld a,(TABHI*256+0xC00)
        out (0xA1),a
        ld a,9
        out (0xA0),a
        ld a,(TABHI*256+0xD00)
        out (0xA1),a
        ld a,10
        out (0xA0),a
        ld a,(TABHI*256+0xE00)
        out (0xA1),a
        ret
        IF SCC
.zero:  ld a,8
        out (0xA0),a
        xor a
        out (0xA1),a
        ld a,9
        out (0xA0),a
        xor a
        out (0xA1),a
        ld a,10
        out (0xA0),a
        xor a
        out (0xA1),a
        ret
        ENDIF

music_fadeout:                          ; fade the music out (0.5 s), then stop it
        ld a,(mus_on)
        or a
        ret z
        ld a,4
        ld (mus_gt),a
        ld b,60
.w:     push bc
        call mvsync
        pop bc
        ld a,(mus_gs)
        cp 4
        jr z,.d
        djnz .w
.d:     jp music_stop

fadestep:                               ; every 6 frames one gain step towards the target
        ld a,(mus_gt)
        ld b,a
        ld a,(mus_gs)
        cp b
        ret z
        ld c,a
        ld a,(mus_fz)
        inc a
        ld (mus_fz),a
        cp 6
        ret c
        xor a
        ld (mus_fz),a
        ld a,c
        cp b
        jr c,.up
        dec c
        jr .sv
.up:    inc c
.sv:    ld a,c
        ld (mus_gs),a
        ld b,a
        add a,a
        add a,b
        add a,TABHI
        ld (mus_tab),a
        jp scc_gain_s                   ; (called from a slot of the player: page 2 is the SCC already)
