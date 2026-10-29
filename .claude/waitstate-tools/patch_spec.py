"""one-time patch: specs screen (game/spec.asm): WAIT STATE line under VIDEO CHIP (C toggles), no CARTRIDGE SLOT line, SELECT works"""
import os
fn = 'F:/MSX Projects/PMdev26/game/spec.asm'
s = open(fn, encoding='utf8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a)
    s = s.replace(a, b)


rep("""        ld a,0x20
        ld (pk_prev),a
spec_screen:""", """        ld a,0x20
        ld (pk_prev),a
        ld a,1
        ld (ck_prev),a
spec_screen:""")
rep("""        ld b,8                          ; the sound chip
        ld hl,sp_l3
        call .lab""", """        ld b,8                          ; the wait state of the VDP: the loop of the title video, 446 or 438 cycles (the test at the start, C toggles)
        ld hl,sp_l9
        call .lab
        ld hl,sp_446
        ld a,(v_tvd)
        or a
        jr z,.wt
        ld hl,sp_438
.wt:    ld b,8
        call .val
        ld b,10                         ; the sound chip
        ld hl,sp_l3
        call .lab""")
rep("""        ld b,8
        call .val
        ld b,10                         ; the refresh rate
        ld hl,sp_l4
        call .lab""", """        ld b,10
        call .val
        ld b,12                         ; the refresh rate
        ld hl,sp_l4
        call .lab""")
rep("""        ld b,12                         ; the palette: MSX2""", """        ld b,14                         ; the palette: MSX2""")
rep(""".pv:    ld b,12
        jp .val
""", """.pv:    ld b,14
        jp .val
""")
rep(""".hz:    ld b,10
        call .val
.nosel: ld b,14                         ; the slot of the cartridge
        ld hl,sp_l5
        call .lab
        ld a,(v_own)
        call .slot
        ld b,14
        call .valbuf
        ld b,16                         ; the slot of the SCC""", """.hz:    ld b,12
        call .val
        ld b,16                         ; the slot of the SCC""")
rep('sp_l5:  db "CARTRIDGE SLOT:",0\n', 'sp_l9:  db "WAIT STATE:",0\nsp_446: db "446 (C)",0\nsp_438: db "438 (C)",0\n')
rep(""".w:     call vsync
        IF MSX2PAL
        call palkey
        jp c,spec_screen                ; FORCE MSX1 changed: the whole screen again
        ENDIF
""", """.w:     call vsync
        IF MSX2PAL
        call palkey
        jp c,spec_screen                ; FORCE MSX1 changed: the whole screen again
        ENDIF
        call ckey
        jp c,spec_screen                ; the title video loop changed
        call selkey
        jp c,spec_screen                ; 50 / 60 Hz changed
""")
rep("""        IF MSX2PAL
palkey:""", """ckey:                                   ; C (row 3 bit 0), once per press: the title video loop 446 <-> 438 cycles (C = changed)
        ld a,3
        call row
        and 1
        ld b,a
        ld a,(ck_prev)
        ld c,a
        ld a,b
        ld (ck_prev),a
        or a
        ret nz
        ld a,c
        or a
        ret z
        ld a,(v_tvd)
        xor 1
        ld (v_tvd),a
        scf
        ret

selkey:                                 ; SELECT (row 7 bit 6), once per press: 50 / 60 Hz (an MSX2 or later; C = pressed)
        ld a,7
        call row
        and 0x40
        ld b,a
        ld a,(sel_prev)
        ld c,a
        ld a,b
        ld (sel_prev),a
        or a
        ret nz
        ld a,c
        or a
        ret z
        call hz_toggle
        scf
        ret

        IF MSX2PAL
palkey:""")
open(fn, 'w', encoding='utf8').write(s)
print('ok')
