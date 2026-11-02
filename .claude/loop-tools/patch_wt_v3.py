"""v2d -> v3 of build_waittest.py: the measurement had no chance on the turbo R: (1) the F flag of the status register is lost now and then (a run is off by whole frames), the
fix: on MSX2 and later the level of the VR bit of status register 2 is the blanking (reading it clears nothing); (2) the median of the 16 runs instead of the sum (an outlier
does not matter); (3) shorter runs (0.25 frame: a machine with 3 x the cycles per item must still end inside one frame); (4) a warm-up before the first test."""
p = r'F:\MSX Projects\PMdev26\.claude\loop-tools\build_waittest.py'
s = open(p).read()
NL = chr(10)
assert 'tvwait_v' not in s


def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)


rep("TARGET = 0.6 * 71364", "TARGET = 0.25 * 71364")
rep("'CYCLE 8 BANKS LDIR64': (3, 6, 0), 'SAME BANK LDIR 64': (3, 6, 0)}", "'CYCLE 8 BANKS LDIR64': (2, 4, 0), 'SAME BANK LDIR 64': (2, 4, 0)}")
rep("msx2    equ 0xC00C", "msx2    equ 0xC00C" + NL + "vwa     equ 0xC0B0                      ; the routine that waits for a blanking / counts the polls to the next one (F flag or VR level)" + NL + "vca     equ 0xC0B2" + NL +
    "nv      equ 0xC0C0                      ; the 16 values N of a measurement" + NL + "np      equ 0xC0E0")
rep("tvwait: in a,(0x99)" + NL + ".w:     in a,(0x99)" + NL + "        rlca" + NL + "        jr nc,.w" + NL + "        ret" + NL + "count:  ld bc,0" + NL + ".l:     in a,(0x99)" + NL + "        inc bc" + NL + "        rlca" + NL + "        jr nc,.l" + NL + "        ret" + NL,
    "tvwait: ld hl,(vwa)" + NL + "        jp (hl)" + NL + "count:  ld hl,(vca)" + NL + "        jp (hl)" + NL +
    "tvwait_f: in a,(0x99)" + NL + ".w:     in a,(0x99)" + NL + "        rlca" + NL + "        jr nc,.w" + NL + "        ret" + NL +
    "count_f: ld bc,0" + NL + ".l:     in a,(0x99)" + NL + "        inc bc" + NL + "        rlca" + NL + "        jr nc,.l" + NL + "        ret" + NL +
    "tvwait_v:                              ; MSX2 and later: status register 2, bit 6 = VR (the blanking is a level: no flag that can be lost)" + NL +
    ".a:     in a,(0x99)" + NL + "        and 0x40" + NL + "        jr nz,.a" + NL + ".b:     in a,(0x99)" + NL + "        and 0x40" + NL + "        jr z,.b" + NL + "        ret" + NL +
    "count_v: ld bc,0" + NL + ".a:     in a,(0x99)" + NL + "        inc bc" + NL + "        and 0x40" + NL + "        jr nz,.a" + NL + ".b:     in a,(0x99)" + NL + "        inc bc" + NL + "        and 0x40" + NL + "        jr z,.b" + NL + "        ret" + NL)
# init: choose the routines, select status register 2 on MSX2 and later
rep("        ld a,(msx2)" + NL + "        or a" + NL + "        jr z,again" + NL + "        ld a,(0xFFE8)",
    "        ld hl,tvwait_f" + NL + "        ld (vwa),hl" + NL + "        ld hl,count_f" + NL + "        ld (vca),hl" + NL + "        ld a,(msx2)" + NL + "        or a" + NL + "        jr z,again" + NL +
    "        ld hl,tvwait_v" + NL + "        ld (vwa),hl" + NL + "        ld hl,count_v" + NL + "        ld (vca),hl" + NL + "        ld a,(0xFFE8)")
rep("        ld a,0x89" + NL + "        out (0x99),a" + NL + "again:", "        ld a,0x89" + NL + "        out (0x99),a" + NL + "        ld a,2                          ; status register 2" + NL + "        out (0x99),a" + NL + "        ld a,0x8F" + NL + "        out (0x99),a" + NL + "again:")
# warm-up + the median
rep("run_all:                                ; every test: L1 and L2" + NL + "        xor a" + NL + "        ld (tn),a" + NL + "        inc a" + NL + "        ld (firsts),a" + NL,
    "run_all:                                ; every test: L1 and L2" + NL + "        xor a" + NL + "        ld (tn),a" + NL + "        ld (firsts),a" + NL + "        call setup                      ; a warm-up run of the first test (the cartridge and the VDP settle)" + NL +
    "        ld hl,(tl1)" + NL + "        call meas" + NL + "        ld a,1" + NL + "        ld (firsts),a" + NL)
i0 = s.index("meas:   ld (ml),hl")
i1 = s.index("vset:   ld a,e")
new_meas = '''meas:   ld (ml),hl                      ; HL = L: DE = 8 * the sum of the two middle values of the 16 values N (the median)
        ld a,16
        ld (mr),a
        ld hl,nv
        ld (np),hl
        call tvwait
.r:     ld de,(ml)
        ld hl,(runad)
        call jphl
        in a,(0x99)
        call count
        ld hl,(np)
        ld (hl),c
        inc hl
        ld (hl),b
        inc hl
        ld (np),hl
        ld a,(firsts)
        or a
        jr z,.ns
        ld a,(mr)                       ; the first 8 runs of the first test are kept
        neg
        add a,16
        cp 8
        jr nc,.ns
        ld l,a
        ld h,0
        add hl,hl
        ld de,fn
        add hl,de
        ld (hl),c
        inc hl
        ld (hl),b
.ns:    ld a,(mr)
        dec a
        ld (mr),a
        jr nz,.r
        ld c,15                         ; sort the 16 values
.po:    ld ix,nv
        ld b,15
.pi:    ld l,(ix+0)
        ld h,(ix+1)
        ld e,(ix+2)
        ld d,(ix+3)
        or a
        sbc hl,de
        jr c,.sk
        jr z,.sk
        ld l,(ix+0)
        ld h,(ix+1)
        ld (ix+0),e
        ld (ix+1),d
        ld (ix+2),l
        ld (ix+3),h
.sk:    inc ix
        inc ix
        djnz .pi
        dec c
        jr nz,.po
        ld hl,(nv+14)
        ld de,(nv+16)
        add hl,de
        add hl,hl
        add hl,hl
        add hl,hl
        ex de,hl
        ret

'''
s = s[:i0] + new_meas + s[i1:]
rep("RUNNING THE TESTS ... (ABOUT 15 S)", "RUNNING THE TESTS ... (ABOUT 20 S)")
open(p, 'w').write(s)
print('patched v3')
