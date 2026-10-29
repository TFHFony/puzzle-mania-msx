"""one-time: removes the --logotest hooks from game/pm.asm and tools/build_game.py again (the test ROM is built standalone by build_logomusic.py); tools/gen_tvplay.py keeps main(DD, pfx, outname)"""
import os
BS = chr(92)
P = r'F:\MSX Projects\PMdev26'
p = P + r'\game\pm.asm'
s = open(p, encoding='utf8').read()
a = "        IF LOGOTEST\n        jp logotest                     ; test ROM: only the PM logo with its music (logotest.asm)\n        ENDIF\n"
assert s.count(a) == 1
s = s.replace(a, '')
b = '        IF TITLEVIDEO\n        IF LOGOTEST\ntvplay  equ tvd0_tvplay\n        INCLUDE "logotest.asm"\n        INCLUDE "tvplay_var.inc"\n        ELSE\n        INCLUDE "tvplay.inc"\n        ENDIF\n'
assert s.count(b) == 1
s = s.replace(b, '        IF TITLEVIDEO\n        INCLUDE "tvplay.inc"\n')
open(p, 'w', encoding='utf8').write(s)
p = P + r'\tools\build_game.py'
s = open(p, encoding='utf8').read()
a = 'TIETONLY equ 0' + BS + 'nLOGOTEST equ %d' + BS + 'nBUILDID'
assert s.count(a) == 1
s = s.replace(a, 'TIETONLY equ 0' + BS + 'nBUILDID')
a = "PLR_BANK, 1 if '--logotest' in sys.argv else 0, (0 if lite"
assert s.count(a) == 1
s = s.replace(a, "PLR_BANK, (0 if lite")
i = s.index("    if '--logotest' in sys.argv:")
j = s.index("    gen = 'WELCOME equ %d")
s = s[:i] + s[j:]
assert 'logotest' not in s
open(p, 'w', encoding='utf8').write(s)
for f in ('game/logotest.asm', 'game/tvplay_var.inc'):
    if os.path.exists(os.path.join(P, f)):
        os.remove(os.path.join(P, f))
print('ok')
