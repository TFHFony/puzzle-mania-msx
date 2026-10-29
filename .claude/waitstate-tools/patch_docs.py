"""one-time: the manual and the README follow the game (specs screen, wait state test, SCC / MSX2 versions, sample jingle, derived keys in the slots)"""
P = 'F:/MSX Projects/PMdev26/'


def edit(fn, pairs):
    s = open(P + fn, encoding='utf8', newline='').read()
    crlf = '\r\n' in s
    s = s.replace('\r\n', '\n')
    for a, b in pairs:
        assert s.count(a) == 1, (fn, a[:60])
        s = s.replace(a, b)
    if crlf:
        s = s.replace('\n', '\r\n')
    open(P + fn, 'w', encoding='utf8', newline='').write(s)


edit('docs/MANUAL.md', [
("""Everything runs on a plain **MSX1**: TMS9918A video chip (SCREEN 2, 15 colours), 16 KB RAM, the PSG for sound.
The photos, the music and the videos live in the ROM of a **NEO16** mapper cartridge. You play with the keyboard, or with a joystick in port 1.
""", """Everything runs on a plain **MSX1**: TMS9918A video chip (SCREEN 2, 15 colours), 16 KB RAM, the PSG for sound. An **MSX2, MSX2+ or turbo R** (128 MB version) gives every photo a palette of its own,
and an **SCC** cartridge gives the music 16 kHz. The photos, the music and the videos live in the ROM of a **NEO16** mapper cartridge. You play with the keyboard, or with a joystick in port 1.
"""),
("""| Sound | The PSG (AY-3-8910 or YM2149). The music is a sample, see [chapter 7](#7-music-and-sound). |
""", """| Sound | The PSG (AY-3-8910 or YM2149). The music is a sample, see [chapter 7](#7-music-and-sound). A Konami SCC cartridge in another slot is used when there is one (128 MB version). |
"""),
("""| `PuzzleMania_128MB.rom` | The full version (88 MB). The reward videos""", """| `PuzzleMania_128MB.rom` | The full version (96 MB, build number on the specs screen). The reward videos"""),
("""With an **SCC** cartridge in another slot the music (menu, puzzle and the title video) plays on the SCC at 16 kHz, 8 bit, and so does the jingle. Only for cartridges""", """With an **SCC** cartridge in another slot the music (menu, puzzle and the title video) plays on the SCC at 16 kHz, 8 bit, and so does the jingle. A test at power-on checks whether the video chip adds a wait state to every write (see [the specs screen](#2b-the-specs-screen)) and keeps the music at the right speed. Only for cartridges"""),
("""After power-on the cartridge checks that the NEO16 mapper works. If it does not, a message tells you so instead of a black screen.
Then the **FONY logo** appears for three seconds (SPACE skips it), followed by the **PUZZLE MANIA** title with the menu music.
""", """After power-on the cartridge checks that the NEO16 mapper works. If it does not, a message tells you so instead of a black screen. (The 128 MB version then tests the video chip for a wait state; the screen stays black
for about half a second.) Hold **S** while the game starts to see the [specs screen](#2b-the-specs-screen).
Then the **FONY logo** appears for three seconds (SPACE skips it): on an MSX1 in one purple colour, on an MSX2 or later in the 16 colours of the disk version of the game, which come in one by one with the FONY jingle. It is followed by the **PUZZLE MANIA** title with the menu music.
"""),
("""## 3. Choosing a photo
""", """## 2b. The specs screen

Hold **S** while the game starts (or press reset with S held) and the specs screen appears instead of the logo. ESC goes on to the game.

![Specs screen](images/17_specs.png)

| Line | Meaning |
|---|---|
| MSX GENERATION | MSX1, MSX2, MSX2+ or MSX turbo R (BIOS). |
| VIDEO CHIP | TMS9918A, V9938 or V9958. |
| **WAIT STATE** | The loop of the title video (128 MB version): **446** cycles per sample, or **438** when the video chip adds a wait state to every write. The game tests this at power-on (8 writes to the VDP per iteration run a little slower on the MSX2+ of Sanyo and Panasonic and on a turbo R, whose T9769 adds a cycle; the MSX1, MSX2 and the Sony MSX2+ do not). Press **C** to switch between the two values if the music of the title sounds too low or too high on your machine. |
| SOUND CHIP | PSG, PSG (SCC not used) or SCC 16 kHz. |
| SCREEN | 50 or 60 Hz; **SELECT** switches (MSX2 and later). |
| FORCE MSX1 | MSX2 and later: **P** shows the photos with the fixed MSX1 colours instead of the palette per photo. |
| SCC SLOT | The slot of the SCC cartridge, or NONE. |
| ROM / BUILD | 64 MB, 128 MB or 15 MB TEST, with the build number of the 128 MB version. |

## 3. Choosing a photo
"""),
("""The jingle is not a sample: it is played by the sound chip itself. On the PSG it is a fanfare with a fast arpeggio (one note of the chord per frame); with an **SCC** it
is played with five voices and real chords.
""", """The jingle is the FONY jingle of the disk version of the game, played as a **sample** (on the PSG at about 8 kHz, with an **SCC** at 16 kHz). It starts when the picture is complete and has its full volume at once.
"""),
("""- Menu music: PM-Menu theme. Puzzle music: PM theme. The jingle plays once.
""", """- Menu music: PM-Menu theme. Puzzle music: PM theme. The jingle plays once.
- The screens are built first, and then the music starts: the photo menu is drawn while the player runs silent, after that the song fades in from its beginning. Stopping the music leaves the PSG at its level of silence, so there is no click.
"""),
("""in the menu, in the puzzle and in the title video. The jingle uses the SCC as a synthesizer (five voices). Without an SCC""", """in the menu, in the puzzle and in the title video, and the jingle is played on the SCC as well. Without an SCC"""),
("""- In the 128 MB version the title video has its own player that mixes video and music without any gaps: the sound is continuous while the letters play the video.
""", """- In the 128 MB version the title video has its own player that mixes video and music without any gaps: the sound is continuous while the letters play the video. The music of the title is coded for the speed of that loop, so the song has its true pitch in the PSG and in the SCC version, and the picture runs equally fast in both (the SCC version has its own, slightly longer frames).
"""),
("""| Keys do not react | The game reads the keyboard matrix directly. The joystick must be in port 1. |
""", """| Keys do not react | The game reads the keyboard matrix directly. The joystick must be in port 1. |
| The music of the title video is too low or too high | Hold S at power-on and look at the WAIT STATE line: 446 for a video chip without wait state, 438 with. Press C to try the other one. |
| The photos look different (MSX2 and later) | Hold S at power-on: FORCE MSX1 (P) switches between the palette per photo and the MSX1 colours. |
"""),
("""- Sound: 3-channel PSG sample at 8025 Hz (446 CPU cycles on PAL): a block of samples per frame, a few skipped samples as gap. The first
  samples of every block are "slots" that carry the work of the frame, and a small **job engine** in the sample loop copies queued pieces of picture to the VDP
  (4 bytes per sample), so that tile moves, the help pages and the menus are drawn without silence. The music does not wait for the vblank flag
  (real machines lose it now and then) and every frame takes the same time, whatever the work of the game.
""", """- Sound: 3-channel PSG sample at 8025 Hz (446 CPU cycles on PAL): a block of samples per frame, a few skipped samples as gap (a stop frame is exactly one VDP frame: 160 samples). The first
  samples of every block are "slots" that carry the work of the frame: the keyboard rows, the joystick, the busy level of the frame and the **derived keys** (any key, SELECT, the cursor direction with its auto repeat, the keys L, C and T), so that the main loop only reads
  a few variables. A small **job engine** in the sample loop copies queued pieces of picture to the VDP
  (4 bytes per sample), so that tile moves, the help pages and the menus are drawn without silence. The music does not wait for the vblank flag
  (real machines lose it now and then) and every frame takes the same time, whatever the work of the game. The SCC player does the same with 16 kHz (two samples per iteration).
- Wait state test (128 MB version): the bank of the self-test holds a small program that is copied to the RAM and run with the screen off. Two loops of the same length (8 writes to the VDP, or 8 reads of an unused port) run for two frames each, counted by the VDP interrupt; if the VDP loop does 5 or more cycles fewer per iteration, the title video uses its loop of 438 cycles instead of 446 (the T9769 of the MSX2+ of Sanyo and Panasonic and of the turbo R adds one cycle to every VDP access). The result and the loop in use are shown on the specs screen.
"""),
("""- The title video (128 MB version) is one stream: per iteration of 446 cycles 1 sample byte for the PSG and 8 bytes for the VDP, one 16 KB bank per video frame
  (about 5 frames per second, 154 frames).""", """- The title video (128 MB version) is one stream: per iteration of 446 cycles 1 sample byte for the PSG and 8 bytes for the VDP, one 16 KB bank per video frame
  (about 5 frames per second, 152 frames; with an SCC two samples per iteration and 147 frames of its own, cut at the speed of that loop)."""),
])

edit('README.md', [
("""On an MSX2 or later (128 MB version) every photo has a palette of its own.
""", """On an MSX2 or later (128 MB version) every photo has a palette of its own; hold **S** at power-on for the specs screen (video chip, wait state test, SCC, 50/60 Hz, build number).
"""),
("""| `PuzzleMania_128MB.rom` | the full version (88 MB): full length 10 fps reward videos and a 30 s video with music in the letters of the title; needs a cartridge / emulator that maps more than 64 MB |""",
 """| `PuzzleMania_128MB.rom` | the full version (96 MB): full length 10 fps reward videos and a 30 s video with music in the letters of the title, a palette per photo on an MSX2 or later, 16 kHz music on an SCC; needs a cartridge / emulator that maps more than 64 MB |"""),
("""`plr.asm`/`player.asm` the PSG sample player that runs from RAM (`slots.inc` is generated by `tools/gen_slots.py`, the slot lengths in `heads.inc` by `tools/tune_slots.py`),
  `ovl.asm`/`video.asm` the video player in its own overlay bank, `tvplay.inc` (generated by `tools/gen_tvplay.py`) the player of the title video (video and PSG samples in one stream),""",
 """`plr.asm`/`player.asm` the PSG sample player that runs from RAM (`slots.inc` is generated by `tools/gen_slots.py`, the slot lengths in `heads.inc`; `plr_scc.asm` + `slots_scc16.inc` from `tools/gen_slots16.py` and `scc16.json` the 16 kHz SCC player),
  `spec.asm` the specs screen, `msx2.asm` / `intro.asm` the palette per photo and the FONY logo of the MSX2, `scc.asm` the SCC, `extra.asm` the attract mode, `wtest.asm` the VDP wait state test (it lives in the bank of the self-test and runs from the RAM),
  `ovl.asm`/`video.asm` the video player in its own overlay bank, `tvplay.inc` / `tvplay8.inc` (generated by `tools/gen_tvplay.py`, 446 and 438 cycles per iteration) and `tvplay16.inc` / `tvplay16w.inc` (`tools/gen_tvplay16.py`, SCC) the players of the title video (video and music in one stream),"""),
("""  `music.py` (PSG samples), `gen_pjingle.py` (the win jingle for the PSG and the SCC), `palette_opt.py`""", """  `music.py` (PSG and SCC samples, the jingle is a sample too), `palette_opt.py`"""),
("""  `build_timing.py` (timing test ROM). The manual is `docs/MANUAL.md`.""", """  `build_timing.py` (timing test ROM). The manual is `docs/MANUAL.md`.
  `build_game.py` counts a build number for the full 128 MB build (`tools/build_number.txt`, shown on the specs screen); test builds (`--lite`, `--quick`, `--only-clip0 --clipframes N` for a small test ROM) show none."""),
("""* `.claude/pm-tools/` openMSX Tcl scripts""", """* `.claude/waitstate-tools/` and `.claude/logomusic-tools/` small ROMs and scripts that were used to measure the VDP wait state, the title video loop and the slots of the player (`PM_WaitState_16KB.rom`, the loop test ROM, `slotmeas.py`, `tune_psg.py`, `tune_scc.py`).
* `.claude/pm-tools/` openMSX Tcl scripts"""),
])
print('ok')
