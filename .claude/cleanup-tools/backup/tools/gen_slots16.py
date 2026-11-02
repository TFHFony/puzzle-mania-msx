"""The player block for the SCC at 16 kHz (game/slots_scc16.inc), called by gen_slots.py --scc16.
Every iteration of the loop (446 cycles, like the PSG player) outputs TWO samples, 223 cycles apart: both data bytes are fetched first (page 2 = our cartridge),
then page 2 is switched to the SCC slot (port A8h), sample A is written (wave entry 0 of channel 1, then the frequency register: the wave restarts), the work of the
iteration (the VDP job engine, or the task of a slot) runs, sample B is written 223 cycles after A, page 2 goes back to our cartridge.
The work of the iteration sits between the two samples (the first half: 223 cycles) and after the second one (the second half); the burns that make both halves
exactly 223 cycles are in tools/scc16.json (cycles; written by tools/tune_scc16.py, measured in openMSX).
The job engine and the tasks of the slots are the same as in the PSG player (gen_slots.py); the sample clock has no fraction here (an integer number of cycles)."""
import os, re, json
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
CFG = os.path.join(HERE, 'scc16.json')
MIN_B = 0.0                                     # IBURN 0,0: nothing


def load_cfg():
    d = {'split': {}, 'b1': {}, 'b2': {}, 'loop': {'C': 40.0, 'H1': 60.0, 'H2': 40.0, 'I': 90.0, 'P': 48.0}}
    if os.path.exists(CFG):
        d.update(json.load(open(CFG)))
    return d


def bn(cycles, per=23, base=8, minb=0):
    """(B, N) for a burn of about `cycles` cycles: B rounds of `per` cycles + base (IBURN: a loop on IYL), N nops of 5 cycles; B = 0: only the nops"""
    best = None
    for B in range(minb, 60):
        for N in range(0, 12):
            c = (per * B + base if B else 0) + 5 * N
            e = abs(c - cycles)
            if best is None or e < best[0] or (e == best[0] and N < best[2]):
                best = (e, B, N)
    return best[1], best[2]


MACROS = """        MACRO IFETCH                    ; the two samples of the iteration (page 2 = our cartridge): E = first, D = second
        ld a,(hl)
        inc hl
        ld e,a
        ld d,(hl)
        inc hl
        ENDM
        MACRO SWSCC                     ; page 2 = the slot of the SCC (port A8h: the other pages stay as they are)
        ld a,(scc_pg)
        out (0xA8),a
        ENDM
        MACRO SWCART                    ; page 2 = our cartridge again
        ld a,(cart_pg)
        out (0xA8),a
        ENDM
        MACRO WRA                       ; wave entry 0 of channel 1, then the frequency register: the wave restarts (98E0h bit 5) and plays its first entry
        ld a,e
        ld (0x9800),a
        ld (0x9880),a
        ENDM
        MACRO WRB                       ; (the plain loop: the second sample is still in D)
        ld a,d
        ld (0x9800),a
        ld (0x9880),a
        ENDM
        MACRO STB                       ; (a slot: the second sample waits in RAM, the tasks may use every register)
        ld a,d
        ld (sl_b),a
        ENDM
        MACRO WRBM
        ld a,(sl_b)
        ld (0x9800),a
        ld (0x9880),a
        ENDM
        MACRO IBURN bb, nn              ; a burn that only uses IYL (B, C, D, E and the flags of a task stay as they are)
        IF bb > 0
        ld iyl,bb
.t:     dec iyl
        jr nz,.t
        ENDIF
        DUP nn
        nop
        EDUP
        ENDM
        MACRO IWRAP                     ; the bank of the music is used up: the next one
        ld a,h
        cp 0xC0
        jr c,.nw
        call mnext
.nw:
        ENDM
"""

TAIL = """.s:     IFETCH
        SWSCC
        WRA
        exx                             ; the VDP job engine (alternate registers): HL = source, DE = VRAM address of the run (bit 14 set), B = bytes left of
        ld a,b                          ; the run, C = 98h, A' = 1: the address of the next row still has to be written
        or a
        jr z,.nx
        outi                            ; copy 4 bytes (one VDP access every 29 cycles)
        ld a,r
        outi
        ld a,r
        outi
        ld a,r
        outi
        MEBURN EBC,ENC
        exx
.w2:    WRB
        SWCART
        IWRAP
        dec c                           ; the last iteration leaves at once: its idle time is part of the gap otherwise
        jp z,.post
        MBURN LPB,LPN
        jp .s
.nx:    ex af,af'
        or a
        jr nz,.h2
        ld a,(j_dend)                   ; was this the last row?
        cp d
        jr z,.idle
        inc d                           ; next row: +256 in the VRAM, the source moves by (256 - length) (or back to the start for a blank block)
        ld bc,(j_adj)
        add hl,bc
        ld b,0
        ld a,1
        ex af,af'
        MEBURN EBH1,ENH1
        exx
        jp .w2
.h2:    ld a,e                          ; write the VRAM address of the new row
        out (0x99),a
        ld a,d
        out (0x99),a
        ld bc,(j_lc)                    ; B = length, C = 98h
        xor a
        ex af,af'
        MEBURN EBH2,ENH2
        exx
        jp .w2
.idle:  xor a                           ; (A holds the state of the engine, and has been used above)
        ex af,af'
        MEBURN EBI,ENI
        exx
        jp .w2
.post:  xor a                           ; page 1: the code bank again
        ld (0x6000),a
        BANKHI 0x6001
        ld a,(mus_sk)                   ; the frame advances mus_fl iterations: skip the rest (two samples per iteration)
        ld e,a
        ld d,0
        add hl,de
        add hl,de
        ld a,h
        cp 0xC0
        jr c,.nos
        push hl
        call mnext
        pop de
        ld a,d
        sub 0x40
        ld d,a
        ex de,hl
        ld a,(mus_done)                 ; a track that plays once: the end is silence
        or a
        jr z,.nos
        ld hl,0xBF00
.nos:   ld (mus_ptr),hl
        pop hl
        pop de
        pop bc
        ret

; frame counters without the player (no music): v_frame, v_rng, the timer
mfbk:   ld hl,v_frame
        inc (hl)
        ld hl,(v_rng)
        inc hl
        ld (v_rng),hl
        jp VEC_TICK
"""

# ---- cycles of a line (MSX: +1 per opcode fetch, +1 more for an I/O instruction), only to choose where a long task is split
_RAW = [
    (r'^ld [abcdehl],[abcdehl]$', 4, 1), (r'^ld [abcdehl],\(hl\)$', 7, 1), (r'^ld \(hl\),[abcdehl]$', 7, 1), (r'^ld [abcdehl],\(ix\+', 19, 2),
    (r'^ld a,\(de\)$', 7, 1), (r'^ld a,\(', 13, 1), (r'^ld \(.*\),a$', 13, 1), (r'^ld ix,\(', 20, 2), (r'^ld ix,', 14, 2), (r'^ld [abcdehl],', 7, 1),
    (r'^(add|adc|sub|sbc|and|or|xor|cp) a,\(ix\+', 19, 2), (r'^(add|adc|sub|sbc|and|or|xor|cp)( a,|\s)[abcdehl]$', 4, 1), (r'^(add|adc|sub|sbc|and|or|xor|cp)( a,|\s)', 7, 1),
    (r'^add ix,', 15, 2), (r'^neg$', 8, 2), (r'^cpl$', 4, 1), (r'^(inc|dec) [abcdehl]$', 4, 1), (r'^(rla|rrca|rlca|rra)$', 4, 1), (r'^(ex af,af.|exx)$', 4, 1),
    (r'^(in a,|out )\(', 11, 1), (r'^jr ', 8, 1), (r'^call ', 130, 1), (r'^(sla|srl) ', 8, 2), (r'^MCMP', 97, 0), (r'^BANKHI', 14, 1),
]


def lcyc(line):
    l = re.sub(r'^\.\w+:\s*', '', line.strip())
    if not l:
        return 0
    for pat, raw, m1 in _RAW:
        if re.search(pat, l):
            return raw + m1 + (1 if l.startswith(('in ', 'out ')) else 0)
    return 10


def split_ok(lines, k):
    """k lines in the first part: no jump across the cut"""
    lab = {}
    for i, l in enumerate(lines):
        m = re.match(r'^(\.\w+):', l.strip())
        if m:
            lab[m.group(1)] = i
    for i, l in enumerate(lines):
        m = re.search(r'\bj[rp] (?:n?[zc],)?(\.\w+)', l)
        if m and m.group(1) in lab:
            t = lab[m.group(1)]
            if (i < k) != (t < k):
                return False
    return True


REGS = ('a',)                               # the register that the code between the two halves clobbers: a split may not carry A across (B, C, D, E stay)


def rw(line):
    """(reads, writes, flags read, flags written) of a line, for the registers a, b, d, e (a rough parser for the instructions of the tasks)"""
    l = re.sub(r'^\.\w+:\s*', '', line.strip())
    if not l:
        return set(), set(), False, False
    m = l.split(None, 1)
    op = m[0]
    args = [x.strip() for x in m[1].split(',')] if len(m) > 1 else []

    def regs(txt):
        out = set(re.findall(r'\b([abde])\b', re.sub(r'\(ix[^)]*\)|\([a-z_0-9+]+\)', '', txt)))
        if re.search(r'\((de)\)', txt):
            out |= {'d', 'e'}
        return out
    reads, writes, fr, fw = set(), set(), False, False
    if op == 'ld':
        d, sr = args[0], args[1]
        if d in ('a', 'b', 'c', 'd', 'e', 'h', 'l'):
            writes |= {d} & set(REGS)
        else:
            reads |= regs(d.replace('(', ' ').replace(')', ' ')) - set() if False else set()
        reads |= regs(sr) if sr not in ('a', 'b', 'd', 'e') else {sr}
        if d.startswith('(') and sr in REGS:
            reads |= {sr}
        if re.search(r'\(ix|\(iy', sr + d):
            pass
    elif op == 'add' and args[0] in ('ix', 'iy', 'hl'):
        reads |= {c for c in args[1] if c in REGS}
        fw = True
    elif op in ('add', 'adc', 'sub', 'sbc', 'and', 'or', 'xor', 'cp'):
        if len(args) == 2 and args[0] == 'a':
            reads |= {'a'} | (regs(args[1]) if args[1] in REGS else set())
        else:
            reads |= {'a'} | (regs(args[0]) if args[0] in REGS else set())
        if op == 'xor' and args == ['a']:
            reads = set()
        if op != 'cp':
            writes |= {'a'}
        fr = op in ('adc', 'sbc'); fw = True
    elif op in ('inc', 'dec'):
        if args[0] in REGS:
            reads |= {args[0]}; writes |= {args[0]}
        fw = args[0] in ('a', 'b', 'c', 'd', 'e', 'h', 'l')
    elif op in ('neg', 'cpl', 'rrca', 'rlca', 'rra', 'rla', 'ccf'):
        reads |= {'a'}; writes |= {'a'}; fr = op in ('rra', 'rla'); fw = True
    elif op in ('sla', 'srl', 'sra', 'rl', 'rr'):
        if args[0] in REGS:
            reads |= {args[0]}; writes |= {args[0]}
        fw = True
    elif op in ('bit',):
        if args[1] in REGS:
            reads |= {args[1]}
        fw = True
    elif op == 'jr' or op == 'jp':
        if len(args) == 2:
            fr = True
    elif op in ('call', 'out'):
        reads |= {'a'}
    elif op == 'in':
        writes |= {'a'}
    return reads, writes, fr, fw


def can_cut(lines, k):
    """the cut after k lines carries no register (a, b, d, e) and no flag from the first part to the second, and exx / ex af,af' stay balanced"""
    p1, p2 = lines[:k], lines[k:]
    if sum(l.strip() in ('exx',) for l in p1) % 2 or sum(l.strip().startswith('ex af') for l in p1) % 2:
        return False
    written = set(); flags = False
    for l in p2:
        r, w, fr, fw = rw(l)
        if (r - written) & set(REGS):
            return False
        if fr and not flags:
            return False
        written |= w
        flags = flags or fw
    return True


def choose_split(lines, first_budget):
    """the number of lines for the first half: the longest part that fits first_budget cycles (model), at a place where no jump crosses"""
    acc = 0; best = len(lines)
    for k, l in enumerate(lines):
        acc += lcyc(l)
        if acc > first_budget:
            best = k
            break
    else:
        return len(lines)
    while best > 0 and not (split_ok(lines, best) and can_cut(lines, best)):
        best -= 1
    if best <= 0 or sum(lcyc(l) for l in lines[best:]) > 55:       # no good place for a cut: the whole task in the first half
        return len(lines)
    return best


def adapt(tasks):
    """the two long tasks (joystick merge, the new phase of the job engine) are cut into smaller ones: a slot has about 200 cycles for its task here, not 450;
    the registers that live across the cut go through RAM (sl_jc)"""
    out = []
    for cm, lines in tasks:
        if cm.startswith('joystick: merge'):
            out.append((cm + ' (1/3)', lines[:16] + ['ld (sl_jc),a']))
            out.append((cm + ' (2/3)', ['ld a,(sl_jc)', 'ld c,a'] + lines[16:34]))
            out.append((cm + ' (3/3)', ['ld a,(sl_jc)', 'ld c,a'] + lines[34:]))
        elif cm.startswith('job engine: length, last row'):
            g = ['ld a,(j_go)', 'or a', 'jr z,.pce']
            out.append((cm + ' (1/3)', g + lines[3:9] + ['.pce:']))
            out.append((cm + ' (2/3)', g + lines[9:17] + ['.pce:']))
            out.append((cm + ' (3/3)', g + lines[17:-1] + ['.pce:']))
        else:
            out.append((cm, lines))
    return out


def generate(HEAD, tasks, fmt, NS):
    cfg = load_cfg()
    tasks = adapt(tasks)
    NS = len(tasks)
    i0 = HEAD.index('        MACRO MSAMPLE'); i1 = HEAD.index('        ENDM', i0) + len('        ENDM\n')
    head = HEAD[:i0] + MACROS + HEAD[i1:]
    out = [head, 'NSLOTS equ %d\n' % NS]
    for i, (cm, lines) in enumerate(tasks, 1):
        k = cfg['split'].get(str(i))
        if k is None:
            k = len(lines)
            if sum(lcyc(l) for l in lines) > 135:                  # (the model is a bit optimistic: look for a cut with a smaller first part, if the task is long)
                for fb in (135, 120, 105, 90, 75):
                    kk = choose_split(lines, fb)
                    if kk < len(lines):
                        k = kk
                        break
        p1, p2 = lines[:k], lines[k:]
        b1 = cfg['b1'].get(str(i), MIN_B); b2 = cfg['b2'].get(str(i), MIN_B)
        B1, N1 = bn(b1); B2, N2 = bn(b2)
        out.append('sx_%d:     IFETCH                      ; %d: %s\n' % (i, i, cm))
        out.append('        SWSCC\n        WRA\n        STB\n')
        for ln in p1:
            out.append(fmt(ln, i) + '\n')
        out.append('        IBURN %d,%d                     ; %.0f cycles\n        WRBM\n        SWCART\n        IWRAP\n' % (B1, N1, b1))
        for ln in p2:
            out.append(fmt(ln, i) + '\n')
        out.append('        IBURN %d,%d                     ; %.0f cycles\n' % (B2, N2, b2))
    lp = cfg['loop']
    tail = TAIL
    for nm, key in (('EBC', 'C'), ('EBH1', 'H1'), ('EBH2', 'H2'), ('EBI', 'I')):
        B, N = bn(lp[key], 18, 3, 1)
        tail = tail.replace('MEBURN %s,%s' % (nm, nm.replace('EB', 'EN')), 'MEBURN %d,%d                  ; %.0f cycles' % (B, N, lp[key]))
    B, N = bn(lp['P'])
    tail = tail.replace('MBURN LPB,LPN', 'IBURN %d,%d                   ; %.0f cycles' % (B, N, lp['P']))
    out.append(tail)
    open(os.path.join(PROJ, 'game', 'slots_scc16.inc'), 'w').write(''.join(out))
    open(os.path.join(PROJ, 'game', 'slots_ns.txt'), 'w').write(str(NS))
    print('slots (scc16):', NS)
