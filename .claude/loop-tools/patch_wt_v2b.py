"""part 2 of the patch (v1 -> v2): the arithmetic and the computed page of the wait test ROM"""
p = r'F:\MSX Projects\PMdev26\.claude\loop-tools\build_waittest.py'
s = open(p).read()
assert 'compute_all:' not in s
new_code = r'''
; ---- the arithmetic: cycles of a loop = 71364 * (S1 - S2) / (16 * cf * dL), with two decimals; the difference with the reference per item
zero16: ld (ix+0),0
        ld (ix+1),0
        ld (ix+2),0
        ld (ix+3),0
        ld (ix+4),0
        ld (ix+5),0
        ld (ix+6),0
        ld (ix+7),0
        ld (ix+8),0
        ld (ix+9),0
        ld (ix+10),0
        ld (ix+11),0
        ld (ix+12),0
        ld (ix+13),0
        ld (ix+14),0
        ld (ix+15),0
        ret
zero4:  ld (ix+0),0
        ld (ix+1),0
        ld (ix+2),0
        ld (ix+3),0
        ret

mul:    sla (ix+0)                      ; (ix+0..3) = HL * BC, D = 16 (the four bytes are 0 on entry)
        rl (ix+1)
        rl (ix+2)
        rl (ix+3)
        add hl,hl
        jr nc,.n
        ld a,(ix+0)
        add a,c
        ld (ix+0),a
        ld a,(ix+1)
        adc a,b
        ld (ix+1),a
        ld a,(ix+2)
        adc a,0
        ld (ix+2),a
        ld a,(ix+3)
        adc a,0
        ld (ix+3),a
.n:     dec d
        jr nz,mul
        ret

div32:  ld b,32                         ; N (0..3) / D (8..11): quotient in 0..3, remainder in 4..7 (the remainder starts at 0)
.l:     sla (ix+0)
        rl (ix+1)
        rl (ix+2)
        rl (ix+3)
        rl (ix+4)
        rl (ix+5)
        rl (ix+6)
        rl (ix+7)
        ld a,(ix+4)
        sub (ix+8)
        ld l,a
        ld a,(ix+5)
        sbc a,(ix+9)
        ld h,a
        ld a,(ix+6)
        sbc a,(ix+10)
        ld e,a
        ld a,(ix+7)
        sbc a,(ix+11)
        ld d,a
        jr c,.n
        ld (ix+4),l
        ld (ix+5),h
        ld (ix+6),e
        ld (ix+7),d
        inc (ix+0)
.n:     djnz .l
        ret

compute_all:
        xor a
        ld (tn),a
.t:     ld a,(tn)
        ld l,a                          ; ctab entry (8 bytes): dL, ref (2 words), shift
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        ld de,ctab
        add hl,de
        ld (cp),hl
        ld a,(tn)
        add a,a
        add a,a
        ld l,a
        ld h,0
        ld de,res
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld c,(hl)
        inc hl
        ld b,(hl)
        ex de,hl
        or a
        sbc hl,bc                       ; S1 - S2
        jr nc,.p
        ld hl,0
.p:     ld (ds),hl
        ld ix,dblk
        call zero16
        ld hl,(cf)                      ; divisor = 16 * cf * dL
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl
        ex de,hl
        ld hl,(cp)
        ld c,(hl)
        inc hl
        ld b,(hl)
        ex de,hl                        ; HL = 16 * cf (multiplier), BC = dL
        ld d,16
        call mul
        ld a,(ix+0)
        ld (ix+8),a
        ld a,(ix+1)
        ld (ix+9),a
        ld a,(ix+2)
        ld (ix+10),a
        ld a,(ix+3)
        ld (ix+11),a
        call zero4
        ld hl,(ds)                      ; numerator = (S1 - S2) * 71364 = * 5828 + * 65536
        ld bc,5828
        ld d,16
        call mul
        ld hl,(ds)
        ld a,(ix+2)
        add a,l
        ld (ix+2),a
        ld a,(ix+3)
        adc a,h
        ld (ix+3),a
        call div32
        ld l,(ix+0)
        ld h,(ix+1)
        ld (qv),hl
        ld a,(ix+4)                     ; fraction: remainder * 100 / divisor
        ld (ix+12),a
        ld a,(ix+5)
        ld (ix+13),a
        ld a,(ix+6)
        ld (ix+14),a
        ld a,(ix+7)
        ld (ix+15),a
        call zero4
        ld (ix+4),0
        ld (ix+5),0
        ld (ix+6),0
        ld (ix+7),0
        ld b,100
.m:     ld a,(ix+0)
        add a,(ix+12)
        ld (ix+0),a
        ld a,(ix+1)
        adc a,(ix+13)
        ld (ix+1),a
        ld a,(ix+2)
        adc a,(ix+14)
        ld (ix+2),a
        ld a,(ix+3)
        adc a,(ix+15)
        ld (ix+3),a
        djnz .m
        call div32
        ld a,(ix+0)
        ld (fr),a
        call zero4                      ; C * 100 = qv * 100 + fraction
        ld hl,(qv)
        ld bc,100
        ld d,16
        call mul
        ld a,(fr)
        add a,(ix+0)
        ld (ix+0),a
        ld a,(ix+1)
        adc a,0
        ld (ix+1),a
        ld a,(ix+2)
        adc a,0
        ld (ix+2),a
        ld a,(ix+3)
        adc a,0
        ld (ix+3),a
        ld hl,(cp)                      ; - the reference
        inc hl
        inc hl
        ld a,(ix+0)
        sub (hl)
        ld (ix+0),a
        inc hl
        ld a,(ix+1)
        sbc a,(hl)
        ld (ix+1),a
        inc hl
        ld a,(ix+2)
        sbc a,(hl)
        ld (ix+2),a
        inc hl
        ld a,(ix+3)
        sbc a,(hl)
        ld (ix+3),a
        inc hl
        ld b,(hl)                       ; / the number of items (a power of 2)
.s:     sra (ix+3)
        rr (ix+2)
        rr (ix+1)
        rr (ix+0)
        djnz .s
        ld c,0                          ; C = sign
        bit 7,(ix+3)
        jr z,.pos
        ld c,1
        ld a,(ix+0)
        cpl
        add a,1
        ld (ix+0),a
        ld a,(ix+1)
        cpl
        adc a,0
        ld (ix+1),a
        ld a,(ix+2)
        cpl
        adc a,0
        ld (ix+2),a
        ld a,(ix+3)
        cpl
        adc a,0
        ld (ix+3),a
.pos:   ld l,(ix+0)
        ld h,(ix+1)
        ld a,(ix+2)
        or (ix+3)
        jr nz,.big
        ld de,9999
        or a
        sbc hl,de
        add hl,de
        jr c,.ok
.big:   ld hl,9999
.ok:    push hl                         ; the result row: qv (2), fraction, sign, |difference|
        ld a,(tn)
        add a,a
        add a,a
        add a,a
        ld e,a
        ld d,0
        ld hl,cres
        add hl,de
        ld de,(qv)
        ld (hl),e
        inc hl
        ld (hl),d
        inc hl
        ld a,(fr)
        ld (hl),a
        inc hl
        ld (hl),c
        inc hl
        pop de
        ld (hl),e
        inc hl
        ld (hl),d
        ld a,(tn)
        inc a
        ld (tn),a
        cp NT
        jp nz,.t
        ret

p2d:    ld b,'0'                        ; A = 0..99: two digits
.t:     sub 10
        jr c,.d
        inc b
        jr .t
.d:     add a,10
        add a,'0'
        ld c,a
        ld a,b
        out (0x98),a
        ld a,c
        out (0x98),a
        ret

show0:  ld hl,s_title
        ld de,0
        call puts
        ld hl,s_cf
        ld de,40
        call puts
        ld hl,(cf)
        call pdec5
        ld hl,s_v
        call pstr
        ld a,(msx2)
        ld l,a
        ld h,0
        call pdec5
        ld hl,s_head0
        ld de,80
        call puts
        xor a
        ld (tn),a
.l:     ld a,(tn)
        add a,3
        ld l,a
        ld h,0
        ld d,h
        ld e,l
        add hl,hl
        add hl,hl
        add hl,de
        add hl,hl
        add hl,hl
        add hl,hl
        ex de,hl
        call vset
        ld a,(tn)
        add a,a
        ld l,a
        ld h,0
        ld de,ntab
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        ex de,hl
        call pstr
        ld a,(tn)
        add a,a
        add a,a
        add a,a
        ld l,a
        ld h,0
        ld de,cres
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld a,(hl)
        inc hl
        ld (fr),a
        ld a,(hl)
        inc hl
        ld (ds),a
        ld c,(hl)
        inc hl
        ld b,(hl)
        push bc
        ex de,hl
        call pdec5
        ld a,'.'
        out (0x98),a
        ld a,(fr)
        call p2d
        ld a,' '
        out (0x98),a
        ld b,'+'
        ld a,(ds)
        or a
        jr z,.sg
        ld b,'-'
.sg:    ld a,b
        out (0x98),a
        pop hl                          ; |difference| in hundredths
        ld de,100
        ld b,0
.dv:    or a
        sbc hl,de
        jr c,.dd
        inc b
        jr .dv
.dd:    add hl,de
        push hl
        ld a,b
        call p2d
        ld a,'.'
        out (0x98),a
        pop hl
        ld a,l
        call p2d
        ld a,(tn)
        inc a
        ld (tn),a
        cp NT
        jp nz,.l
        ret
'''
i = s.index('show2:')
s = s[:i] + new_code + '\n' + s[i:]
open(p, 'w').write(s)
print('part 2 ok')
