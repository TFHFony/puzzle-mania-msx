"""measure the interval of every work slot of the PSG player in the real game (menu idle): python slotmeas.py rom [machine]"""
import subprocess, os, re, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
G = r'F:\MSX Projects\PMdev26\game'
SJ = r'F:\MSX Projects\Dev27\.claude\msx-video-tools\sjasmplus\sjasmplus-1.24.0.win\sjasmplus.exe'
def first_write_pcs():
    subprocess.run([SJ, '--nologo', '--lst=plr_slot.lst', '--sym=plr_slot.sym', 'plr.asm'], cwd=G, capture_output=True)
    L = []
    for l in open(os.path.join(G, 'plr_slot.lst'), errors='replace'):
        m = re.match(r'\s*\d+\+*\s*([0-9A-F]{4})\s+((?:[0-9A-F]{2}\s)+)\s*>?\s*(.*)$', l)
        if m: L.append((int(m.group(1), 16), m.group(3).strip()))
    pcs = []
    for i in range(len(L) - 3):
        t = [x[1].split(';')[0].strip() for x in L[i:i + 4]]
        if t[0] == 'ld a,8' and t[1] == 'out (0xA0),a' and t[2] == 'ld a,(de)' and t[3] == 'out (0xA1),a':
            pcs.append(L[i + 3][0])
    return pcs
def measure(rom, machine='Philips_VG_8020', ton='44'):
    out = os.path.join(HERE, 'sm.txt').replace(chr(92), '/')
    if os.path.exists(out): os.remove(out)
    env = dict(os.environ, T0=ton, OUT=out)
    p = subprocess.Popen([r'C:\Program Files\openMSX\openmsx.exe', '-machine', machine, '-cart', rom, '-romtype', 'NEO-16', '-script', os.path.join(HERE, 'slotmeas.tcl')], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = time.time()
    for chk in (20, 40, 60, 90):
        while time.time() - t0 < chk and p.poll() is None and not os.path.exists(out): time.sleep(1)
        print('  check at %ds: running=%s output=%s' % (chk, p.poll() is None, os.path.exists(out)), flush=True)
        if os.path.exists(out) or p.poll() is not None: break
    time.sleep(1)
    if p.poll() is None: p.kill(); print('  killed')
    return [l.split() for l in open(out).read().splitlines()]
if __name__ == '__main__':
    rom = sys.argv[1]
    pcs = set(first_write_pcs())
    print('sample first-write PCs:', len(pcs))
    ev = measure(rom, *(sys.argv[2:3]))
    # frames start at the M markers; sample first writes
    frames = []; cur = None
    for k, a, t in ev:
        if k == 'M': cur = []; frames.append(cur)
        elif k == 'W' and cur is not None and int(a, 16) in pcs: cur.append(float(t) * 3579545)
    res = []
    for f in frames[1:-1]:
        d = np.diff(f)
        res.append(d)
    n = min(len(r) for r in res)
    R = np.array([r[:n] for r in res])
    med = np.median(R, 0)
    np.save(os.path.join(HERE, 'slot_iv.npy'), med)
    print('frames', len(res), 'intervals', n)
    print('slot intervals (cycles), target 446.0:')
    print(' '.join('%d:%.0f' % (i + 1, v) for i, v in enumerate(med[:62])))
