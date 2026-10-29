import subprocess, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROM = r'F:\MSX Projects\PMdev26\PM_WaitState_16KB.rom'
machines = sys.argv[1:]
ps = []
for m in machines:
    env = dict(os.environ, OUT=os.path.join(HERE, 'r_%s.txt' % m), AT=os.environ.get('AT', '25'))
    if os.path.exists(env['OUT']): os.remove(env['OUT'])
    ps.append((m, subprocess.Popen([r'C:\Program Files\openMSX\openmsx.exe', '-machine', m, '-cart', ROM, '-script', os.path.join(HERE, 'dump.tcl')], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)))
for m, p in ps:
    try: p.wait(timeout=300)
    except subprocess.TimeoutExpired: p.kill()
for m in machines:
    f = os.path.join(HERE, 'r_%s.txt' % m)
    print('==', m)
    if os.path.exists(f):
        t = open(f, errors='replace').read().split('\n')
        print('\n'.join(l.rstrip() for l in t[:18] if l.strip()))
    else: print('no output')
