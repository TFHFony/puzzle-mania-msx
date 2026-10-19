# Puzzle Mania — user manual

*A sliding puzzle with a video reward for the MSX1 — 16 KB RAM — NEO16 cartridge*
*MSXdev26 entry — freeware*

![Title screen](images/02b_title_video.png)

> **Adult content:** the photos and videos contain nudity. For players of 18 and older.

---

## 1. The game

Choose one of nine photos, choose how many pieces it is cut into (3×3 up to 6×6), shuffle, and slide the pieces back into place.
When the picture is complete a jingle plays, the screen flashes and the video clip starts. It loops until you press SPACE.

Everything runs on a plain **MSX1**: TMS9918A video chip (SCREEN 2, 15 colours), 16 KB RAM, the PSG for sound.
The photos, the music and the videos live in the ROM of a **NEO16** mapper cartridge. You play with the keyboard, or with a joystick in port 1.

### Requirements

| Item | Needed |
|---|---|
| Computer | MSX1 or later, 16 KB RAM is enough (about 9 KB is used). 50 Hz and 60 Hz machines both work. A keyboard or a joystick in port 1. |
| Cartridge | NEO16 mapper (16 KB banks). The 64 MB ROM fits every NEO16 cartridge; the 128 MB ROM needs a cartridge that maps more than 64 MB. |
| Emulator | openMSX: `openmsx -machine Philips_VG_8020 -cart PuzzleMania_64MB.rom -romtype NEO-16`. openMSX and the standard WebMSX read at most 64 MB of a NEO16 ROM, so use the 64 MB file there. A WebMSX that maps more than 64 MB plays the 128 MB file. |
| Sound | The PSG (AY-3-8910 or YM2149). The music is a sample, see [chapter 7](#7-music-and-sound). |

### The ROM files

| File | Contents |
|---|---|
| `PuzzleMania_64MB.rom` | The normal version (63 MB). The reward videos are cut to about 70 % of their length and fade out. The title screen shows the photo in the letters of PUZZLE MANIA, with music, until you press SPACE. |
| `PuzzleMania_128MB.rom` | The full version (107 MB). The reward videos have their full length (10 frames per second), and the title screen shows a **video in the letters** (30 seconds, with music) that leads to the photo menu. Only for cartridges and emulators that map more than 64 MB. |

---

## 2. Starting the game

After power-on the cartridge checks that the NEO16 mapper works. If it does not, a message tells you so instead of a black screen.
Then the **FONY logo** appears for three seconds (SPACE skips it), followed by the **PUZZLE MANIA** title with the menu music.

- **64 MB version:** the letters are filled with a photo. Press SPACE to go to the photo menu.
- **128 MB version:** the letters show a video with the music in the background. When the video is finished you arrive in the photo menu; SPACE (or fire) goes there at once.

| | | |
|---|---|---|
| ![FONY logo](images/01_fony.png) | ![Title screen (64 MB)](images/02_title.png) | ![Title screen (128 MB): the letters show a video](images/02c_title_video.png) |
| The FONY logo | The title screen of the 64 MB version | The title screen of the 128 MB version (video) |

## 3. Choosing a photo

Four photos are shown at a time. The four yellow corners show the selected photo. Move with the **cursor keys** (or the joystick); at the side of the screen a
triangle shows that there are more photos: the list scrolls one column at a time, two photos stay in view. Press **SPACE** (or RETURN, or fire) to choose.

| | |
|---|---|
| ![Photo menu](images/06_menu.png) | ![Photo menu, scrolled](images/07_menu_scrolled.png) |
| The first four photos | Scrolled one column |

The bottom line shows © 2026 FONY, a smile and [H]ELP: **H** shows two pages of help (SPACE = next page, ESC = back); **ESC** shows the credits.

| | |
|---|---|
| ![Help, page 1](images/03_howto1.png) | ![Help, page 2](images/04_howto2.png) |
| Help, page 1 (H at the photo menu) | Help, page 2 |

## 4. Choosing the size

The four buttons show your photo with the grid of 3×3, 4×4, 5×5 and 6×6 pieces. Choose with the cursor keys and SPACE, ESC goes back.
Two options can be set here (and also during the game):

| Key | Option | Values |
|---|---|---|
| **L** | Tile lines | OFF (default): no lines at all. THICK: white lines around every piece. THIN: one pixel line. Each press goes to the next value. |
| **C** | How a piece is moved | ARROWS (default): an arrow key slides the piece next to the gap. CURSOR: move the four yellow corners to a piece and press SPACE. |

| | |
|---|---|
| ![Size menu](images/08_size.png) | ![Size menu with CURSOR control](images/08b_size_cursor.png) |
| The size menu with the two options | After pressing C: the control is CURSOR |

## 5. Playing

The empty square is the gap. Only a piece next to the gap can move. The picture is complete when every piece is back where it came from.
The game always starts from a puzzle that can be solved. The moves and the time start at 0 with every new puzzle.

| Key | What it does |
|---|---|
| Cursor keys | ARROWS: slide the piece next to the gap in that direction (press LEFT and the piece on the right of the gap slides left). CURSOR: move the corners to a piece. |
| SPACE / RETURN | CURSOR control: slide the piece under the corners into the gap (it must be next to the gap). |
| **H** (hold) | Shows the finished photo for as long as you hold the key. |
| **N** (hold) | Shows the number of every piece (its place in the solved picture, 1 to N×N−1) and, in the gap, the number of **moves** and the elapsed **time**. |
| **T** | Hint: flashes green corners around the piece that belongs on the square where the gap is now. |
| **L** | Tile lines: off, thick, thin. |
| **C** | Control: ARROWS or CURSOR. |
| ESC | Back to the photo menu. |

### Joystick (port 1)

The joystick works at the same time as the keyboard everywhere in the game.

| Joystick | Same as |
|---|---|
| Stick up, down, left, right | The cursor keys |
| Fire A | SPACE (choose, next page, stop the video) |
| Fire B (hold) | H: the finished photo |
| Fire A and left together | ESC |

| | |
|---|---|
| ![A shuffled 4x4 puzzle](images/09_puzzle4.png) | ![N held: numbers, moves and time](images/10_numbers.png) |
| A shuffled 4×4 puzzle (no lines) | N held: piece numbers, moves and time |
| ![Hint](images/11_hint.png) | ![Solution](images/13_solution.png) |
| T: the hint (green corners, bottom left) | H held: the solution |
| ![Thick lines](images/13a_lines.png) | ![Thin lines](images/13b_lines.png) |
| Thick lines | Thin lines |
| ![No lines](images/13c_lines.png) | ![CURSOR control](images/12_cursor_mode.png) |
| No lines | CURSOR control: yellow corners |

## 6. Solved!

When the last piece slides into place the picture is shown, a short **jingle** plays, the border and four corner marks **flash**, and a line at the bottom
shows your moves and time. After the jingle the **video** starts and loops. Press **SPACE** (or fire) to return to the photo menu
(a new puzzle with the same or another photo).

| | |
|---|---|
| ![Solved](images/14_solved.png) | ![Reward video](images/15_video.png) |
| The solved picture with the result line | The reward video |

## 7. Music and sound

The MSX1 has no sample chip, so the music is played as a **sample on the three PSG channels** (about 8 kHz, 5 bit): each channel gets a volume value for every sample.
There is no timer on an MSX1, therefore the player outputs the samples itself, with an exact clock. The program does its other work (keyboard,
counters, cursor flashes, and the redrawing of the screen) in the tiny gaps between two samples, so the music goes on while you play.

### What you may notice

- The music keeps playing while pieces slide, while you hold N or H, when the photo menu scrolls and in the help pages.
- A few screen changes still cause a short pause (about 0.04 to 0.1 s): choosing a photo and leaving a puzzle with ESC. Starting a puzzle is silent: the puzzle is built first and then its music fades in. The music then continues at the right place.
- Menu music fades out when you start a puzzle; the puzzle music fades in (and the other way round after ESC).
- Menu music: PM-Menu theme. Puzzle music: PM theme. The jingle plays once.
- The reward videos have no sound: the video player needs all the processor time.
- In the 128 MB version the title video has its own player that mixes video and music without any gaps: the sound is continuous while the letters play the video.

## 8. Tips

- Start with 3×3 to learn the controls; use T when you are stuck and H to look at the picture.
- Solve the top row first, then the left column, and work towards the bottom right corner.
- With N you can see which pieces belong together, even when the photo is dark.
- THIN or OFF lines show more of the photo; THICK lines show the pieces best on large grids.
- The 5×5 and 6×6 puzzles use smaller pieces: CURSOR control is handy there.

## 9. Troubleshooting

| Problem | Solution |
|---|---|
| A message "NO NEO16 MAPPER" | The ROM must be started as a NEO16 cartridge: in openMSX use `-romtype NEO-16`. |
| The wrong video or garbage after a puzzle | Your emulator or cartridge reads less than the ROM size (openMSX / WebMSX: 64 MB). Use `PuzzleMania_64MB.rom`. |
| No sound | Check that the PSG is enabled; the music is a PSG sample. In a browser emulator click on the screen first (the browser only starts the sound after a click or key press). |
| Keys do not react | The game reads the keyboard matrix directly. The joystick must be in port 1. |

## 10. Technical notes

- MSX1, TMS9918A SCREEN 2: every 8×1 pixel row has two of the 15 fixed colours. All pictures are error-diffused with a colour-pair search;
  edges (borders, tile lines, lettering) are coded with constraints so that colours do not bleed.
- The reward video player writes a full frame of 12 KB straight into the visible tables, one 16 KB NEO16 bank per frame, at 10 frames per second
  (8.3 fps in the 64 MB version, 6 or 7 screen refreshes per frame on 50 or 60 Hz). It lives in its own overlay bank (255).
- The game code is a single 16 KB bank (bank 0); the NEO16 window at 8000h brings in pictures, samples and video frames. The sample player is copied to the RAM
  (C400h) at the start, so that the window at 4000h can show data banks while it plays.
- Sound: 3-channel PSG sample at 8025 Hz (446 CPU cycles on PAL): a block of samples per frame, a few skipped samples as gap. The first
  samples of every block are "slots" that carry the work of the frame, and a small **job engine** in the sample loop copies queued pieces of picture to the VDP
  (4 bytes per sample), so that tile moves, the help pages and the menus are drawn without silence. The music does not wait for the vblank flag
  (real machines lose it now and then) and every frame takes the same time, whatever the work of the game.
- The title video (128 MB version) is one stream: per iteration of 446 cycles 1 sample byte for the PSG and 8 bytes for the VDP, one 16 KB bank per video frame
  (about 5 frames per second, 154 frames). The picture is written row by row (pattern row, then colour row), so the picture never has new patterns with old colours for more than a row.
- Input: the keyboard matrix and joystick port 1 are read directly (no BIOS, no interrupts): the game runs with interrupts disabled.
- 50 Hz and 60 Hz machines are both supported.

## 11. Credits

| | |
|---|---|
| Coding | The File-Hunter & Claude |
| GFX | The File-Hunter & Tittygram |
| Music | The File-Hunter & Solmi AI |

![Credits](images/16_credits.png)

## 12. Freeware licence

**PUZZLE MANIA — freeware.**

You may download, play, copy and distribute this game, free of charge, as long as the files are kept unchanged and complete (ROM files, manual) and no fee is asked for it.
The game must always be freely obtainable in its full version.

The authors keep the ownership of the game, the pictures, the music and the videos; all rights that are not explicitly granted here are reserved.
During the MSXdev compo the game is exclusive to the MSXdev website; afterwards the authors may redistribute it or sell it.

The game is provided "as is", without any warranty. Use it at your own risk.

*The game contains nudity (photos and videos) and is meant for adults (18+).*
