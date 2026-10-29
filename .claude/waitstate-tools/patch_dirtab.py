P = 'F:/MSX Projects/PMdev26/'
s = open(P + '.claude/waitstate-tools/tune_psg.py').read()
lines = s.split('\n')
for i, l in enumerate(lines):
    if l.startswith('ROM = '):
        lines[i] = "ROM = r'F:\\MSX Projects\\PMdev26\\.claude\\waitstate-tools\\wip\\PuzzleMania_keys_TEST.rom'"
open(P + '.claude/waitstate-tools/tune_psg.py', 'w').write('\n'.join(lines))
p = P + 'game/player.asm'
s = open(p, encoding='utf8').read()
a = "        db (d == 2) * 1 + (d == 8) * 3 + (d == 4) * 5 + (d == 1) * 7\n"
assert a in s
s = s.replace(a, "        db 0 - ((d == 2) * 1 + (d == 8) * 3 + (d == 4) * 5 + (d == 1) * 7)      ; (sjasmplus: true = -1)\n")
open(p, 'w', encoding='utf8').write(s)
print('ok')
