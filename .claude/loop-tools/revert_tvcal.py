"""reverts the title video calibration in the game sources (the old logo loop `tvplay` again); the calibration files are moved to .claude/loop-tools/tvcal-archive"""
import os, shutil
P = r'F:\MSX Projects\PMdev26'
G = P + r'\game'; T = P + r'\tools'; A = P + r'\.claude\loop-tools\tvcal-archive'
os.makedirs(A, exist_ok=True)


def edit(path, pairs):
    s = open(path).read()
    for a, b in pairs:
        assert a in s, (path, a[:60])
        s = s.replace(a, b, 1)
    open(path, 'w').write(s)


edit(G + r'\equ.inc', [("v_tvc    equ 0xC1E8     ; title video: 1 = the loop speed was measured (tvcal.asm)\nv_tvi    equ 0xC1E9     ; the variant of the loop that fits this machine\n", "")])
edit(G + r'\pm.asm', [('        INCLUDE "tvcal.inc"\n        INCLUDE "tvcal.asm"\n', '        INCLUDE "tvplay.inc"\n')])
edit(G + r'\screens.asm', [("        call tvcalib                    ; (once) the speed of the loop of this machine\n", ""),
                           ("        call tvrun                      ; video and music in one stream (a variant of tvplay.inc, tvcal.asm)", "        call tvplay                     ; video and music in one stream (tvplay.inc)")])
edit(T + r'\build_game.py', [
    ("PLR_BANK = 254\nTVVB, TVZERO = PLR_BANK - 3, PLR_BANK - 2        # the variants of the title video player (1 KB each, tools/gen_tvvar.py) and a bank of zeros (the calibration run)\n", "PLR_BANK = 254\n"),
    ("(PLR_BANK - 2 - (1 if scc else 0) - len(banks) if ascii16 else None))", "(PLR_BANK - (1 if scc else 0) - len(banks) if ascii16 else None))"),
    ("<= (PLR_BANK - 2 if ascii16 else 4096 if lite else 16384), b", "<= (PLR_BANK if ascii16 else 4096 if lite else 16384), b"),
    ("TIETONLY equ %d\\nTVVB equ %d\\nTVZERO equ %d\\nCALDBG equ %d\\nBUILDID equ %d", "TIETONLY equ 0\\nBUILDID equ %d"),
    ("PLR_BANK, 1 if '--tietonly' in sys.argv else 0, TVVB, TVZERO, 1 if '--tietonly' in sys.argv or '--caldbg' in sys.argv else 0, (0 if lite", "PLR_BANK, (0 if lite"),
    ("    subprocess.run([sys.executable, os.path.join(HERE, 'gen_tvvar.py')], check=True, capture_output=True)       # the variants of the title video player\n"
     "    r = subprocess.run([SJASM, '--nologo', 'tvvar.asm'], cwd=gdir, capture_output=True, text=True)\n"
     "    if r.returncode != 0:\n        print(r.stdout + r.stderr)\n        sys.exit('assembly of the title video variants failed')\n"
     "    tvvar = open(os.path.join(gdir, 'tvvar.bin'), 'rb').read()\n    assert len(tvvar) == 16384\n", ""),
    ("len(banks) < TVVB\n", "len(banks) < PLR_BANK\n"),
    ("(TVVB - len(banks) - (sum(nb) if ascii16 else 0)))\n        f.write(tvvar)                  # bank TVVB\n        f.write(bytes(16384))           # bank TVZERO", "(PLR_BANK - 1 - len(banks) - (sum(nb) if ascii16 else 0)))"),
])
shutil.copy(P + r'\.claude\loop-tools\gen_tvplay.py.orig', T + r'\gen_tvplay.py')
shutil.copy(P + r'\.claude\loop-tools\tvplay.inc.orig', G + r'\tvplay.inc')
for f in ('tvcal.asm', 'tvcal.inc', 'tvtab.inc', 'tvvar.asm', 'tvvar.bin'):
    if os.path.exists(G + '\\' + f): shutil.move(G + '\\' + f, A + '\\' + f)
for f in ('gen_tvvar.py', 'tvcal.json'):
    if os.path.exists(T + '\\' + f): shutil.move(T + '\\' + f, A + '\\' + f)
print('reverted')
