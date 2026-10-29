"""one-time patch: the PSG player also splits the joystick merge task (slot 7: 598 cycles in the game, 150 too long) into three slots, like the SCC player does; heads.inc is renumbered"""
import re
P = 'F:/MSX Projects/PMdev26/'
s = open(P + 'tools/gen_slots.py', encoding='utf8').read()
a = "if True:\n    import re as _re\n    hp = os.path.join(PROJ, 'game', 'heads.inc')\n"
assert s.count(a) == 1
b = """if True:
    import re as _re
    nt = []
    for cm, lines in tasks:                          # the joystick merge is too long for one slot (the SCC player cuts it in three, with sl_jc across the cuts)
        if cm.startswith('joystick: merge'):
            nt.append((cm + ' (1/3)', lines[:16] + ['ld (sl_jc),a']))
            nt.append((cm + ' (2/3)', ['ld a,(sl_jc)', 'ld c,a'] + lines[16:34]))
            nt.append((cm + ' (3/3)', ['ld a,(sl_jc)', 'ld c,a'] + lines[34:]))
        else:
            nt.append((cm, lines))
    tasks = nt
    NS = len(tasks)
    hp = os.path.join(PROJ, 'game', 'heads.inc')
"""
s = s.replace(a, b)
open(P + 'tools/gen_slots.py', 'w', encoding='utf8').write(s)
h = open(P + 'game/heads.inc', encoding='utf8').read()
d = dict((m.group(1), int(m.group(2))) for m in re.finditer(r'(\w+) equ (\d+)', h))
old = 55
new = {}
for i in range(1, old + 1):
    if i < 7:
        j = i
    elif i == 7:
        continue
    else:
        j = i + 2
    new['B%d' % j] = d['B%d' % i]; new['N%d' % j] = d['N%d' % i]
for j in (7, 8, 9):
    new['B%d' % j] = 4; new['N%d' % j] = 0
others = [k for k in d if not re.match(r'[BN]\d+$', k)]
keys = ['%s%d' % (c, i) for i in range(1, old + 3) for c in 'BN'] + others
open(P + 'game/heads.inc', 'w', encoding='utf8').write(''.join('%s equ %d\n' % (k, new[k] if k in new else d[k]) for k in keys))
print('ok')
