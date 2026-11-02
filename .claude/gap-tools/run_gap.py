"""usage: run_gap.py ROM MODE SIZE CTL [HOLD]  -> runs gap_log.tcl in openMSX (own process, killed after 150 s at most) and prints the analysis (analyse.py)"""
import subprocess, os, sys, time
P = r'F:\MSX Projects\PMdev26'
rom, mode, size, ctl = sys.argv[1:5]
hold = len(sys.argv) > 5 and sys.argv[5] == 'hold'
out = os.path.join(P, 'work', 'gap_%s_%s_%s.txt' % (mode, size, ctl))
os.makedirs(os.path.join(P, 'work', 'shots'), exist_ok=True)
open(os.path.join(P, 'work', 'shots', 'log.txt'), 'w').close()
env = dict(os.environ, MODE=mode, SIZE=size, CTL=ctl, OUT=out.replace(chr(92), '/'))
if hold: env['HOLD'] = '1'
for a in sys.argv[5:]:
    if a == 'PROF': env['PROF'] = '1'
    if a == 'HINT': env['HINT'] = '1'
    if a.startswith('PCS='): env['PCS'] = a[4:].replace(',', ' '); env['PROF'] = '1'
    if a.startswith('KC='): env['KC'] = a[3:]
    if a.startswith('KB='): env['KB'] = a[3:]
    if a.startswith('TAG='): out = out.replace('.txt', '_' + a[4:] + '.txt'); env['OUT'] = out.replace(chr(92), '/')
if os.path.exists(out): os.remove(out)
ext = ['-ext', 'scc'] if 'EXT=scc' in sys.argv else []
p = subprocess.Popen([r'C:\Program Files\openMSX\openmsx.exe', '-machine', 'Philips_NMS_8250' if ext else 'Philips_VG_8020', '-cart', rom, '-romtype', 'NEO-16'] + ext + ['-script', os.path.join(P, '.claude', 'gap-tools', 'gap_log.tcl')], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
t0 = time.time()
while time.time() - t0 < 70 and p.poll() is None: time.sleep(2)
if p.poll() is None: p.kill(); print('killed after 150 s')
print(open(os.path.join(P, 'work', 'shots', 'log.txt')).read())
print(subprocess.run([sys.executable, os.path.join(P, '.claude', 'gap-tools', 'analyse.py'), out], capture_output=True, text=True).stdout)
