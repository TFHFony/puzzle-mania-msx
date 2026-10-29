"""one-time patch: anykey, selchk, getkey, keyedge read what the slots of the player derived (mus_any, mus_sel, mus_dkey, mus_ke); without music the old code runs"""
P = 'F:/MSX Projects/PMdev26/game/'


def edit(fn, pairs):
    s = open(P + fn, encoding='utf8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (fn, a)
        s = s.replace(a, b)
    open(P + fn, 'w', encoding='utf8').write(s)


edit('extra.asm', [("""anykey:                                 ; NZ = a key that the game uses, or the joystick, is down
        ld a,(k8)
""", """anykey:                                 ; NZ = a key that the game uses, or the joystick, is down
        ld a,(mus_on)                   ; (with music the slots of the player have done this: mus_any)
        or a
        jr z,.slow
        ld a,(mus_any)
        or a
        ret
.slow:  ld a,(k8)
""")])

edit('spec.asm', [("""selchk:                                 ; SELECT (row 7 bit 6): once per press
        ld a,(k7)
""", """selchk:                                 ; SELECT (row 7 bit 6): once per press
        ld a,(mus_on)                   ; (with music the slots of the player look at it: mus_sel, latched)
        or a
        jr z,.slow
        ld a,(mus_sel)
        or a
        ret z
        xor a
        ld (mus_sel),a
        jp hz_toggle
.slow:  ld a,(k7)
""")])

edit('core.asm', [("""getkey: call getdir
        ld b,a
""", """getkey: ld a,(mus_on)                   ; (with music the slots of the player have done this: mus_dkey)
        or a
        jr z,.slow
        ld a,(mus_dkey)
        ret
.slow:  call getdir
        ld b,a
"""), ("""keyedge:                                ; A = keys that went down since the last call: bit 0 L, bit 1 C, bit 2 T
        ld c,0
""", """keyedge:                                ; A = keys that went down since the last call: bit 0 L, bit 1 C, bit 2 T
        ld a,(mus_on)                   ; (with music the slots of the player collect them: mus_ke, latched)
        or a
        jr z,.slow
        ld a,(mus_ke)
        ld b,a
        xor a
        ld (mus_ke),a
        ld a,b
        ret
.slow:  ld c,0
""")])
e = open(P + 'wtequ.inc', encoding='utf8').read()
e = e.replace('WT_RAM  equ 0xE600', 'WT_RAM  equ 0xEB00').replace('WT_VARS equ 0xE800', 'WT_VARS equ 0xED00')
open(P + 'wtequ.inc', 'w', encoding='utf8').write(e)
print('ok')
