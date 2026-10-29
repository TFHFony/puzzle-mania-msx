"""profile one idle menu frame (instruction level) of a test ROM: python profidle.py rom"""
import re, os, sys, subprocess, time, bisect
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); G = r'F:\MSX Projects\PMdev26\game'
SJ = r'F:\MSX Projects\Dev27\.claude\msx-video-tools\sjasmplus\sjasmplus-1.24.0.win\sjasmplus.exe'
def sym(fn):
    d = {}
    for l in open(fn):
        m = re.match(r'([\w.]+): EQU 0x([0-9A-Fa-f]+)', l)
        if m: d[m.group(1)] = int(m.group(2), 16)
    return d
def starts(lst, ranges):
    out = set()
    for l in open(lst, errors='replace'):
        m = re.match(r'\s*\d+\+*\s*([0-9A-F]{4})\s+((?:[0-9A-F]{2}\s)+)', l)
        if m:
            a = int(m.group(1), 16)
            if any(lo <= a < hi for lo, hi in ranges): out.add(a)
    return sorted(out)
rom = sys.argv[1]
subprocess.run([SJ, '--nologo', '--lst=pm_prof.lst', '--sym=pm_prof.sym', 'pm.asm'], cwd=G, capture_output=True)
subprocess.run([SJ, '--nologo', '--lst=plr_prof.lst', '--sym=plr_prof.sym', 'plr.asm'], cwd=G, capture_output=True)
ps, ms = sym(os.path.join(G, 'plr_prof.sym')), sym(os.path.join(G, 'pm_prof.sym'))
post = ps['NSLOTS.post']
rp = [(0xD300, ps['mvsync_.go'] + 0x20), (post, post + 0x60)]
rm = [(ms['menu_loop.l'], ms['menu_loop.bz'] + 0x10), (ms['anykey'], ms['anykey'] + 0x30), (ms['att_check'], ms['att_check'] + 0x60), (ms['selchk'], ms['selchk'] + 0x40)]
addrs = starts(os.path.join(G, 'plr_prof.lst'), rp) + starts(os.path.join(G, 'pm_prof.lst'), rm)
out = os.path.join(HERE, 'pi.txt').replace(chr(92), '/')
if os.path.exists(out): os.remove(out)
env = dict(os.environ, OUT=out, ADDRS=' '.join('0x%X' % a for a in addrs), T0='44')
p = subprocess.Popen([r'C:\Program Files\openMSX\openmsx.exe', '-machine', 'Philips_VG_8020', '-cart', rom, '-romtype', 'NEO-16', '-script', os.path.join(HERE, 'profidle.tcl')], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
t0 = time.time()
for chk in (20, 40, 60, 90):
    while time.time() - t0 < chk and p.poll() is None and not os.path.exists(out): time.sleep(1)
    print('check at %ds: running=%s output=%s' % (chk, p.poll() is None, os.path.exists(out)), flush=True)
    if os.path.exists(out) or p.poll() is not None: break
time.sleep(1)
if p.poll() is None: p.kill()
ev = [(l.split()[0], int(l.split()[1], 16), float(l.split()[2]) * 3579545) for l in open(out).read().splitlines()]
def region(pc):
    if rp[0][0] <= pc < rp[0][1]: return 'player prologue'
    if rp[1][0] <= pc < rp[1][1]: return 'player epilogue (.post)'
    for nm in ('menu_loop', 'anykey', 'att_check', 'selchk'):
        a = ms[nm] if nm != 'menu_loop' else ms['menu_loop.l']
        if a <= pc < a + 0x70 and nm != 'menu_loop' or (nm == 'menu_loop' and ms['menu_loop.l'] <= pc < ms['menu_loop.bz'] + 0x10): return nm
    return '?'
by = defaultdict(float)
for i, (k, pc, t) in enumerate(ev[:-1]):
    d = ev[i + 1][2] - t
    if k == 'I' and d < 1500: by[region(pc)] += d
tot = ev[-1][2] - ev[0][2]
print('frame %.0f cycles' % tot)
for k, v in sorted(by.items(), key=lambda x: -x[1]): print('  %-26s %5.0f' % (k, v))
print('  sum %.0f' % sum(by.values()))
