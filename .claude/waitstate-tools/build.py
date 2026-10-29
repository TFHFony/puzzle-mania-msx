import subprocess, sys, hashlib, os
HERE = os.path.dirname(os.path.abspath(__file__))
SJ = r'F:\MSX Projects\Dev27\.claude\msx-video-tools\sjasmplus\sjasmplus-1.24.0.win\sjasmplus.exe'
r = subprocess.run([SJ, '--nologo', '--lst=waitstate.lst', '--sym=waitstate.sym', 'waitstate.asm'], cwd=HERE, capture_output=True, text=True)
print(r.stdout + r.stderr)
if r.returncode: sys.exit('assembly failed')
d = open(os.path.join(HERE, 'waitstate.bin'), 'rb').read()
assert len(d) == 16384
out = os.path.join(HERE, '..', '..', 'PM_WaitState_16KB.rom')
open(out, 'wb').write(d)
print(os.path.abspath(out), len(d), hashlib.md5(d).hexdigest())
