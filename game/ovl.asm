; overlay bank: the video player.  Page 1 (4000h..7FFFh) is switched to this bank by the stub (stub.inc) while a clip plays.
        DEVICE NOSLOT64K
        ORG 0x4000
        INCLUDE "equ.inc"
        jp ov_main
        jp ov_jig                       ; 4003h: the jigsaw outro of the title (jigplay.asm)
        jp ov_snd                       ; 4006h: the FONY jingle (sndplay.asm)
        jp ov_fony                      ; 4009h: the FONY film (fonyplay.asm)
        INCLUDE "video.asm"
        INCLUDE "jigplay.asm"
        INCLUDE "sndplay.asm"
        INCLUDE "fonyplay.asm"
        ASSERT $ < 0x7F00
        ds 0x7F00-$,0xFF
        INCLUDE "stub.inc"
        ds 0x8000-$,0xFF
        SAVEBIN "ovl.bin",0x4000,0x4000
