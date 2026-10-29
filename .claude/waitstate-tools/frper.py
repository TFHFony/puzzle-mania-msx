import subprocess, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
jobs = []
for spec in sys.argv[1:]:
    rom, m, scc, addr = spec.split(',')
    out = os.path.join(HERE, 'fr_%s_%s_%s.txt' % (os.path.basename(rom), m, scc)).replace(chr(92), '/')
    if os.path.exists(out): os.remove(out)
    env = dict(os.environ, T0='44', ADDR=addr, OUT=out)
    jobs.append((spec, out, subprocess.Popen([r'C:\Program Files\openMSX\openmsx.exe', '-machine', m, '-cart', rom, '-romtype', 'NEO-16'] + (['-ext', 'scc'] if scc == '1' else []) + ['-script', os.path.join(HERE, 'frper.tcl')], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)))
for spec, out, p in jobs:
    try: p.wait(timeout=300)
    except subprocess.TimeoutExpired: p.kill()
    if os.path.exists(out):
        t = np.array([float(x) for x in open(out).read().split()]); d = np.diff(t) * 1000
        print(os.path.basename(spec.split(',')[0]), spec.split(',')[1:3], 'frames %d  mean %.4f ms  min %.3f max %.3f' % (len(d), d.mean(), d.min(), d.max()))
    else: print(spec, 'no output')
