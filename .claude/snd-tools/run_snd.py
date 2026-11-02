"""Run a jingle test ROM (built with --jngtest) in openMSX and log the sample times.
usage: run_snd.py ROM psg|scc [SEC] -> prints the distance (cycles) of the samples per position of the pass"""
import os, sys, subprocess, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
OPENMSX = r'C:\Program Files\openMSX\openmsx.exe'
CPU = 3579545.0


def run(rom, mode, sec=6, machine='Philips_NMS_8250'):
    out = os.path.join(HERE, 'snd_%s.txt' % mode)
    if os.path.exists(out): os.remove(out)
    cmd = [OPENMSX, '-machine', machine, '-cart', rom, '-romtype', 'NEO-16']
    if mode == 'scc': cmd += ['-ext', 'scc']
    cmd += ['-script', os.path.join(HERE, 'snd_log.tcl')]
    p = subprocess.Popen(cmd, env=dict(os.environ, MODE=mode, SEC=str(sec), OUT=out))
    t = time.time()
    while not os.path.exists(out) and time.time() - t < 120:
        time.sleep(0.5)
    time.sleep(1)
    p.kill()
    return np.array([float(x) for x in open(out).read().split()])


if __name__ == '__main__':
    rom, mode = sys.argv[1], sys.argv[2]
    sec = float(sys.argv[3]) if len(sys.argv) > 3 else 6
    t = run(rom, mode, sec)
    if mode == 'psg':                                   # six data writes per sample: the first of every six is the register 8 volume
        t = t[0::3]
    d = np.diff(t) * CPU
    print(mode, len(t), 'events, mean distance', d.mean())
    # 4 iterations per pass: the pattern repeats every 8 samples (PSG) / 8 samples (SCC); find the phase from a long run of typical values
    d = d[:len(d) // 8 * 8]
    # robust: use the median per phase over the first 4000 samples (the bank slips are rare)
    for ph in range(8):
        x = d[ph::8]
        print('phase', ph, 'median %.1f' % np.median(x), 'min %.1f max %.1f' % (x.min(), x.max()))
