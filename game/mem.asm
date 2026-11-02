; overlay bank MEMB: the choice screen and the memory game (memplay.asm) with the cards (memdata.bin: tools/memory_cards.py).  Page 1 is switched to this bank by the stubs (stub.inc).
        DEVICE NOSLOT64K
        ORG 0x4000
        INCLUDE "equ.inc"
        jp mm_init                      ; 4000h
        jp mm_frame                     ; 4003h
        jp mg_init                      ; 4006h
        jp mg_frame                     ; 4009h
        INCLUDE "memplay.asm"
        ASSERT $ < 0x4600
        ds 0x4600-$,0xFF
        INCBIN "memdata.bin"
        ASSERT $ < 0x7F00
        ds 0x7F00-$,0xFF
        INCLUDE "stub.inc"
        ds 0x8000-$,0xFF
        SAVEBIN "mem.bin",0x4000,0x4000
