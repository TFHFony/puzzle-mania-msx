"""usage: run_jig.py ROM MODE MACHINE OUTDIR   (MODE video|photo; MACHINE e.g. Philips_VG_8020 / Philips_NMS_8250)  runs jig_test.tcl in openMSX (own process, 150 s at most)"""
import subprocess, os, sys, time, shutil
rom, mode, machine, out = sys.argv[1:5]
shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
env = dict(os.environ, MODE=mode, OUT=out.replace(chr(92), '/'))
p = subprocess.Popen([r'C:\Program Files\openMSX\openmsx.exe', '-machine', machine, '-cart', rom, '-romtype', 'NEO-16', '-script', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jig_test.tcl')], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
t0 = time.time()
while time.time() - t0 < 150 and p.poll() is None: time.sleep(2)
if p.poll() is None: p.kill(); print('killed')
print(open(os.path.join(out, 'log.txt')).read() if os.path.exists(os.path.join(out, 'log.txt')) else 'no log')
