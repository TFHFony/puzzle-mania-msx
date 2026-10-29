import re
HP = 'F:/MSX Projects/PMdev26/game/heads.inc'
def load():
    h = open(HP, encoding='utf8').read()
    return dict((m.group(1), int(m.group(2))) for m in re.finditer(r'(\w+) equ (\d+)', h))
def save(d, ns):
    others = [k for k in d if not re.match(r'[BN]\d+$', k)]
    keys = ['%s%d' % (c, i) for i in range(1, ns + 1) for c in 'BN'] + others
    open(HP, 'w', encoding='utf8').write(''.join('%s equ %d\n' % (k, d[k]) for k in keys))
def insert(after, count, guess=(4, 0)):
    """insert count new slots after slot `after`: entries above shift up"""
    d = load()
    ns = max(int(k[1:]) for k in d if re.match(r'B\d+$', k))
    nd = {k: v for k, v in d.items() if not re.match(r'[BN]\d+$', k)}
    for i in range(1, ns + 1):
        j = i if i <= after else i + count
        nd['B%d' % j] = d['B%d' % i]; nd['N%d' % j] = d['N%d' % i]
    for j in range(after + 1, after + 1 + count):
        nd['B%d' % j], nd['N%d' % j] = guess
    save(nd, ns + count)
def setbn(i, b, n):
    d = load(); d['B%d' % i] = b; d['N%d' % i] = n
    ns = max(int(k[1:]) for k in d if re.match(r'B\d+$', k)); save(d, ns)
