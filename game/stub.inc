; overlay stub: the same bytes at the same address (7F00h) in the code bank and in the overlay bank, because the bank switch of page 1 happens while it runs
ovl_video:
        ld a,OVLB
        ld (0x6000),a
        xor a
        BANKHI 0x6001
        call 0x4000                     ; the entry of the overlay
        xor a
        ld (0x6000),a                   ; back to the code bank
        BANKHI 0x6001
        ret
ovl_jig:                                ; the jigsaw outro of the title: (vbank) = the first bank of its stream, carry = a key stopped it
        ld a,OVLB
        ld (0x6000),a
        xor a
        BANKHI 0x6001
        call 0x4003
        push af
        xor a
        ld (0x6000),a
        BANKHI 0x6001
        pop af
        ret
ovl_snd:                                ; the FONY jingle: C = banks in which a key does not stop it, carry = a key stopped it
        ld a,OVLB
        ld (0x6000),a
        xor a
        BANKHI 0x6001
        call 0x4006
        push af
        xor a
        ld (0x6000),a
        BANKHI 0x6001
        pop af
        ret
ovl_fony:                               ; the FONY film (fonyplay.asm): carry = a key stopped it
        ld a,OVLB
        ld (0x6000),a
        xor a
        BANKHI 0x6001
        call 0x4009
        push af
        xor a
        ld (0x6000),a
        BANKHI 0x6001
        pop af
        ret
        MACRO MEMSTUB entry
        ld a,MEMB & 255
        ld (0x6000),a
        ld a,MEMB >> 8
        BANKHI 0x6001
        call entry
        push af
        xor a
        ld (0x6000),a
        BANKHI 0x6001
        pop af
        ret
        ENDM
ovl_mm_init:                            ; the memory bank (mem.asm): the choice screen / the game, one routine per call
        MEMSTUB 0x4000
ovl_mm_frame:
        MEMSTUB 0x4003
ovl_mg_init:
        MEMSTUB 0x4006
ovl_mg_frame:
        MEMSTUB 0x4009
