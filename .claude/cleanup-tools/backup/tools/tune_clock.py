"""Tune the sample clock of the PSG player so that a video frame holds exactly mus_f samples (the music is locked to the frame, so a loop
clock that is not exactly frame/mus_f makes the lock skip or repeat a fraction of a sample every frame: rough high tones).
PAL frame 313 lines * 228 = 71364 cycles = 160 samples of 446.025 cycles; NTSC 262 * 228 = 59736 cycles = 400/3 samples of 448.02 cycles.
Measures the sample period in openMSX (sample ROM, time of the PSG writes, work/wlog.txt) for MDELAY with the fraction off, then sets the 8 bit fraction FI (FI/256 of the
iterations are 5 cycles longer) for both standards; writes tools/clock.json.
usage: tune_clock.py            (measure, choose, verify)
       tune_clock.py MD FIP FIN (measure only)"""
import os, sys, json, subprocess, re
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
OPENMSX = r'C:\Program Files\openMSX\openmsx.exe'
TCL = os.path.join(PROJ, '.claude', 'pm-tools', 'wlog.tcl')
LOG = os.path.join(PROJ, 'work', 'shots', 'log.txt')
CPU = 3579545
PAL = 313 * 228 / 160
NTSC = 262 * 228 * 3 / 400


def measure(md, fip, fin):
    json.dump({'MDELAY': md, 'FI_PAL': fip, 'FI_NTSC': fin}, open(os.path.join(HERE, 'clock.json'), 'w'))
    subprocess.run([sys.executable, os.path.join(HERE, 'build_sample.py'), '--curve', 'ym', '--framed', '--out', 'work/slots_test.rom'], check=True, capture_output=True)
    w = os.path.join(PROJ, 'work', 'wlog.txt')
    if os.path.exists(w): os.remove(w)
    subprocess.run([OPENMSX, '-machine', 'Philips_VG_8020', '-cart', os.path.join(PROJ, 'work', 'slots_test.rom'), '-romtype', 'NEO-16', '-script', TCL],
                   capture_output=True, timeout=300)
    import numpy as np
    t = []
    for ln in open(w):
        p, v, tm = ln.split()
        if p == '0' and int(v) == 8: t.append(float(tm))
    t = np.array(t) * CPU; d = np.diff(t); P = np.median(d)
    pers = []
    for s, e in zip([0] + list(np.where(d > 1.5 * P)[0] + 1), list(np.where(d > 1.5 * P)[0]) + [len(t) - 1]):
        if e - s > 50: pers.append(np.polyfit(np.arange(e - s + 1), t[s:e + 1], 1)[0])
    cyc = float(np.mean(pers))
    print('MDELAY %d FI %d/%d -> %.3f cycles (%.2f Hz)' % (md, fip, fin, cyc, CPU / cyc), flush=True)
    return CPU / cyc


if __name__ == '__main__':
    if len(sys.argv) > 3:
        measure(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
        sys.exit()
    md = 10
    cyc = CPU / measure(md, 0, 0)
    while cyc > PAL:                         # the base must be below both targets, within 5 cycles of the NTSC one (the fraction adds 0..5)
        md -= 1; cyc -= 14
    while cyc + 14 <= PAL:
        md += 1; cyc += 14
    cyc = CPU / measure(md, 0, 0)
    fip = int(round((PAL - cyc) * 256 / 5))
    fin = int(round((NTSC - cyc) * 256 / 5))
    assert 0 <= fip < 256 and 0 <= fin < 256, (cyc, fip, fin)
    print('chosen MDELAY', md, 'FI_PAL', fip, 'FI_NTSC', fin)
    rate = measure(md, fip, fin)
    print('PAL target %.3f cycles, got %.3f; frame rate check: %.3f samples/frame' % (PAL, CPU / rate, 313 * 228 / (CPU / rate)))
