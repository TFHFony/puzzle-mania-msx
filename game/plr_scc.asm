; the player block for an SCC, assembled for its place in the RAM (tools/build_game.py stores it in ROM bank PLR_BANK_SCC): the sample goes to the SCC
        DEVICE NOSLOT64K
SCCPLAYER equ 1
        INCLUDE "equ.inc"
        INCLUDE "heads.inc"
        INCLUDE "clk_scc.inc"
        ORG PLAYER_RAM
        INCLUDE "player.asm"
        ASSERT mvsync_ == mvsync
PLR_END:
        SAVEBIN "plr_scc.bin",PLAYER_RAM,PLR_END-PLAYER_RAM
