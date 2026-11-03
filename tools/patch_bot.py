"""one-off patch (applied once): the memory bot remembers what it has seen, the win screen keeps the board, the attract mode goes on after the clip, the card of the choice screen has the size of the photo
 - game/memplay.asm: m_st bit 7 = seen; the bot turns a second card only if it has seen its partner (else a card nobody has seen)
 - game/puzzle2.asm: label win_go (the win without drawing the photo and the banner)
 - game/memory.asm: the board stays; att_on for the clip
 - tools/memory_cards.py: big_card with a black margin of two pixels (the edge cells hold black and blue only)"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(HERE, '..', 'game')

# ---- memplay.asm
p = os.path.join(G, 'memplay.asm')
t = open(p).read()
assert 'partner:' not in t
old = '        ld a,(hl)\n        or a\n        jr z,.turn\n        xor a                           ; (a card that is turned already)\n'
assert old in t
t = t.replace(old, '        ld a,(hl)\n        and 0x7F                        ; (bit 7: the card has been seen)\n        or a\n        jr z,.turn\n        xor a                           ; (a card that is turned already)\n', 1)
old = '.turn:  ld (hl),1\n'
assert old in t
t = t.replace(old, '.turn:  ld (hl),0x81                     ; face up, seen\n', 1)
old = '        ld (hl),0\n        ld d,12\n        jp qcard\n'
assert old in t
t = t.replace(old, '        ld (hl),0x80                    ; face down again, but it has been seen\n        ld d,12\n        jp qcard\n', 1)
a = t.index('.first: ld c,20')
b = t.index('.chosen:ld hl,m_ph')
new = '''.first: ld e,0                          ; a pair that has been seen (two cards face down, turned before, the same photo): turn one of them
.fp:    ld d,0
        ld hl,m_st
        add hl,de
        ld a,(hl)
        cp 0x80                         ; face down and seen
        jr nz,.fpn
        ld hl,m_pic
        add hl,de
        ld b,(hl)
        ld a,e
        push de
        call partner
        pop de
        jr c,.fpn
        ld a,e
        ld (m_tgt),a
        jr .chosen
.fpn:   inc e
        ld a,e
        cp 20
        jr nz,.fp
.unseen:ld c,20                         ; else a card that nobody has seen
        ld d,31
        call pick
        ld e,a
        ld d,0
        ld hl,m_st
        add hl,de
        ld a,(hl)
        or a
        jr nz,.unseen
        ld a,e
        ld (m_tgt),a
        jr .chosen
.second:ld a,(m_f1)                     ; has the partner of the first card been seen? then that one, else a card that nobody has seen
        ld e,a
        ld d,0
        ld hl,m_pic
        add hl,de
        ld b,(hl)
        ld a,e
        call partner
        jr c,.unseen
        ld (m_tgt),a
'''
t = t[:a] + new + t[b:]
marker = '; ---- the attract mode: a bot plays the memory game'
assert marker in t
partner = '''partner:ld c,a                          ; B = a photo, A = a place to leave out -> NC and A = the other place with that photo that is face down and has been seen, or carry
        ld e,0
.l:     ld a,e
        cp c
        jr z,.n
        ld d,0
        ld hl,m_st
        add hl,de
        ld a,(hl)
        cp 0x80
        jr nz,.n
        ld hl,m_pic
        add hl,de
        ld a,(hl)
        cp b
        jr nz,.n
        ld a,e
        or a
        ret
.n:     inc e
        ld a,e
        cp 20
        jr nz,.l
        scf
        ret

'''
t = t.replace(marker, partner + marker, 1)
t = t.replace('(it moves the cursor and presses SPACE like a player; three times of four it turns the right partner, else any card)', '(it moves the cursor and presses SPACE like a player and remembers what it has seen: a second card only when it has seen its partner)')
open(p, 'w').write(t)

# ---- puzzle2.asm: win_go
p = os.path.join(G, 'puzzle2.asm')
t = open(p).read()
old = '        call win_banner\n        call music_stop                 ; the jingle:'
assert old in t
t = t.replace(old, '        call win_banner\nwin_go:                                 ; (the memory game comes in here: its board stays on the screen)\n        call music_stop                 ; the jingle:', 1)
open(p, 'w').write(t)

# ---- memory.asm
p = os.path.join(G, 'memory.asm')
t = open(p).read()
a = t.index('        call music_stop                 ; won: the photo of the last pair')
b = t.index('        or a\n        ret\n.out:')
new = '''        ld a,(m_last)                   ; won: the board stays (all the cards are up), the jingle, the confetti over it, then the video of the last pair
        ld (v_photo),a
        call job_flush                  ; (the last card is drawn)
        ld a,(m_att)
        ld (att_on),a                   ; the attract mode: the clip plays once and it goes on
        call win_go
        xor a
        ld (att_on),a
        ret
.out:'''
t = t[:a] + new + t[b + len('        or a\n        ret\n.out:'):]
open(p, 'w').write(t)

# ---- memory_cards.py: the card of the choice screen
p = os.path.join(HERE, 'memory_cards.py')
t = open(p).read()
a = t.index('def big_card(blue):')
b = t.index('def card_bytes(pat, col):')
new = '''def big_card(blue):
    """the card of the memory game on the choice screen (104 x 80 pixels = 13 x 10 characters, 2080 bytes), as big as the photo next to it (100 x 76 with a black margin of two pixels):
    a blue card with a white frame and a white question mark; the characters at the edge hold black and blue only, the others blue and white"""
    import build_game as B
    im = Image.new('L', (BIGW, BIGH), 0)
    d = ImageDraw.Draw(im)
    d.rectangle([8, 8, BIGW - 9, BIGH - 9], outline=255, width=3)
    f = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 58)
    x0, y0, x1, y1 = d.textbbox((0, 0), '?', font=f)
    d.text(((BIGW - (x1 - x0)) // 2 - x0, (BIGH - (y1 - y0)) // 2 - y0), '?', font=f, fill=255)
    white = np.asarray(im) >= 128
    card = np.zeros((BIGH, BIGW), bool)
    card[2:BIGH - 2, 2:BIGW - 2] = True                      # the blue card (100 x 76)
    pat = np.zeros((BIGH, BIGW // 8), np.uint8)
    col = np.zeros((BIGH, BIGW // 8), np.uint8)
    for y in range(BIGH):
        for cx in range(BIGW // 8):
            sl = slice(cx * 8, cx * 8 + 8)
            w, c = white[y, sl] & card[y, sl], card[y, sl]
            if w.any():                                      # white on blue (a white pixel can sit in a character at the edge only inside the card)
                assert c.all(), (y, cx)
                fg, bg, bits = WHITE, blue, w
            elif c.all():
                fg, bg, bits = blue, blue, np.zeros(8, bool)
            elif c.any():                                    # the edge: blue on black
                fg, bg, bits = blue, 1, c
            else:
                fg, bg, bits = 1, 1, np.zeros(8, bool)
            pat[y, cx] = int(sum(1 << (7 - i) for i in range(8) if bits[i]))
            col[y, cx] = (fg << 4) | bg
    return B.chars(pat) + B.chars(col)


'''
t = t[:a] + new + t[b:]
open(p, 'w').write(t)
print('patched')
