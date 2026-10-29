import subprocess, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
machine, key, tag = sys.argv[1], sys.argv[2], sys.argv[3]
env = dict(os.environ, KEY=key, SHOT=os.path.join(HERE, 'q_' + tag), OUT=os.path.join(HERE, 'q_' + tag + '.txt'), T0='9')
rom = r'F:\MSX Projects\PMdev26\PM_LogoMusic_4MB_ASCII16.rom'
p = subprocess.Popen([r'C:\Program Files\openMSX\openmsx.exe', '-machine', machine, '-cart', rom, '-romtype', 'ASCII16', '-script', os.path.join(HERE, 'run.tcl')], env=env)
try: p.wait(timeout=240)
except subprocess.TimeoutExpired: p.kill(); print('timeout', tag)
