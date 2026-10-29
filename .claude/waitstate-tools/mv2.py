import subprocess, os, time, sys
import numpy as np
from collections import Counter
HERE=os.path.dirname(os.path.abspath(__file__))
rom=sys.argv[1]; tag=sys.argv[2]
out=os.path.join(HERE,'mv2_%s.txt'%tag).replace(chr(92),'/')
if os.path.exists(out): os.remove(out)
env=dict(os.environ,OUT=out)
p=subprocess.Popen([r'C:\Program Files\openMSX\openmsx.exe','-machine','Philips_VG_8020','-cart',rom,'-romtype','NEO-16','-script',os.path.join(HERE,'mv2.tcl')],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
t0=time.time()
for chk in (20,40,60,90):
    while time.time()-t0<chk and p.poll() is None and not os.path.exists(out): time.sleep(1)
    print('check at %ds: running=%s output=%s'%(chk,p.poll() is None,os.path.exists(out)),flush=True)
    if os.path.exists(out) or p.poll() is not None: break
time.sleep(1)
if p.poll() is None: p.kill(); print('killed')
R=[l.split() for l in open(out).read().splitlines()]
t=np.array([float(r[0]) for r in R]); sk=np.array([int(r[1]) for r in R]); lv=np.array([int(r[3]) for r in R]); q=np.array([int(r[4]) for r in R]); sz=[int(r[5]) for r in R]; trk=[int(r[6]) for r in R]
per=np.diff(t)*1000
print(tag,'frames',len(per),'size',sz[-1],'track',trk[-1],'period mean %.3f min %.3f max %.3f'%(per.mean(),per.min(),per.max()))
print(' skip histogram',sorted(Counter(sk[1:]).items()),' level',sorted(Counter(lv[1:]).items()))
print(' extra skipped samples per second: %.1f (idle = 2 per frame)'%(((sk[1:]-2).clip(0).sum())/(t[-1]-t[0])))
