"""one-time patch: tools/build_game.py assembles game/wtest.asm into the bank SELFTEST and generates tvplay16w.inc with the SCC loop"""
fn = 'F:/MSX Projects/PMdev26/tools/build_game.py'
s = open(fn, encoding='utf8').read()
a = "    banks = build_assets(choices, '--fresh' in sys.argv)\n"
assert s.count(a) == 1
s = s.replace(a, a + """    r = subprocess.run([SJASM, '--nologo', 'wtest.asm'], cwd=os.path.join(PROJ, 'game'), capture_output=True, text=True)      # the VDP wait state test: it lives in the bank SELFTEST behind the signature (screens.asm wt_go copies it to the RAM)
    if r.returncode != 0:
        print(r.stdout + r.stderr)
        sys.exit('assembly of the wait state test failed')
    banks[SELFTEST] = pad(b'NEO16OK!'.ljust(16, bytes(1)) + open(os.path.join(PROJ, 'game', 'wtest.bin'), 'rb').read())
""")
b = "        subprocess.run([sys.executable, os.path.join(HERE, 'gen_tvplay16.py')], check=True, capture_output=True)\n"
assert s.count(b) == 1
s = s.replace(b, b + "        subprocess.run([sys.executable, os.path.join(HERE, 'gen_tvplay16.py'), '--wait'], check=True, capture_output=True)       # (and the loop for a machine with a VDP wait state)\n")
open(fn, 'w', encoding='utf8').write(s)
print('ok')
