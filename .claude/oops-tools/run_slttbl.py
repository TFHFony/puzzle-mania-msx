"""usage: run_slttbl.py ROM SLT [extra openmsx args]  -> boot test with SLTTBL[1] = SLT (decimal or 0x..); prints the log; kills openMSX after 60 s"""
import subprocess, os, sys, time
P = r'F:\MSX Projects\PMdev26'
rom, slt = sys.argv[1], sys.argv[2]
extra = sys.argv[3:]
os.makedirs(os.path.join(P, 'work', 'slt'), exist_ok=True)
env = dict(os.environ, SLT=slt, DUMP=P.replace(chr(92), '/') + '/work/slt/' + os.path.basename(rom) + '_' + slt)
open(os.path.join(P, 'work', 'shots', 'log.txt'), 'w').close()
p = subprocess.Popen([r'C:\Program Files\openMSX\openmsx.exe', '-machine', 'Philips_NMS_8250', '-cart', rom, '-romtype', 'NEO-16'] + extra + ['-script', os.path.join(P, '.claude', 'oops-tools', 'slttbl_check.tcl')], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
t0 = time.time()
for chk in (20, 40, 60):
    while time.time() - t0 < chk and p.poll() is None: time.sleep(1)
    print('check at %ds: running=%s' % (chk, p.poll() is None), flush=True)
    if p.poll() is not None: break
if p.poll() is None: p.kill(); print('killed')
print(open(os.path.join(P, 'work', 'shots', 'log.txt')).read())
