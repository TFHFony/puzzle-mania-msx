import subprocess, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
rom, out, at, machine = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
env = dict(os.environ, OUT=out, AT=at)
if len(sys.argv) > 5: env['ZF'] = sys.argv[5]
p = subprocess.Popen([r'C:\Program Files\openMSX\openmsx.exe', '-machine', machine, '-cart', rom, '-romtype', os.environ.get('RT','ASCII16'), '-script', os.path.join(HERE, 'lt_p2.tcl')], env=env)
try: p.wait(timeout=300)
except subprocess.TimeoutExpired: p.kill(); print('timeout')
