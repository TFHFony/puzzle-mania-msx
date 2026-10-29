"""one-time patch: no click when the PSG music stops (the PSG goes to the level of silence = the constant silent table set 4, not to 0), the menu is drawn before its music starts"""
import os
P = 'F:/MSX Projects/PMdev26/'


def edit(fn, pairs):
    s = open(P + fn, encoding='utf8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (fn, a)
        s = s.replace(a, b)
    open(P + fn, 'w', encoding='utf8').write(s)


edit('tools/gen_tvplay.py', [("""    L += ['        ld a,8', '        out (0xA0),a', '        xor a', '        out (0xA1),a', '        ld a,9', '        out (0xA0),a', '        xor a', '        out (0xA1),a',
          '        ld a,10', '        out (0xA0),a', '        xor a', '        out (0xA1),a', '        ret']
""", """    L += ['        ld a,8', '        out (0xA0),a', '        ld a,(TABHI*256+0xC00)', '        out (0xA1),a', '        ld a,9', '        out (0xA0),a', '        ld a,(TABHI*256+0xD00)', '        out (0xA1),a',
          '        ld a,10', '        out (0xA0),a', '        ld a,(TABHI*256+0xE00)', '        out (0xA1),a', '        ret']        # (the PSG stays at the level of silence: the first entries of the constant tables of gain step 4, no click)
""")])

edit('game/music.asm', [("""        dec a
        ld (mus_trk),a
        ld a,8
        out (0xA0),a
        xor a
        out (0xA1),a
        ld a,9
        out (0xA0),a
        xor a
        out (0xA1),a
        ld a,10
        out (0xA0),a
        xor a
        out (0xA1),a
        ret
""", """        dec a
        ld (mus_trk),a
        IF SCC
        ld a,(v_sccm)
        or a
        jr nz,.zero                     ; (the SCC plays the music: the PSG is idle)
        ENDIF
        ld a,8                          ; the PSG stays at the level of silence (the first entries of the constant tables of gain step 4): a step to volume 0 is a click
        out (0xA0),a
        ld a,(TABHI*256+0xC00)
        out (0xA1),a
        ld a,9
        out (0xA0),a
        ld a,(TABHI*256+0xD00)
        out (0xA1),a
        ld a,10
        out (0xA0),a
        ld a,(TABHI*256+0xE00)
        out (0xA1),a
        ret
        IF SCC
.zero:  ld a,8
        out (0xA0),a
        xor a
        out (0xA1),a
        ld a,9
        out (0xA0),a
        xor a
        out (0xA1),a
        ld a,10
        out (0xA0),a
        xor a
        out (0xA1),a
        ret
        ENDIF
""")])

edit('game/pm.asm', [("""        ld c,1
        call music_play                 ; menu music (carries on if it already plays)
        call draw_menu
        call menu_loop                  ; NC = photo chosen, C = ESC
""", """        ld a,(mus_on)                   ; the menu music plays already (back from the credits, the size menu, the puzzle): the menu is drawn over it
        or a
        jr z,.fresh
        ld a,(mus_trk)
        or a
        jr z,.cont
.fresh: ld c,1                          ; a new start: the player runs silent while the menu is drawn, then the music starts from its beginning
        call music_play
        ld a,4
        ld (mus_gt),a
        call draw_menu
        call music_stop
        ld c,1
        xor a
        call music_play                 ; (fades in)
        jr .mm
.cont:  ld c,1
        call music_play                 ; (carries on)
        call draw_menu
.mm:    call menu_loop                  ; NC = photo chosen, C = ESC
""")])
print('ok')
