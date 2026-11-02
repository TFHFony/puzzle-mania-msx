"""one-time patch: build number on the specs screen (tools/build_number.txt, game/buildno.inc, game/spec.asm)"""
P = r'F:\MSX Projects\PMdev26'
BS = chr(92)
p = P + r'\tools\build_game.py'
s = open(p, encoding='utf8').read()
a = "    open(os.path.join(PROJ, 'game', 'cfg.inc'), 'w')"
assert s.count(a) == 1
new = ("    bnf = os.path.join(HERE, 'build_number.txt')                                  # the build number of the specs screen: counted by the full 128 MB builds only (lite, quick and test builds show none)\n"
       "    official = not (lite or quick or ascii16 or test0 or arg('--clipframes') or arg('--titleframes')) and os.path.basename(out) == 'PuzzleMania_128MB.rom'\n"
       "    bn = int(open(bnf).read().strip()) + 1 if official else 0\n"
       "    open(os.path.join(PROJ, 'game', 'buildno.inc'), 'w').write('sp_build: db \"%s\",0' + chr(10) % ('/ %d' % bn if bn else ''))\n")
# the % applies to the whole string: build it explicitly
new = new.replace("""'sp_build: db "%s",0' + chr(10) % ('/ %d' % bn if bn else '')""", """('sp_build: db "%s",0' % ('/ %d' % bn if bn else '')) + chr(10)""")
s = s.replace(a, new + a)
b = "    free = 0x3EE0 - len(code[:0x3EE0].rstrip(b'" + BS + "xff'))" + chr(10)
assert s.count(b) == 1, s.count(b)
s = s.replace(b, "    if bn:" + chr(10) + "        open(bnf, 'w').write('%d' % bn + chr(10))" + chr(10) + "        print('build number', bn)" + chr(10) + b)
open(p, 'w', encoding='utf8').write(s)

q = P + r'\game\spec.asm'
t = open(q, encoding='utf8').read()
t = t.replace('sp_l7:  db "ROM:",0', 'sp_l7:  db "ROM / BUILD:",0')
old = "        ld b,18\n        call .val\n        ld hl,sp_eyes\n"
assert t.count(old) == 1
t = t.replace(old, "        ld b,18\n        call .val\n        ld hl,sp_build                  ; \"/ 65\": the build number of the full 128 MB builds (game/buildno.inc, tools/build_number.txt)\n        ld d,18\n        ld e,25\n        ld a,0xF1\n        call boldcol\n        ld hl,sp_eyes\n")
assert 'sp_eyes: db "(.)(.)",0' in t
t = t.replace('sp_eyes: db "(.)(.)",0', '        INCLUDE "buildno.inc"\nsp_eyes: db "(.)(.)",0')
open(q, 'w', encoding='utf8').write(t)
print('ok')
