; overlay bank: the video player.  Page 1 (4000h..7FFFh) is switched to this bank by the stub (stub.inc) while a clip plays.
        DEVICE NOSLOT64K
        ORG 0x4000
        INCLUDE "equ.inc"
        jp ov_main
        INCLUDE "video.asm"
        ASSERT $ < 0x7F00
        ds 0x7F00-$,0xFF
        INCLUDE "stub.inc"
        ds 0x8000-$,0xFF
        SAVEBIN "ovl.bin",0x4000,0x4000
