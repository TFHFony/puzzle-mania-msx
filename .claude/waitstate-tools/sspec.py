import subprocess, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROM = r'F:\MSX Projects\PMdev26\PuzzleMania_128MB.rom'
os.makedirs(os.path.join(HERE, 'ss'), exist_ok=True)
ps = []
for spec in sys.argv[1:]:
    m, t1, scc = spec.split(',')
    env = dict(os.environ, SHOT=os.path.join(HERE, 'ss', m).replace(chr(92), '/'), T1=t1)
    args = [r'C:\Program Files\openMSX\openmsx.exe', '-machine', m, '-cart', ROM, '-romtype', 'NEO-16'] + (['-ext', 'scc'] if scc == '1' else []) + ['-script', os.path.join(HERE, 'sspec.tcl')]
    ps.append(subprocess.Popen(args, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
for p in ps:
    try: p.wait(timeout=400)
    except subprocess.TimeoutExpired: p.kill()
