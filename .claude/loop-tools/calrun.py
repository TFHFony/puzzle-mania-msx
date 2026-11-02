import subprocess, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
rom, out, machine = sys.argv[1], sys.argv[2], sys.argv[3]
env = dict(os.environ, OUT=out, TS=os.environ.get('TS', '12 16'))
if len(sys.argv) > 4 and sys.argv[4] != '-': env['ZF'] = sys.argv[4]
p = subprocess.Popen([r'C:\Program Files\openMSX\openmsx.exe', '-machine', machine, '-cart', rom, '-romtype', os.environ.get('RT','ASCII16'), '-script', os.path.join(HERE, 'cal.tcl')], env=env)
try: p.wait(timeout=300)
except subprocess.TimeoutExpired: p.kill(); print('timeout')
