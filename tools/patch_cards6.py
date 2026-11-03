"""one-off patch (applied once): the memory cards centred. A card is 40 x 40 pixels inside a block of 6 x 5 characters (48 x 40: four black pixels at both sides), so the
5 blocks of the row fill the characters 1..30 and the margins at the left and the right are equal (12 pixels). The edge characters hold black and one card colour only (the frame is 4 pixels
wide, the photos are coded with the black margin as a fixed colour): no colour bleed. 13 x 2 cards of 480 bytes do not fit in the overlay bank any more: they sit in their own data bank MEMD = MEMB + 1."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__)); G = os.path.join(HERE, '..', 'game')

# ---- memplay.asm
p = os.path.join(G, 'memplay.asm'); t = open(p).read()
a = t.index('MEMDATA equ 0x4600'); b = t.index('        MACRO CELLADDR')
t = t[:a] + """MEMDATA equ 0x4600
CARD    equ 480                         ; a card: 5 rows of 48 pattern bytes, 5 rows of 48 colour bytes (6 x 5 characters: 40 pixels and a black margin of 4 pixels at both sides)
MEMICON equ MEMDATA                     ; the big cards of the choice screen (2080 bytes each: MSX1, MSX2); the cards themselves are in the bank MEMD (26 x 480 bytes)

""" + t[b:]
a = t.index('csrc:'); b = t.index('dcard:')
t = t[:a] + """csrc:   ld l,d                          ; D = card image 0..12 -> HL = its address in the bank MEMD as page 1 shows it (4000h +): 480 d (the variant of the machine)
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl                       ; 32 d
        ld c,l
        ld b,h
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl                       ; 512 d
        or a
        sbc hl,bc                       ; 480 d
        ld bc,0x4000
        IF MSX2PAL
        ld a,(v_msx)
        or a
        jr z,.b
        ld bc,0x4000 + 13 * CARD
.b:
        ENDIF
        add hl,bc
        ret

""" + t[b:]
old = "dcard:  push de                         ; E = place, D = image\n        call csrc\n        pop de\n"
assert old in t
t = t.replace(old, """dcard:  push de                         ; E = place, D = image: the card is read through the window of page 2 (the bank MEMD)
        call csrc
        ld a,h
        add a,0x40                      ; 8000h +
        ld h,a
        push hl
        ld hl,MEMD
        ld a,l
        ld (0x7000),a
        ld a,h
        BANKHI 0x7001
        pop hl
        pop de
""", 1)
old = "        ld c,0x98\n        ld b,40\n.o:     outi\n        jp nz,.o\n        pop bc\n        inc b                           ; the next character row\n"
assert old in t
t = t.replace(old, old.replace('ld b,40', 'ld b,48'), 1)
old = "        add a,8\n        ld (v_cx),a\n        ld a,(m_cy)"
assert old in t
t = t.replace(old, "        add a,12                        ; (the card starts four pixels into its block)\n        ld (v_cx),a\n        ld a,(m_cy)", 1)
t = t.replace("x = 8 + 48 cx, y = 8 + 48 cy", "x = 12 + 48 cx, y = 8 + 48 cy", 1)
t = t.replace("5 x 4 cards of 40 x 40 pixels (5 x 5 characters) with a gap of one character: card (cx, cy) has its top left\n; character at column 1 + 6 cx, row 1 + 6 cy; row 0 is the header.  The cards are in MEMDATA (tools/memory_cards.py): 13 per variant (12 photos, the back), 400 bytes each:\n; 5 rows of 40 pattern bytes, 5 rows of 40 colour bytes.",
              "5 x 4 cards of 40 x 40 pixels in blocks of 6 x 5 characters (a black margin of 4 pixels at both sides): the block of card (cx, cy) has its top left\n; character at column 1 + 6 cx, row 1 + 6 cy; row 0 is the header.  The cards are in the bank MEMD (tools/memory_cards.py): 13 per variant (12 photos, the back), 480 bytes each:\n; 5 rows of 48 pattern bytes, 5 rows of 48 colour bytes.", 1)
open(p, 'w').write(t)

# ---- memory.asm (mem_jobs)
p = os.path.join(G, 'memory.asm'); t = open(p).read()
assert 'ld hl,MEMB\n        ld (q_bank),hl' in t
t = t.replace('ld hl,MEMB\n        ld (q_bank),hl', 'ld hl,MEMD\n        ld (q_bank),hl', 1)
t = t.replace("        ld b,40                         ; the patterns: 5 rows of 40 bytes", "        ld b,48                         ; the patterns: 5 rows of 48 bytes", 1)
t = t.replace("        ld bc,200\n        add hl,bc                       ; the colours: 200 bytes further", "        ld bc,240\n        add hl,bc                       ; the colours: 240 bytes further", 1)
t = t.replace("        ld b,40\n        ld c,5\n        call jq_put\n        pop hl\n        pop bc\n        djnz .e", "        ld b,48\n        ld c,5\n        call jq_put\n        pop hl\n        pop bc\n        djnz .e", 1)
assert t.count('ld b,48') == 2, t.count('ld b,48')
open(p, 'w').write(t)

# ---- build_game.py
p = os.path.join(HERE, 'build_game.py'); t = open(p).read()
old = "    MEMB = len(banks) + (sum(nb) if ascii16 else 0)"
assert old in t
t = t.replace("    open(os.path.join(PROJ, 'game', 'memdata.bin'), 'wb').write(mc['data'])\n", "    open(os.path.join(PROJ, 'game', 'memdata.bin'), 'wb').write(mc['data'])\n    cardbank = pad(mc['cards'])                                                  # the cards of the memory game: their own bank (MEMD = MEMB + 1)\n", 1)
t = t.replace("    assert MEMB < PLR_BANK - 1, MEMB\n", "    assert MEMB + 1 < PLR_BANK - 1, MEMB\n", 1)
t = t.replace("'MEMB equ %d\nMEMPAL equ %d\nCHTH0 equ %d\nCHOICEPAL equ %d\n' % (MEMB, MEMPAL, CHTH0, CHOICEPAL)", "'MEMB equ %d\nMEMD equ %d\nMEMPAL equ %d\nCHTH0 equ %d\nCHOICEPAL equ %d\n' % (MEMB, MEMB + 1, MEMPAL, CHTH0, CHOICEPAL)", 1)
t = t.replace("        f.write(membank)                # the memory game (MEMB = the first free bank)\n        f.write(bytes([0xFF]) * 16384 * (PLR_BANK - 2 - len(banks) - (sum(nb) if ascii16 else 0)))",
              "        f.write(membank)                # the memory game (MEMB = the first free bank)\n        f.write(cardbank)               # its cards (MEMD = MEMB + 1)\n        f.write(bytes([0xFF]) * 16384 * (PLR_BANK - 3 - len(banks) - (sum(nb) if ascii16 else 0)))", 1)
assert 'MEMD equ' in t and 'f.write(cardbank)' in t and 'PLR_BANK - 3 -' in t and "cardbank = pad" in t
open(p, 'w').write(t)
print('patched')
