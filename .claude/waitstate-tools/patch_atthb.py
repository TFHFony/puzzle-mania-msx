"""one-time patch: att_check (run in every idle frame of the menu) no longer does the 16-bit arithmetic of att_half: att_hb (= first bank of the second half of the song) is made once, in att_init"""
P = 'F:/MSX Projects/PMdev26/game/'
s = open(P + 'extra.asm', encoding='utf8').read()
a = """att_init:                               ; (the menu is entered: that counts as a key; the second half counts from the next one)
        ld a,1
"""
assert s.count(a) == 1
s = s.replace(a, """att_init:                               ; (the menu is entered: that counts as a key; the second half counts from the next one)
        ld hl,(mus_e)                   ; att_hb = the first bank of the second half of the song (att_check compares with it in every frame)
        ld de,(mus_s)
        or a
        sbc hl,de
        srl h
        rr l
        add hl,de
        ld (att_hb),hl
        ld a,1
""")
b = """att_check:                              ; every frame without a key: carry = the last 512 samples of the song and no key in its second half
        ld a,(mus_on)
        or a
        ret z
        call att_half
        jr c,.first
"""
assert s.count(b) == 1
s = s.replace(b, """att_check:                              ; every frame without a key: carry = the last 512 samples of the song and no key in its second half
        ld a,(mus_on)
        or a
        ret z
        ld hl,(mus_bank)                ; (the same as att_half, without its arithmetic: this runs in every idle frame, and the time counts as a gap of the music)
        ld de,(att_hb)
        or a
        sbc hl,de
        jr c,.first
""")
open(P + 'extra.asm', 'w', encoding='utf8').write(s)
e = open(P + 'wtequ.inc', encoding='utf8').read()
e += "att_hb  equ 0xC393      ; word: the first bank of the second half of the menu song (extra.asm att_init)\n"
open(P + 'wtequ.inc', 'w', encoding='utf8').write(e)
print('ok')
