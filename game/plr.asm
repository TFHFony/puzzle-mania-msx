; the player block, assembled for its place in the RAM (tools/build_game.py stores it in ROM bank PLR_BANK)
        DEVICE NOSLOT64K
SCCPLAYER equ 0
        INCLUDE "equ.inc"
        INCLUDE "heads.inc"
        INCLUDE "clk.inc"
        ORG PLAYER_RAM
        INCLUDE "player.asm"
        ASSERT mvsync_ == mvsync
PLR_END:
        SAVEBIN "plr.bin",PLAYER_RAM,PLR_END-PLAYER_RAM
