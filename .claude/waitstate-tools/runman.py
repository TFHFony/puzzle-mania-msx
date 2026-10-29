import subprocess, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); P = r'F:\MSX Projects\PMdev26'
tit = sys.argv[1]; machine = sys.argv[2] if len(sys.argv) > 2 else 'Philips_NMS_8250'
out = P.replace(chr(92), '/') + '/work/manual/' + ('a' if tit == '1' else 'b')
env = dict(os.environ, TIT=tit, DUMP=out)
logf = os.path.join(P, 'work', 'shots', 'log.txt')
p = subprocess.Popen([r'C:\Program Files\openMSX\openmsx.exe', '-machine', machine, '-cart', os.path.join(P, 'PuzzleMania_128MB.rom'), '-romtype', 'NEO-16', '-script', os.path.join(P, '.claude', 'pm-tools', 'screenshots_manual.tcl')], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
t0 = time.time()
for chk in (20, 40, 60, 90, 120, 180, 240, 300, 400, 500):
    while time.time() - t0 < chk and p.poll() is None: time.sleep(1)
    files = sorted(f for f in os.listdir(os.path.join(P, 'work', 'manual')) if f.startswith('a-' if tit == '1' else 'b-'))
    print('check at %ds: running=%s shots=%s' % (chk, p.poll() is None, ' '.join(f[2:-4] for f in files)), flush=True)
    if p.poll() is not None: break
if p.poll() is None: p.kill(); print('killed')
