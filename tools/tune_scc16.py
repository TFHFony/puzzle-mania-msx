"""Calibrate the SCC player at 16 kHz (tools/scc16.json): both samples of an iteration must be 223.01 cycles apart, in every slot and in every path of the job engine.
Builds a small test ROM (NEO16, --lite --quick --scc), logs the frequency writes of the SCC (one per sample, with the PC) and the VDP writes in openMSX (t113.tcl),
measures the first half (A to B) and the second half (B to the next A) of every slot / every kind of loop iteration and corrects the burns (cycles).
usage: tune_scc16.py [rounds]"""
import os, sys, re, json, subprocess, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
OPENMSX = r'C:\Program Files\openMSX\openmsx.exe'
TCL = os.path.join(PROJ, '.claude', 'pm-tools', 't113.tcl')
OUT = os.path.join(PROJ, 'work', 'shots', 't113.txt')
CPU = 3579545.0
HALF = 446.025 / 2
CFG = os.path.join(HERE, 'scc16.json')
ROM = 'PuzzleMania_S16TEST.rom'


def load_cfg():
    sys.path.insert(0, HERE)
    import gen_slots16
    return gen_slots16.load_cfg()


def build():
    r = subprocess.run([sys.executable, os.path.join(HERE, 'build_game.py'), '--lite', '--quick', '--scc', '--out', ROM], capture_output=True, text=True, cwd=PROJ)
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-2000:])
        sys.exit('build failed')


def run():
    if os.path.exists(OUT):
        os.remove(OUT)
    p = subprocess.Popen([OPENMSX, '-machine', 'Philips_NMS_8250', '-cart', os.path.join(PROJ, ROM), '-romtype', 'NEO-16', '-ext', 'scc', '-script', TCL],
                         env=dict(os.environ, DUMP='x'))
    t = time.time()
    while not os.path.exists(OUT) and time.time() - t < 200:
        time.sleep(1)
    time.sleep(1)
    p.kill()


def symbols():
    sx = {}
    loop = None
    for l in open(os.path.join(PROJ, 'game', 'plr_scc.sym')):
        m = re.match(r'(\S+): EQU 0x([0-9A-F]+)', l)
        if not m:
            continue
        n, a = m.group(1), int(m.group(2), 16)
        mm = re.match(r'sx_(\d+)$', n)
        if mm:
            sx[int(mm.group(1))] = a
        if re.match(r'sx_\d+\.s$', n):
            loop = a
    return sx, loop


def analyse():
    sx, loop = symbols()
    ns = max(sx)
    starts = sorted((a, i) for i, a in sx.items())
    ev = [l.split() for l in open(OUT).read().splitlines()]
    S = [(float(t) * CPU, int(pc, 16)) for k, t, pc in ev if k == 's']
    V = np.array([float(t) * CPU for k, t, *_ in ev if k == 'v'])

    def slot_of(pc):
        if pc >= loop:
            return 0
        k = max((i for a, i in starts if a <= pc), default=1)
        return k
    ids = [slot_of(pc) for _, pc in S]
    ts = np.array([t for t, _ in S])
    # pair the writes: slot k has exactly two (A, B); the loop alternates A, B
    pairs = []                       # (slot, tA, tB, index of A)
    i = 0
    while i + 1 < len(S):
        a, b = ids[i], ids[i + 1]
        if a == b and (a != 0 or True):
            pairs.append((a, ts[i], ts[i + 1], i)); i += 2
        else:
            i += 1
    res = {'ab': {}, 'ba': {}, 'cls': {}, 'clsba': {}}
    loop_seq = []                      # the loop iterations in order, with their kind
    for n, (k, ta, tb, idx) in enumerate(pairs):
        nxt = pairs[n + 1] if n + 1 < len(pairs) else None
        ab = tb - ta
        ba = (nxt[1] - tb) if nxt is not None else None
        if ba is not None and ba > 600:
            ba = None                # a gap between two frames
        if k > 0:
            res['ab'].setdefault(k, []).append(ab)
            if ba is not None and nxt[0] in (k + 1, 0):
                res['ba'].setdefault(k, []).append(ba)
        else:
            n1 = int(((V > ta) & (V < tb)).sum())
            n2 = int(((V > tb) & (V < (nxt[1] if nxt else tb))).sum()) if nxt else 0
            if n1 == 4:
                c = 'C'
            elif n1 == 2:
                c = 'H2'
            elif n1 == 0:
                c = 'N0'
            else:
                c = 'X%d' % n1
            res['cls'].setdefault(c, []).append((ab, ba, n2))
            loop_seq.append([c, ab, ba])
    # N0 = H1 (the next iteration is an H2: two address bytes) or idle
    for k in range(len(loop_seq) - 1):
        if loop_seq[k][0] == 'N0':
            loop_seq[k][0] = 'H1' if loop_seq[k + 1][0] == 'H2' else 'I'
    for c, ab, ba in loop_seq:
        res['clsba'].setdefault(c, []).append((ab, ba))
    return res, ns


def med(v):
    return float(np.median(v)) if len(v) else None


def main():
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    for r in range(rounds):
        cfg = load_cfg()
        build()
        run()
        res, ns = analyse()
        worst = 0.0
        # the slots
        bad = []
        for k in range(1, ns + 1):
            ab = med(res['ab'].get(k, [])); ba = med(res['ba'].get(k, []))
            if ab is None:
                continue
            e1 = HALF - ab
            cfg['b1'][str(k)] = max(0.0, cfg['b1'].get(str(k), 17.0) + e1)
            if ba is not None:
                e2 = HALF - ba
                cfg['b2'][str(k)] = max(0.0, cfg['b2'].get(str(k), 17.0) + e2)
                worst = max(worst, abs(e2))
            worst = max(worst, abs(e1) if ab > HALF - 0.01 or cfg['b1'][str(k)] > 17.0 else 0)
            if ab > HALF + 1.5 and cfg['b1'][str(k)] <= 17.0:
                bad.append((k, round(ab - HALF, 1)))
        # the loop
        lp = cfg['loop']
        msg = []
        for c, key in (('C', 'C'), ('H2', 'H2')):
            xs = res['cls'].get(c, [])
            if xs:
                ab = med([x[0] for x in xs]); lp[key] = max(0.0, lp[key] + HALF - ab); worst = max(worst, abs(HALF - ab)); msg.append('%s ab %.1f n=%d' % (c, ab, len(xs)))
        for c in ('H1', 'I'):
            xs = res['clsba'].get(c, [])
            if len(xs) > 5:
                ab = med([x[0] for x in xs]); lp[c] = max(0.0, lp[c] + HALF - ab); worst = max(worst, abs(HALF - ab)); msg.append('%s ab %.1f n=%d' % (c, ab, len(xs)))
        allba = [x[1] for c in res['cls'] for x in res['cls'][c] if x[1] is not None]
        if allba:
            ba = med(allba); lp['P'] = max(0.0, lp['P'] + HALF - ba); worst = max(worst, abs(HALF - ba)); msg.append('loop ba %.1f' % ba)
        print('round %d: worst error %.1f cycles; %s; slots over: %s' % (r, worst, '; '.join(msg), bad), flush=True)
        json.dump(cfg, open(CFG, 'w'), indent=1)
    print('done')


if __name__ == '__main__':
    main()
