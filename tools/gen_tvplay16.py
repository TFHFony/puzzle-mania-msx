"""Generates game/tvplay16.inc: the player of the title video for an SCC (tools/title_video.py --scc16): video and 16 kHz music in one stream.
Every iteration takes 446 cycles and outputs TWO samples, 223 cycles apart (like the SCC player of the game, game/slots_scc16.inc); the VDP bytes (outi) of an iteration
are spread over both halves: 5 before the second sample, 3 after it (the counter trick of tvplay.inc stays: B counts the outi back to 0 after 32 iterations of 8).
A row of the picture = an address iteration (no video bytes, writes the VRAM address) + 32 iterations of 8 bytes, for the pattern row and for the colour row, then an
end-of-row iteration.  A frame = H1 (SPACE?), H2 (joystick fire?), 24 rows, F1 + F2 (the next bank).
Stream (title_video.build16): per iteration 2 sample bytes (signed) and, for the video iterations, 8 VDP bytes.
Registers: HL stream, C = 98h, B counter, IXL / IYL = port A8h value for page 2 = the SCC / our cartridge, IYH / IXH = VRAM address (high byte | 40h) of the pattern /
colour row, D = the second sample, E = the first sample (E is free after the first write).
The burns (cycles) of every half are in tools/tvplay16.json (measured in openMSX: tools/tune_tv16.py)."""
import os, json, re
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
CFG = os.path.join(HERE, 'tvplay16.json')
HALF = 223


EXTRA = {5: '        nop', 8: '        ld a,0', 10: '        neg', 11: '        ld a,r', 13: '        jr $+2'}     # cycles of the instructions of a burn (MSX: +1 per opcode fetch, +1 per I/O)


def _combo(rem):
    """the fewest instructions of EXTRA that make rem cycles (None: impossible)"""
    best = [None] * (rem + 1)
    best[0] = []
    for v in range(1, rem + 1):
        for c in EXTRA:
            if v >= c and best[v - c] is not None and (best[v] is None or len(best[v - c]) + 1 < len(best[v])):
                best[v] = best[v - c] + [c]
    return best[rem]


def burn_ext(n, lab):
    for k in range(n // 18, -1, -1):
        base = 18 * k + 3 if k else 0
        if n - base < 0:
            continue
        cs = _combo(n - base)
        if cs is not None:
            out = []
            if k:
                out += ['        ld e,%d' % k, '.b%s: dec e' % lab, '        jr nz,.b%s' % lab]
            return out + [EXTRA[c] for c in sorted(cs)]
    return None


def burn(n, lab):
    """asm lines that take about n cycles (E is free): loops of 18k+3 (ld e,k / dec e / jr nz), nops (5), ld a,r (11)"""
    n = int(round(n))
    if n <= 0:
        return []
    best = None
    for k in range(n // 18, -1, -1):
        base = 18 * k + 3 if k else 0
        rem = n - base
        if rem < 0:
            continue
        for b in range(0, rem // 11 + 1):
            if (rem - 11 * b) % 5 == 0:
                cand = (k, (rem - 11 * b) // 5, b)
                if best is None or sum(cand[1:]) < sum(best[1:]):
                    best = cand
        if best:
            break
    if not best:                                  # not exact with nop / ld a,r: the extra instructions (A and the flags are free in a burn)
        ex = burn_ext(n, lab)
        if ex is not None:
            return ex
        return burn(n - 1, lab) if n > 1 else []            # (1..4 cycles cannot be made: the nearest below)
    k, a, b = best
    out = []
    if k:
        out += ['        ld e,%d' % k, '.b%s: dec e' % lab, '        jr nz,.b%s' % lab]
    out += ['        nop'] * a + ['        ld a,r'] * b
    return out


FETCH = ['        ld a,(hl)', '        inc hl', '        ld e,a', '        ld d,(hl)', '        inc hl']
SWSCC = ['        ld a,ixl', '        out (0xA8),a']
SWCART = ['        ld a,iyl', '        out (0xA8),a']
WRA = ['        ld a,e', '        ld (0x9800),a', '        ld (0x9880),a']
WRB = ['        ld a,d', '        ld (0x9800),a', '        ld (0x9880),a']
OUT5 = ['        outi', '        ld a,r', '        outi', '        ld a,r', '        outi', '        ld a,r', '        outi', '        ld a,r', '        outi']
OUT3 = ['        outi', '        ld a,r', '        outi', '        ld a,r', '        outi']


def load_cfg():
    d = {}
    if os.path.exists(CFG):
        d = json.load(open(CFG))
    return d


def representable(limit=400):
    """the cycle counts that burn() makes exactly: 0, or 18k+3 (k >= 0, k = 0: nothing) + 5a + 11b"""
    out = {0}
    for k in range(0, limit // 18 + 1):
        base = 18 * k + 3 if k else 0
        for v in range(0, limit - base + 1):
            if _combo(v) is not None:
                out.add(base + v)
    return out


def wait_cfg(cfg):
    """the burns of a machine with a VDP wait state: np / nc (the 8 outi iterations) shorter by 5 (first half) and 3 (second half), the sum kept exact where it can be"""
    R = representable()
    c2 = dict(cfg)
    for k, (d1, d2) in (('np', (5, 3)), ('nc', (5, 3)), ('ap', (2, 0)), ('ac', (2, 0))):       # the VDP writes of the halves: 5 + 3 outi, 2 out (0x99) (address iterations)
        a1 = max(r for r in R if r <= int(round(cfg[k + '1'])))
        a2 = max(r for r in R if r <= int(round(cfg[k + '2'])))
        t1, t2 = a1 - d1, a2 - d2
        best = None
        for tot in (t1 + t2, t1 + t2 - 1):
            for r1 in sorted(R):
                r2 = tot - r1
                if r2 in R and (best is None or abs(r1 - t1) < best[0]):
                    best = (abs(r1 - t1), r1, r2)
            if best:
                break
        assert best, (k, t1, t2)
        c2[k + '1'], c2[k + '2'] = float(best[1]), float(best[2])
        print('%s: burns %d / %d -> %d / %d (wanted %d / %d)' % (k, a1, a2, best[1], best[2], t1, t2))
    return c2


def main(wait=False, pfx='', outname='tvplay16.inc'):
    cfg = load_cfg()
    if wait:
        cfg = wait_cfg(cfg)
    n = [0]

    def b(kind, half, default=20.0):
        n[0] += 1
        return burn(cfg.get('%s%d' % (kind, half), default), '%d' % n[0])

    L = ['; GENERATED by tools/gen_tvplay16.py - do not edit.', 'tvplay16:']
    L += ['        ld c,0x98', '        ld b,0', '        ld a,(scc_pg)', '        ld ixl,a', '        ld a,(cart_pg)', '        ld iyl,a',
          '        xor a', '        ld (tv_f),a', '        ld hl,TVBANK16', '        ld a,l', '        ld (0x7000),a', '        ld a,h', '        BANKHI 0x7001',
          '        ld hl,0x8000', '        ld iyh,0x40', '        ld ixh,0x60']

    def it(kind, label, work1, work2, tail, burn1_where='after', pre_work2=None, end_burn=True):
        """one iteration.  work1: lines after the first sample (before the burn), work2: lines after the second sample"""
        L.append('%s:' % label)
        L.extend(FETCH + SWSCC + WRA + SWCART)
        L.append('.ma:')
        L.extend(work1[0])
        L.extend(b(kind, 1))
        L.extend(work1[1])
        L.extend(SWSCC + WRB + SWCART)
        L.append('.mb:')
        L.extend(work2[0])
        L.extend(b(kind, 2))
        L.extend(work2[1])
        L.extend(tail)

    space = ['        in a,(0xAA)', '        and 0xF0', '        or 8', '        out (0xAA),a', '        in a,(0xA9)', '        bit 0,a', '        jp z,tv16_exit']
    joy = ['        ld a,15', '        out (0xA0),a', '        in a,(0xA2)', '        and 0xBF', '        out (0xA1),a', '        ld a,14', '        out (0xA0),a',
           '        in a,(0xA2)', '        bit 4,a', '        jp z,tv16_exit']
    it('h1', 't16_h1', ([], space), ([], []), [])
    it('h2', 't16_h2', ([], joy), ([], []), [])
    L.append('tv16_row:')
    for tab, reg in (('p', 'iyh'), ('c', 'ixh')):
        it('a' + tab, 't16_a%s' % tab, (['        xor a', '        out (0x99),a', '        ld a,%s' % reg, '        out (0x99),a'], []), ([], []), [])
        L.append('t16_n%s:' % tab)
        L.append('.n%s:' % tab)
        L.extend(FETCH + SWSCC + WRA + SWCART)
        L.append('.ma:')
        L.extend(b('n' + tab, 1))
        L.extend(OUT5)
        L.extend(SWSCC + WRB + SWCART)
        L.append('.mb:')
        L.extend(b('n' + tab, 2))
        L.extend(OUT3)
        L.append('        jp nz,.n%s' % tab)
        L.append('        ld a,r                          ; (the loop path has a jp: the same time)')
    # the end of the row: next row addresses; the last row: the end of the frame
    L.append('t16_e:')
    L.extend(FETCH + SWSCC + WRA + SWCART)
    L.append('.ma:')
    L.extend(['        inc iyh', '        inc ixh'])
    L.extend(b('e', 1))
    L.extend(SWSCC + WRB + SWCART)
    L.append('.mb:')
    L.extend(['        ld a,iyh', '        cp 0x58'])
    L.extend(['        jp z,t16_f1'])
    L.extend(b('e', 2))
    L.append('        jp tv16_row')
    # F1: the frame counter, F2: the next bank
    L.append('t16_f1:')
    L.extend(b('e', 2))                       # (the same burn as the row end that did not jump: the same time)
    L.append('        jp t16_f1a                      ; (the same time as the jp tv16_row of the other path)')
    L.append('t16_f1a:')
    L.extend(FETCH + SWSCC + WRA + SWCART)
    L.append('.ma:')
    L.extend(['        ld a,(tv_f)', '        inc a', '        cp TVFRAMES16', '        jp nc,tv16_exit', '        ld (tv_f),a', '        ld iyh,0x40', '        ld ixh,0x60', '        ld b,0'])
    L.extend(b('f1', 1))
    L.extend(SWSCC + WRB + SWCART)
    L.append('.mb:')
    L.extend(b('f1', 2))
    L.append('t16_f2:')
    L.extend(FETCH + SWSCC + WRA + SWCART)
    L.append('.ma:')
    L.extend(b('f2', 1))
    L.extend(SWSCC + WRB + SWCART)
    L.append('.mb:')
    L.extend(['        ld a,(tv_f)', '        ld l,a', '        ld h,0', '        ld bc,TVBANK16', '        add hl,bc', '        ld a,l', '        ld (0x7000),a', '        ld a,h',
              '        BANKHI 0x7001', '        ld hl,0x8000', '        ld bc,0x0098'])
    L.extend(b('f2', 2))
    L.append('        jp t16_h1')
    L.append('tv16_exit:')
    L.extend(['        ld a,(cart_pg)', '        out (0xA8),a', '        ret'])
    txt = '\n'.join(L) + '\n'
    if pfx:
        txt = re.sub(r'\b(tvplay16|tv16_exit|tv16_row|t16_[a-z0-9]+)\b', pfx + r'\1', txt)
    open(os.path.join(PROJ, 'game', outname), 'w').write(txt)
    print(outname, len(L), 'lines')


if __name__ == '__main__':
    import sys
    if '--wait' in sys.argv:                  # game/tvplay16w.inc: the loop for a machine with a VDP wait state
        main(True, 'w_', 'tvplay16w.inc')
    else:
        main()
