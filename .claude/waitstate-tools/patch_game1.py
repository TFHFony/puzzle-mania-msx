"""one-time patch: wtest.asm sync fix, equ.inc / pm.asm includes, screens.asm (selftest hook, title video loop choice)"""
import os
P = 'F:/MSX Projects/PMdev26'


def rw(p, f):
    fn = os.path.join(P, p)
    s = open(fn, encoding='utf8').read()
    s2 = f(s)
    assert s2 != s, p
    open(fn, 'w', encoding='utf8').write(s2)


def f_wt(s):
    old = """sync:   ld hl,fc                        ; wait for the next frame tick; C = interrupts do not come
        ld a,(hl)
        ld bc,0
.s:     cp (hl)
        ret nz
        dec bc
        ld a,b
        or c
        ld a,(fc)
        jr nz,.s
        scf
        ret
"""
    new = """sync:   ld hl,fc                        ; wait for the next frame tick; C = interrupts do not come
        ld a,(hl)
        ld bc,0
.s:     cp (hl)
        jr nz,.ok
        dec bc
        ld a,b
        or c
        ld a,(fc)
        jr nz,.s
        scf
        ret
.ok:    or a
        ret
"""
    assert old in s
    return s.replace(old, new)


rw('game/wtest.asm', f_wt)
rw('game/equ.inc', lambda s: s.replace('        INCLUDE "cfg.inc"\n', '        INCLUDE "cfg.inc"\n        INCLUDE "wtequ.inc"\n', 1))


def f_pm(s):
    a = '        INCLUDE "tvplay.inc"\n'
    assert s.count(a) == 1
    s = s.replace(a, a + '        INCLUDE "tvplay8.inc"            ; the same for a machine with a VDP wait state (v_tvd, wtest.asm)\n')
    b = '        INCLUDE "tvplay16.inc"\n'
    assert s.count(b) == 1
    return s.replace(b, b + '        INCLUDE "tvplay16w.inc"\n')


rw('game/pm.asm', f_pm)


def f_sc(s):
    old = """        cp 'B'
        ret z
.bad:   call clrscr"""
    assert old in s
    s = s.replace(old, """        cp 'B'
        jr nz,.bad
        jp wt_go                        ; the VDP wait state test (wtest.asm)
.bad:   call clrscr""")
    old2 = """        call scc_tvstart                ; an SCC: its own stream, 16 kHz (tvplay16.inc)
        call tvplay16
        call scc_off
        jp wait_release
.tvp:
        ENDIF
        call tvplay                     ; video and music in one stream (tvplay.inc)
        jp wait_release
"""
    assert old2 in s
    s = s.replace(old2, """        call scc_tvstart                ; an SCC: its own stream, 16 kHz (tvplay16.inc, w_tvplay16 for a machine with a VDP wait state)
        ld a,(v_tvd)
        or a
        jr nz,.t16w
        call tvplay16
        jr .t16e
.t16w:  call w_tvplay16
.t16e:  call scc_off
        jp wait_release
.tvp:
        ENDIF
        ld a,(v_tvd)                    ; video and music in one stream (tvplay.inc, tv8_tvplay: 8 cycles less per iteration for a VDP wait state)
        or a
        jr nz,.tvw
        call tvplay
        jp wait_release
.tvw:   call tv8_tvplay
        jp wait_release
""")
    old3 = "; ------------------------------------------------------------------------------------------------ wipes: full screen pictures"
    assert old3 in s
    s = s.replace(old3, """wt_go:                                  ; the VDP wait state test: out of the bank SELFTEST into the RAM, it runs there (wtest.asm; v_wait, v_tvd)
        ld hl,SELFTEST
        call setbank
        ld hl,0x8010
        ld de,WT_RAM
        ld bc,WT_LEN
        ldir
        ld hl,0
        call setbank
        jp WT_RAM

""" + old3, 1)
    return s


rw('game/screens.asm', f_sc)
print('ok')
