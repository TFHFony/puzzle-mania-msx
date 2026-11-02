; ------------------------------------------------------------------------------------------------ jingle player (runs in the overlay bank, entry 4006h)
; The FONY jingle (intro and win): a plain loop that does nothing but play (no frame, no screen work).  Data: JNGP (PSG: 2 banks) or JNGS (SCC: 4 banks), one byte per
; sample at a constant clock: PSG one sample per SND_T cycles (17.2 kHz; an index into the three volume tables of the player block, 3 channels summed), SCC one per SND_TS cycles
; (34.4 kHz; signed 8 bit, two samples per iteration like the SCC player of the game).  The samples are read with POP (SP is the pointer: no interrupts here, SP is put back at the end).
; In: C = number of banks (0.95 s on the PSG, 0.48 s on the SCC) in which SPACE / RETURN / fire do not stop it (0 = at once), bit 7 = the dreun of the film (BOOMP / BOOMS: the XXXL screen).  Out: carry = a key stopped it.
; Every iteration plays two samples; the keys are polled in the spare cycles of the iterations (SPACE, RETURN, fire, row select), four iterations per pass.
; tools/tune_snd.py measures the distance of the samples in openMSX and corrects the pads (sndcfg.inc).
        INCLUDE "sndcfg.inc"            ; SND_T, SND_TS (cycles per sample), SND_A.. (corrections of the pads; written by tools/tune_snd.py)

        MACRO PADH cyc                    ; n cycles where HL is free: NOP is 5, LD A,0 is 8, INC HL is 7 (an MSX waits one cycle at every opcode fetch); all n but 1..4, 6, 9, 11
_x = cyc
_s = 0
        IF !(_x >= 0 && (_x - 8 * ((2 * _x) % 5)) >= 0)
_s = 1
        ENDIF
        IF !((_x - 7 * _s) >= 0 && ((_x - 7 * _s) - 8 * ((2 * (_x - 7 * _s)) % 5)) >= 0)
_s = 2
        ENDIF
_m = _x - 7 * _s
_a = (2 * _m) % 5
_b = (_m - 8 * _a) / 5
        ASSERT _m >= 0 && _b >= 0
        DUP _s
        inc hl
        EDUP
        DUP _a
        ld a,0
        EDUP
        DUP _b
        nop
        EDUP
        ENDM
        MACRO PADA n
_a = (2 * (n)) % 5
_b = ((n) - 8 * _a) / 5
        ASSERT (n) >= 0 && _b >= 0
        DUP _a
        ld a,0
        EDUP
        DUP _b
        nop
        EDUP
        ENDM

snd_setb:                               ; (snd_bk) = the bank in page 2
        ld a,(snd_bk)
        ld (0x7000),a
        ld a,(snd_bk+1)
        BANKHI 0x7001
        ret

snd_keys:                               ; the PSG: mixer, joystick port 1, PPI rows (IYH = row 8: SPACE, IYL = row 7: RETURN), row 8 selected
        ld a,7
        out (0xA0),a
        ld a,0xBF
        out (0xA1),a
        ld a,15
        out (0xA0),a
        in a,(0xA2)
        and 0xBF
        out (0xA1),a
        in a,(0xAA)
        and 0xF0
        ld e,a
        or 8
        ld iyh,a
        ld a,e
        or 7
        ld iyl,a
        ld a,iyh
        out (0xAA),a
        ret

ov_snd: di
        ld (snd_sp),sp
        ld a,c
        and 0x7F
        ld (snd_dl),a
        ld a,c
        rlca
        and 1
        ld (snd_sel),a                  ; 1 = the dreun of the film (BOOMP / BOOMS) instead of the jingle
        ld hl,JNGP
        ld a,2
        jr z,.j
        ld hl,BOOMP
        ld a,NBOOMP
.j:     ld (snd_nb),a
        IF SCC
        ld a,(v_sccm)
        or a
        jp nz,snd_scc
        ENDIF
        ld (snd_bk),hl
        call snd_setb
        call snd_keys
        ld sp,0x8000
        ld c,0xA1
        ld ixl,0
        ld ixh,8                        ; 8 * 256 passes of 4 iterations (8 samples) = one bank (16 KB)
        jp psg_pass

; ---- the PSG: one iteration = two samples; the volumes of sample 1 (E) and 2 (D), a burst of six writes (A, B, C) close together
        MACRO PLOOK r                   ; r = the sample byte -> B, E, H = the volumes of channel A, B, C
        ld l,r
        ld h,TABHI
        ld b,(hl)
        inc h
        ld e,(hl)
        inc h
        ld h,(hl)
        ENDM
        MACRO PBURST
        ld a,8
        out (0xA0),a
        out (c),b
        inc a
        out (0xA0),a
        out (c),e
        inc a
        out (0xA0),a
        out (c),h
        ENDM

SND_BURST equ 102                       ; model of the cycles (tune_snd.py corrects them with the SND_A pads)
SND_LOOK equ 47
SND_POP equ 11

        MACRO PSGTOP p1, adj1            ; an iteration: sample 1 and 2; between burst 1 and burst 2: the lookup of sample 2 and p1 cycles of poll, the rest is pad
        pop de
        PLOOK e
        PBURST
        PADH SND_T - SND_BURST - SND_LOOK - (p1) + adj1
        PLOOK d
        ENDM
        MACRO PSGBOT p2, tail, adj2      ; after burst 2: p2 cycles of poll, pad, the end of the loop (tail cycles), the pop and the lookup of the next iteration
        PADH SND_T - SND_BURST - SND_POP - SND_LOOK - (p2) - (tail) + adj2
        ENDM

psg_pass:
        PSGTOP 29, SND_A11              ; ---- iteration 1: SPACE (row 8 is selected)
        in a,(0xA9)
        rra
        jp nc,snd_k1
snd_b1:
        PBURST
        PSGBOT 0, 0, SND_A12
        PSGTOP 52, SND_A21              ; ---- iteration 2: RETURN (row 7)
        ld a,iyl
        out (0xAA),a
        in a,(0xA9)
        rlca
        jp nc,snd_k2
snd_b2:
        PBURST
        PSGBOT 0, 0, SND_A22
        PSGTOP 39, SND_A31              ; ---- iteration 3: the fire button (the test after burst 2)
        ld a,14
        out (0xA0),a
        in a,(0xA2)
        ex af,af'
        PBURST
        ex af,af'
        and 0x10
        jp z,snd_k3
snd_b3:
        PSGBOT 24, 0, SND_A32
        PSGTOP 23, SND_A41              ; ---- iteration 4: row 8 again, the end of the pass
        ld a,iyh
        out (0xAA),a
        PBURST
        PSGBOT 0, 23, SND_A42
        dec ixl
        jp nz,psg_pass
        dec ixh
        jp nz,psg_pass
        ld hl,(snd_bk)                  ; the next bank
        inc hl
        ld (snd_bk),hl
        ld a,(snd_dl)
        or a
        jr z,snd_n1
        dec a
        ld (snd_dl),a
snd_n1: ld a,(snd_nb)
        dec a
        ld (snd_nb),a
        jr z,snd_end
        ld sp,(snd_sp)                  ; (the CALL needs a stack in the RAM: SP points into the data here)
        call snd_setb
        ld sp,0x8000
        ld ixh,8
        jp psg_pass

snd_end:ld sp,(snd_sp)
        or a                            ; carry 0: it played to the end
        ret
snd_stop:                               ; a key (SP is restored)
        ld sp,(snd_sp)
        scf
        ret

snd_k1: ld a,(snd_dl)
        or a
        jr z,snd_stop
        jp snd_b1
snd_k2: ld a,(snd_dl)
        or a
        jr z,snd_stop
        jp snd_b2
snd_k3: ld a,(snd_dl)
        or a
        jr z,snd_stop
        jp snd_b3

        IF SCC
; ---- the SCC: page 2 is switched to the slot of the SCC for the two writes of an iteration (B = that port A8h value, C = our cartridge); channel 1, the wave restarts at
; every frequency write (the same as the SCC player of the game).  Two samples SND_TS cycles apart, 2 * SND_TS per iteration.
snd_scc:ld hl,JNGS
        ld a,(snd_sel)
        or a
        ld a,4
        jr z,.j
        ld hl,BOOMS
        ld a,NBOOMS
.j:     ld (snd_nb),a
        ld (snd_bk),hl
        ld a,(snd_dl)                   ; (a bank is half as long here)
        add a,a
        ld (snd_dl),a
        call snd_setb
        ld a,(scc_pg)                   ; the same as scc_minit and scc_vol 15
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
        ld a,15
        ld (0x988A),a
        ld a,(cart_pg)
        out (0xA8),a
        call snd_keys
        ld a,(scc_pg)
        ld b,a
        ld a,(cart_pg)
        ld c,a
        ld sp,0x8000
        ld l,0
        ld h,8                          ; 8 * 256 passes of 4 iterations = one bank
        jp scc_pass

        MACRO SCCIT tail, adj1, adj2    ; the poll sits before this macro (_poll cycles)
        PADA SND_TS - 33 - _poll + adj1
        ld a,d                          ; sample 2
        ld (0x9800),a
        ld (0x9880),a
        ld a,c                          ; page 2 = our cartridge
        out (0xA8),a
        ENDM
        MACRO SCCHEAD
        pop de
        ld a,b                          ; page 2 = the SCC
        out (0xA8),a
        ld a,e                          ; sample 1
        ld (0x9800),a
        ld (0x9880),a
        ENDM

scc_pass:
        SCCHEAD                         ; ---- iteration 1: SPACE
        in a,(0xA9)
        rra
        jp nc,snd_s1
snd_c1:
_poll = 29
        SCCIT 0, SND_S11, SND_S12
        PADA SND_TS - 80 + SND_S12
        SCCHEAD                         ; ---- iteration 2: RETURN
        ld a,iyl
        out (0xAA),a
        in a,(0xA9)
        and 0x80
        jp z,snd_s2
snd_c2:
_poll = 55
        SCCIT 0, SND_S21, SND_S22
        PADA SND_TS - 80 + SND_S22
        SCCHEAD                         ; ---- iteration 3: the fire button
        ld a,14
        out (0xA0),a
        in a,(0xA2)
        and 0x10
        jp z,snd_s3
snd_c3:
_poll = 53
        SCCIT 0, SND_S31, SND_S32
        PADA SND_TS - 80 + SND_S32
        SCCHEAD                         ; ---- iteration 4: row 8 again, the end of the pass
        ld a,iyh
        out (0xAA),a
_poll = 23
        SCCIT 0, SND_S41, SND_S42
        PADA SND_TS - 80 - 16 + SND_S42
        dec l
        jp nz,scc_pass
        dec h
        jp nz,scc_pass
        ld de,(snd_bk)                  ; the next bank (page 2 is our cartridge)
        inc de
        ld (snd_bk),de
        ld a,(snd_dl)
        or a
        jr z,snd_n2
        dec a
        ld (snd_dl),a
snd_n2: ld a,(snd_nb)
        dec a
        ld (snd_nb),a
        jp z,snd_end
        ld sp,(snd_sp)                  ; (the CALL needs a stack in the RAM: SP points into the data here)
        call snd_setb
        ld sp,0x8000
        ld h,8
        jp scc_pass

snd_s1: ld a,(snd_dl)
        or a
        jr z,snd_sstop
        jp snd_c1
snd_s2: ld a,(snd_dl)
        or a
        jr z,snd_sstop
        jp snd_c2
snd_s3: ld a,(snd_dl)
        or a
        jr z,snd_sstop
        jp snd_c3
snd_sstop:
        ld a,c                          ; page 2 = our cartridge again
        out (0xA8),a
        jp snd_stop
        ENDIF
