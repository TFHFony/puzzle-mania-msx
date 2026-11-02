"""usage: run_menu.py ROM OUTNAME  -> menu_hold.tcl in openMSX (own process, killed after 70 s), prints the samples"""
import subprocess, os, sys, time
P = r'F:\MSX Projects\PMdev26'
rom, name = sys.argv[1:3]
out = os.path.join(P, 'work', 'menu_%s.txt' % name)
open(os.path.join(P, 'work', 'shots', 'log.txt'), 'w').close()
if os.path.exists(out): os.remove(out)
p = subprocess.Popen([r'C:\Program Files\openMSX\openmsx.exe', '-machine', 'Philips_VG_8020', '-cart', rom, '-romtype', 'NEO-16', '-script', os.path.join(P, '.claude', 'gap-tools', 'menu_hold.tcl')], env=dict(os.environ, OUT=out.replace(chr(92), '/')), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
t0 = time.time()
while time.time() - t0 < 70 and p.poll() is None: time.sleep(2)
if p.poll() is None: p.kill(); print('killed')
print(open(out).read() if os.path.exists(out) else open(os.path.join(P, 'work', 'shots', 'log.txt')).read())
