; the wait state test (wtest.asm: lives in the bank SELFTEST, runs from the RAM at the start) and its result
WT_RAM  equ 0xEB00      ; the test is copied here (free at the start: the puzzle's RAM copy of the picture comes later)
WT_VARS equ 0xED00      ; its variables
WT_LEN  equ 0x0200      ; bytes that are copied (the code is shorter)
v_wait  equ 0xC390      ; extra cycles per loop of 8 VDP writes: 8 = a T9769 (MSX2+ of Sanyo / Panasonic, turbo R), 0 = none
v_tvd   equ 0xC391      ; the title video loop: 0 = 446 cycles per iteration, 1 = 438 (a VDP wait state); the test sets it, the specs screen (C) toggles it
ck_prev equ 0xC392      ; C of the previous frame in the specs screen (bit 0, 0 = down)
att_hb  equ 0xC393      ; word: the first bank of the second half of the menu song (extra.asm att_init)
mus_any equ 0xC396      ; (slots of the player) NZ = a key that the game uses, or the joystick, is down
mus_sel equ 0xC397      ; SELECT went down (latched: the consumer clears it)
mus_dk  equ 0xC398      ; one cursor key: 1 up, 3 right, 5 down, 7 left, else 0
mus_ke  equ 0xC399      ; the keys L, C, T that went down (bits 0..2, latched: the consumer clears it)
mus_t2  equ 0xC39A      ; temporaries of the slots
mus_t3  equ 0xC39B
mus_t4  equ 0xC39C
mus_dkey equ 0xC39D     ; getkey: the direction on a press / auto repeat, else 0
