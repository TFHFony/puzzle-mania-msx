"""one-time patch of tools/build_game.py: the banks of the title video variants (TVVB) and of the zeros for the calibration (TVZERO), --tietonly / --caldbg"""
p = r'F:\MSX Projects\PMdev26\tools\build_game.py'
s = open(p).read()
assert 'TVVB' not in s


def rep(a, b):
    global s
    assert a in s, a
    s = s.replace(a, b, 1)


rep("PLR_BANK = 254\n", "PLR_BANK = 254\nTVVB, TVZERO = PLR_BANK - 3, PLR_BANK - 2        # the variants of the title video player (1 KB each, tools/gen_tvvar.py) and a bank of zeros (the calibration run)\n")
rep("(PLR_BANK - (1 if scc else 0) - len(banks) if ascii16 else None))", "(PLR_BANK - 2 - (1 if scc else 0) - len(banks) if ascii16 else None))")
rep("<= (PLR_BANK if ascii16 else 4096 if lite else 16384), b", "<= (PLR_BANK - 2 if ascii16 else 4096 if lite else 16384), b")
rep("TIETONLY equ 0\\nBUILDID equ %d", "TIETONLY equ %d\\nTVVB equ %d\\nTVZERO equ %d\\nCALDBG equ %d\\nBUILDID equ %d")
rep("PLR_BANK, (0 if lite else 2 if arg('--clipframes') else 1), 1 if '--scc'", "PLR_BANK, 1 if '--tietonly' in sys.argv else 0, TVVB, TVZERO, 1 if '--tietonly' in sys.argv or '--caldbg' in sys.argv else 0, (0 if lite else 2 if arg('--clipframes') else 1), 1 if '--scc'")
rep("    r = subprocess.run([SJASM, '--nologo', '--sym=pm.sym', 'pm.asm']",
    "    subprocess.run([sys.executable, os.path.join(HERE, 'gen_tvvar.py')], check=True, capture_output=True)       # the variants of the title video player\n"
    "    r = subprocess.run([SJASM, '--nologo', 'tvvar.asm'], cwd=gdir, capture_output=True, text=True)\n"
    "    if r.returncode != 0:\n        print(r.stdout + r.stderr)\n        sys.exit('assembly of the title video variants failed')\n"
    "    tvvar = open(os.path.join(gdir, 'tvvar.bin'), 'rb').read()\n    assert len(tvvar) == 16384\n"
    "    r = subprocess.run([SJASM, '--nologo', '--sym=pm.sym', 'pm.asm']")
rep("len(banks) < PLR_BANK\n", "len(banks) < TVVB\n")
rep("(PLR_BANK - 1 - len(banks) - (sum(nb) if ascii16 else 0)))", "(TVVB - len(banks) - (sum(nb) if ascii16 else 0)))\n        f.write(tvvar)                  # bank TVVB\n        f.write(bytes(16384))           # bank TVZERO")
open(p, 'w').write(s)
print('patched')
