import subprocess, os, time
P = r'F:\MSX Projects\PMdev26'
out = P.replace(chr(92), '/') + '/work/xmas/a'
env = dict(os.environ, DUMP=out)
open(os.path.join(P, 'work', 'shots', 'log.txt'), 'w').close()
p = subprocess.Popen([r'C:\Program Files\openMSX\openmsx.exe', '-machine', 'Philips_NMS_8250', '-cart', os.path.join(P, '.claude', 'oops-tools', 'wip', 'PM_xmas_TEST.rom'), '-romtype', 'NEO-16', '-script', os.path.join(P, '.claude', 'oops-tools', 'xmas_check.tcl')], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
t0 = time.time()
for chk in (20, 40, 60, 90, 120, 180, 240):
    while time.time() - t0 < chk and p.poll() is None: time.sleep(1)
    files = sorted(f for f in os.listdir(os.path.join(P, 'work', 'xmas')) if f.startswith('a-'))
    print('check at %ds: running=%s shots=%s' % (chk, p.poll() is None, ' '.join(f[2:-4] for f in files)), flush=True)
    if p.poll() is not None: break
if p.poll() is None: p.kill(); print('killed')
print(open(os.path.join(P, 'work', 'shots', 'log.txt')).read())
