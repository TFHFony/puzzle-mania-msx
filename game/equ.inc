; ---- BIOS / hardware
CHGMOD  equ 0x005F
BURST   equ 800

; ---- RAM (page 3, 0C000h..): the game uses well under 1 KB, the rest is left to the BIOS
v_photo equ 0xC000      ; chosen photo 0..8
v_size  equ 0xC001      ; puzzle size N (3..6)
v_sel   equ 0xC002      ; menu selection (photo number)
v_pdir  equ 0xC003      ; last direction key, for the auto repeat
v_rep   equ 0xC004
v_rng   equ 0xC005      ; word, random seed
v_font  equ 0xC007      ; word, address of the BIOS font
v_frame equ 0xC009      ; frame counter of the menus (flashing cursor)
v_cx    equ 0xC00A      ; sprite cursor rectangle in pixels
v_cy    equ 0xC00B
v_cw    equ 0xC00C
v_ch    equ 0xC00D
v_i     equ 0xC00E      ; loop counter
v_hz    equ 0xC00F      ; 50 or 60
b_w     equ 0xC010      ; blit parameters
b_h     equ 0xC011
b_rows  equ 0xC012
b_cols  equ 0xC013
b_ss8   equ 0xC014      ; word
b_cofs  equ 0xC016      ; word
t_col   equ 0xC018
v_lines equ 0xC019      ; tile lines: 0 thick, 1 thin, 2 off
v_ctl   equ 0xC01A      ; control: 0 arrow keys slide the tile, 1 sprite cursor + SPACE
v_pcx   equ 0xC01B      ; puzzle cursor position (control 1)
v_pcy   equ 0xC01C
v_pf    equ 0xC01D      ; SPACE state of the previous frame
v_ccol  equ 0xC01E      ; sprite colour override (0 = flashing yellow / red)
p_tw    equ 0xC020      ; tile width / height / offset of the puzzle field in characters
p_th    equ 0xC021
p_ox    equ 0xC022
p_oy    equ 0xC023
p_n2    equ 0xC024      ; N * N
p_bx    equ 0xC025      ; blank position
p_by    equ 0xC026
p_hshow equ 0xC027      ; H held
p_cnt   equ 0xC028      ; word
p_last  equ 0xC02A
m_ox    equ 0xC02B      ; the position the blank came from (last move)
m_oy    equ 0xC02C
m_i0    equ 0xC02D
m_i1    equ 0xC02E
p_hint  equ 0xC02F      ; hint frames left
d_x     equ 0xC030
d_y     equ 0xC031
d_t     equ 0xC032
d_dy    equ 0xC033
d_dx8   equ 0xC034
d_sx    equ 0xC035
d_sy    equ 0xC036
d_sl    equ 0xC037
d_sh    equ 0xC038
vbank   equ 0xC040      ; video player
vleft   equ 0xC042
vbase   equ 0xC044
vnf     equ 0xC046
vptr    equ 0xC04A      ; read pointer of the packed frames (8000h..BFFFh in the bank vbank)
snd_bk  equ 0xC06D      ; word: bank of the jingle in the page 2 window (sndplay.asm)
snd_sp  equ 0xC06F      ; word: SP of the caller
snd_dl  equ 0xC071      ; banks of the jingle in which a key does not stop it
snd_nb  equ 0xC072      ; banks left
; ---- the memory game (memplay.asm, memory.asm): its state is in the RAM of the puzzle permutation (C100h..C13Fh)
m_pic   equ 0xC100      ; 20 bytes: the photo (0..11) of every place
m_st    equ 0xC114      ; 20 bytes: 0 face down, 1 face up (turned), 2 pair found
m_cx    equ 0xC128
m_cy    equ 0xC129
m_f1    equ 0xC12A      ; the places of the cards that are turned (255 = none)
m_f2    equ 0xC12B
m_wait  equ 0xC12C      ; frames to wait (the cards of a wrong pair turn back, the last pair stays)
m_pairs equ 0xC12D
m_moves equ 0xC12E      ; word
m_prev  equ 0xC130      ; the keys of the previous frame
m_rep   equ 0xC131      ; frames that a cursor key is down
m_fr    equ 0xC132      ; frames of this second
m_win   equ 0xC133
m_last  equ 0xC134      ; the photo of the last pair
m_ic    equ 0xC135      ; the photo on the card of the choice screen
m_sel   equ 0xC136      ; the choice: 0 sliding puzzle, 1 memory
m_cur   equ 0xC137
att_k   equ 0xC07C      ; the attract mode: the next kind (0 = sliding puzzle, 1 = memory), it alternates
att_pd  equ 0xC07D      ; the attract mode of the sliding puzzle starts at once in the photo menu (started from the choice screen)
m_att   equ 0xC07E      ; the memory game is played by the attract mode (a bot: memplay.asm)
m_tgt   equ 0xC07F      ; the bot: the place of the card it moves to
m_ph    equ 0xC080      ; the bot: 0 chooses the first card, 1 moves to it, 2 chooses the second card, 3 moves to it
m_dl    equ 0xC081      ; the bot: frames to wait
m_jn    equ 0xC082      ; the cards that the memory bank wants drawn by the jobs of the player (memory.asm mem_jobs): the number
m_jq    equ 0xC083      ; and the entries: destination (pattern address), source (in the memory bank), 4 bytes each, at most 2
snd_sel equ 0xC07B      ; 1 = the dreun of the film is played (sndplay.asm)
fy_ptr  equ 0xC073      ; word: the table entry of the next frame of the FONY film (fony.inc)
fy_st   equ 0xC075      ; word: its address in the bank
fy_bk   equ 0xC077      ; word: its bank
fy_base equ 0xC079      ; word: the first bank of the stream in use
lbl     equ 0xC050      ; text buffer (16 bytes)
v_src   equ 0xC060      ; word
v_dd    equ 0xC062      ; word
g_x     equ 0xC064
g_y     equ 0xC065
v_win   equ 0xC066      ; first visible column of the photo carousel
p_nshow equ 0xC067      ; N held
g_fp    equ 0xC068      ; word
g_r     equ 0xC06A
v_ssel  equ 0xC06B      ; size menu selection
v_t2    equ 0xC06C
nbuf    equ 0xC090      ; 48 bytes
n_d1    equ 0xC0C0
n_d2    equ 0xC0C1
n_nc    equ 0xC0C2
g_fp2   equ 0xC0C4      ; word
v_tmp   equ 0xC0C8
v_tmp2  equ 0xC0CA      ; word
mus_on  equ 0xC0D0      ; sample player
mus_trk equ 0xC0D1
mus_bank equ 0xC0D2     ; word, current 16 KB bank of the track
mus_ptr equ 0xC0D4      ; word, 8000h..BFFFh
mus_s   equ 0xC0D6      ; word, first bank of the track
mus_e   equ 0xC0D8      ; word, bank after the last one
mus_f   equ 0xC0DB      ; samples per video frame: 160 at 50 Hz; 133 (+1 every third frame) at 60 Hz
mus_fx  equ 0xC0DC      ; 0 = 50 Hz
mus_fc  equ 0xC0DD
mus_tab equ 0xC0DE      ; high byte of the volume tables in use (gain step)
mus_gs  equ 0xC0DF      ; gain step 0 (full) .. 4 (silent)
k8      equ 0xC0E0      ; keyboard rows 8, 7, 3, 4, 5 (0 = pressed), read once per frame
k7      equ 0xC0E1
k3      equ 0xC0E2
k4      equ 0xC0E3
mus_gt  equ 0xC0E4      ; target gain step
mus_fz  equ 0xC0E5      ; frames since the last gain step
mus_lp  equ 0xC0E6      ; track loops
mus_done equ 0xC0E7     ; a track that does not loop has reached its end
sc_last equ 0xC0E8      ; last sprite cursor written (x, y, w, h, colour)
k5      equ 0xC0ED
p_ek    equ 0xC0EE      ; keys L, C, T of the previous frame (edge detection)
p_moves equ 0xC0F0      ; word
p_secs  equ 0xC0F2      ; word
p_fr    equ 0xC0F4
mus_fr  equ 0xC0F9      ; sample clock accumulator
mus_k   equ 0xC0FB      ; samples of a frame that are skipped (time of the work of the caller)
mus_sl  equ 0xC0FC      ; polls of the last wait for the blanking (0 = late)
mus_n   equ 0xC0FD      ; samples played in this frame
mus_fl  equ 0xC0FE      ; samples in this frame
mus_fi  equ 0xC0FA      ; its step (fraction of the iterations that are 5 cycles longer)
h_x     equ 0xC0F5      ; hint rectangle
h_y     equ 0xC0F6
h_w     equ 0xC0F7
h_h     equ 0xC0F8
perm    equ 0xC100      ; permutation of the tiles (64 bytes)
mus_n2   equ 0xC140     ; plan of the next frame: samples to play
mus_k2   equ 0xC141     ; samples to skip
mus_sk   equ 0xC142     ; samples to skip in this frame
mus_fl2  equ 0xC143     ; length of the next frame
mus_sp   equ 0xC144     ; samples skipped in the previous frame
mus_dl   equ 0xC145     ; change of the number of skipped samples
mus_kt   equ 0xC146     ; track: fixed number of skipped samples (0 = adapt)
mus_am   equ 0xC147     ; 0xFF = the number of skipped samples adapts, 0 = fixed
mus_busy equ 0xC148     ; the game has work to do this frame (a key changed / is down, the cursor flashes, the hint runs)
pk8      equ 0xC149     ; keys of the previous frame
pk7      equ 0xC14A
pk3      equ 0xC14B
pk4      equ 0xC14C
pk5      equ 0xC14D
mus_ch   equ 0xC14E     ; keys that changed
mus_kbt  equ 0xC14F     ; track: fixed number of skipped samples of a busy frame
mus_kb   equ 0xC150
mus_nb2  equ 0xC151     ; plan of the next frame (busy)
mus_kb2  equ 0xC152
mus_ce   equ 0xC155     ; colour of the cursor sprites
j_qp     equ 0xC157     ; job queue (8 byte entries in the ring JQ): read pointer, write pointer, number of entries
j_qa     equ 0xC159
j_qn     equ 0xC15B
j_dend   equ 0xC15C     ; high byte of the VRAM address of the last row of the running phase
j_lc     equ 0xC15D     ; word: 98h, bytes per row (loaded into BC)
j_go     equ 0xC15F
p_shadow equ 0xC161     ; the RAM copy of the puzzle image is valid
JQ       equ 0xC200     ; job ring (16 entries of 8 bytes)
j_adj    equ 0xC162     ; word: source step at the end of a row
j_ln     equ 0xC165     ; bytes per row of a tile (width * 8)
JT       equ 0xC180     ; offset of every cell of the puzzle in the picture / on the screen (one word per cell)
mus_np   equ 0xC1C8     ; plan of this frame by busy level 0..7: samples to play (written during the previous frame)
mus_kp   equ 0xC1D0     ; samples to skip
mus_pr   equ 0xC16E     ; keys that were pressed this frame
mus_kct  equ 0xC16F     ; track: fixed number of skipped samples of an action frame (level 2)
mus_kc   equ 0xC170
mus_kd   equ 0xC171     ; FFh: a cursor key is down
b4_r     equ 0xC172     ; boldcol4: row of the text
b4_cur   equ 0xC173     ; word: glyph of the cell that is drawn
b4_f     equ 0xC175     ; 1 = the last cell (the right half of the last character)
d_only   equ 0xC177     ; drawpos: 1 = only the tile numbers (the tiles are on the screen already)
g_i      equ 0xC178     ; loop counter of the queue routines
OVLB     equ 255        ; ROM bank of the overlay (the video player), mapped into page 1 by the stub (stub.inc)
v_xtra   equ 0xC179     ; the 8 fps ROM: one extra blanking per frame (for the overlay)
mus_p8   equ 0xC17A     ; keys of row 8 that were pressed this frame (cursor keys in the high nibble)
mus_km   equ 0xC17B     ; skipped samples while the sprite cursor moves
mus_t    equ 0xC17C     ; temporary of the slots
mus_rd   equ 0xC17D     ; FFh: a held cursor key repeats in this frame (v_rep = 1)
mus_cp   equ 0xC17E     ; FFh: a cursor key went down in this frame
v_bc     equ 0xC17F     ; the colour of the screen that the MSX started with (RG7SAV at the start of the cartridge)

; ---- the player (volume tables + mvsync + mnext) runs from RAM, so that page 1 can show another ROM bank to the job engine while it plays
PLAYER_RAM equ 0xC400   ; the block is copied here at the start (ROM bank PLR_BANK)
TABHI    equ 0xC4       ; the volume tables come first in the block
mvsync   equ 0xD300     ; = PLAYER_RAM + 15 * 256 (5 gain sets of 3 tables)
VEC_ROW  equ 0x7EE0     ; routines of the code bank that the player calls (a jump table at fixed addresses)
VEC_FADE equ 0x7EE3
VEC_SETBANK equ 0x7EE6
VEC_VSYNC equ 0x7EE9
VEC_TICK equ 0x7EEC

        MACRO SETADDR addr
        ld a,addr&0xFF
        out (0x99),a
        ld a,(addr>>8)|0x40
        out (0x99),a
        ENDM
        MACRO VOUT                      ; a VRAM write with the pause that the VDP needs while the screen is drawn (29 cycles between two accesses, or bytes are lost)
        out (0x98),a
        nop
        nop
        nop
        nop
        ENDM
att_on   equ 0xC1F7     ; the attract mode plays the puzzle
att_t    equ 0xC1F8     ; frames until the next move of the attract mode
att_p    equ 0xC1F0     ; word: end of the recorded shuffle moves
att_idle equ 0xC1F2     ; word: frames without a key in the photo menu
att_d    equ 0xC300     ; NPHOTO bytes: photos that the attract mode has solved
scc_pg   equ 0xC1F4     ; port A8h value with page 2 = the slot of the SCC (the sample goes there)
cart_pg  equ 0xC1F5     ; port A8h value with page 2 = our cartridge
att_act  equ 0xC385     ; a key was pressed since the second half of the menu song began
att_wo   equ 0xC386     ; the menu song is in its second half
att_sz   equ 0xC380     ; the size (3 or 4) that the attract mode has chosen
mus_wr   equ 0xC381     ; how many times the music of a track has come round (the attract mode starts when the menu song ends)
att_wr   equ 0xC382     ; its value when the menu was entered
pk_prev  equ 0xC384     ; P of the previous frame in the specs screen (bit 5, 0 = down)
sel_prev equ 0xC383     ; SELECT of the previous frame (bit 6, 0 = down)
sl_b     equ 0xC37E     ; the SCC player: the second sample of the iteration while a task of a slot runs
sl_jc    equ 0xC37D     ; the SCC player: a register of the joystick task that lives across two slots
v_sccm   equ 0xC37A     ; 1 = the music goes to the SCC (the player block for the SCC is in the RAM)
fi_p     equ 0xC37B     ; sample clock fractions of the player block in use (50 Hz / 60 Hz)
fi_n     equ 0xC37C
v_own    equ 0xC1F6     ; slot of our cartridge (ENASLT format)
v_scc    equ 0xC1FE     ; 1 = an SCC was found
v_sccslot equ 0xC1FF    ; its slot
v_pb     equ 0xC1FA     ; word: offset of the photo banks (MSX2 version: the photos coded for their own palette, behind the video)
v_msx    equ 0xC1FC     ; 0 = MSX1, else MSX2 or later (palette registers)
v_pal    equ 0xC1FD     ; palette that is loaded (0FFh = none yet)
v_tit    equ 0xC1F9     ; 128 MB ROM: 0 = the next title is the video, 1 = the photo
JW_PAL   equ 2110       ; counted frame of the win loop (tools: measured in openMSX)
JW_NTSC  equ 1715
ATT_BUF  equ 0xC310     ; the moves of the shuffle (one byte each, up to 192)
CONF     equ 0xC310     ; confetti: y, x, speed, drift, colour (5 bytes each)
NCONF    equ 16
ATT_SHOW  equ 90      ; frames that the attract mode shows its choice (the photo, then the size)
ATT_DELAY equ 48      ; frames between two moves of the attract mode: 1 move per second at 50 Hz (the drawing of a move runs in the player while the music goes on)
ATT_DELAY60 equ 58
p_bank   equ 0xC1E0     ; word: ROM bank of the puzzle picture (size, line style)
j_nl     equ 0xC1E2     ; - bytes per row of a tile
j_zero   equ 0xC1E3     ; always 0
q_adj    equ 0xC1E4     ; word: source step at the end of a row (the entry that jq_put writes)
q_bank   equ 0xC1E6     ; word: ROM bank of the source of that entry
j_bank   equ 0xC1E8     ; word: ROM bank of the source of the running phase: page 1 shows it while the loop of the player copies
j_t      equ 0xC1EA     ; temporary of the queue routines
d_cnt   equ 0xC040     ; diagnostic build (diag.asm): frames left in the run
d_late  equ 0xC042      ; word: late frames
d_sum   equ 0xC044      ; word: sum of the slack of the frames that were not late
d_min   equ 0xC046
d_run   equ 0xC047
d_to    equ 0xC048      ; word: waits for the blanking that ran out
d_buf   equ 0xC050
tv_f    equ 0xC1EF     ; title video: the frame that is queued next
joy     equ 0xC1EE     ; joystick port 1 as read from PSG register 14 (0 = pressed)
mus_pl  equ 0xC1ED     ; busy level of the previous frame (FREE: the delay that makes every frame equally long)
v_tmp3   equ 0xC1E9     ; word: the number of frames of the confetti in the solved screen
bankdummy equ 0xC1EC   ; ASCII16 build: target of the stores that replace the high byte of a bank register (same duration)
        INCLUDE "cfg.inc"
        INCLUDE "memcfg.inc"            ; MEMB, MEMPAL (the memory game, generated by tools/build_game.py)
        INCLUDE "fonycfg.inc"           ; FYFRAMES, FYP1.. (the FONY film, generated by tools/build_game.py)
        INCLUDE "wtequ.inc"
NPHOTO equ 12                   ; the number of photos (tools/encode_clips.py USED)
MAXWIN equ (NPHOTO + 1) / 2 - 2 ; the last v_win of the menu: the carousel has (NPHOTO + 1) / 2 columns of 2, two are visible
PLR_BANK_SCC equ PLR_BANK - 1       ; the player block for the SCC       ; ASCII16, DIAG, FREE, TITLEVIDEO, TVBANK, TVFRAMES, PLR_BANK, TIETONLY, MSX2PAL, PBOFFS, WELCOME2, SCC, BUILDID (generated by tools/build_game.py)
        MACRO BANKHI addr       ; A = high byte of a bank number
        IF ASCII16
        ld (bankdummy),a
        ELSE
        ld (addr),a
        ENDIF
        ENDM
mus_hint equ 0xC1EB    ; the game sets it before mvsync when it is going to queue screen work: that frame gets the action pause (level 2)
