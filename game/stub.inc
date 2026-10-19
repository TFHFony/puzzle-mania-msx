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
