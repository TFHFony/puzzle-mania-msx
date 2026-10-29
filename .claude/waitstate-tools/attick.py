import subprocess, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROM = r'F:\MSX Projects\PMdev26\PuzzleMania_128MB.rom'
ps = []
for spec in sys.argv[1:]:
    m, scc = spec.split(',')
    wav = os.path.join(HERE, 'at_%s_%s.wav' % (m, scc)).replace(chr(92), '/')
    log = os.path.join(HERE, 'at_%s_%s.log' % (m, scc)).replace(chr(92), '/')
    for f in (wav, log):
        if os.path.exists(f): os.remove(f)
    env = dict(os.environ, WAV=wav, LOG=log)
    ps.append(subprocess.Popen([r'C:\Program Files\openMSX\openmsx.exe', '-machine', m, '-cart', ROM, '-romtype', 'NEO-16'] + (['-ext', 'scc'] if scc == '1' else []) + ['-script', os.path.join(HERE, 'attick.tcl')], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
for p in ps:
    try: p.wait(timeout=900)
    except subprocess.TimeoutExpired: p.kill()
