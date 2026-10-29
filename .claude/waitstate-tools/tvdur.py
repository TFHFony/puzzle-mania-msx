import subprocess, os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROM = os.environ.get('ROM', 'F:/MSX Projects/PMdev26/PuzzleMania_128MB.rom')
sym = {}
for l in open(r'F:\MSX Projects\PMdev26\game\pm.sym'):
    m = re.match(r'(\w+): EQU 0x([0-9A-Fa-f]+)', l)
    if m: sym[m.group(1)] = '0x' + m.group(2)
jobs = []
for spec in sys.argv[1:]:
    m, scc, force = spec.split(',')
    if scc == '1':
        ent, ex = [sym['tvplay16'], sym['w_tvplay16']], [sym['tv16_exit'], sym['w_tv16_exit']]
    else:
        ent, ex = [sym['tvplay'], sym['tv8_tvplay']], [sym['tv_exit'], sym['tv8_tv_exit']]
    out = os.path.join(HERE, 'tv_%s_%s_%s.txt' % (m, scc, force))
    if os.path.exists(out): os.remove(out)
    env = dict(os.environ, FORCE=force, ENT=' '.join(ent), EX=' '.join(ex), OUT=out.replace(chr(92), '/'))
    jobs.append((spec, out, subprocess.Popen([r'C:\Program Files\openMSX\openmsx.exe', '-machine', m, '-cart', ROM, '-romtype', 'NEO-16'] + (['-ext', 'scc'] if scc == '1' else []) + ['-script', os.path.join(HERE, 'tvdur.tcl')], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)))
for spec, out, p in jobs:
    try: p.wait(timeout=500)
    except subprocess.TimeoutExpired: p.kill()
    print(spec, open(out).read().strip() if os.path.exists(out) else 'no output')
