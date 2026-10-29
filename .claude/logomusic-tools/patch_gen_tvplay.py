"""one-time patch: tools/gen_tvplay.py gets main(DD, pfx, outname): DD cycles less per loop, pfx before the global labels, another output file (the title video test ROM)"""
import re
p = r'F:\MSX Projects\PMdev26\tools\gen_tvplay.py'
s = open(p, encoding='utf8').read()
assert 'DD=0' not in s
assert s.count('def main():') == 1
s = s.replace('def main():', "def main(DD=0, pfx='', outname='tvplay.inc'):          # DD: cycles less per loop (a faster loop for a machine with VDP wait states), pfx: before the global labels (several copies in one program)", 1)
n = s.count('B(PERIOD - ')
assert n == 6, n
s = s.replace('B(PERIOD - ', 'B(PERIOD - DD - ')
old = "    open(os.path.join(PROJ, 'game', 'tvplay.inc'), 'w').write('\\n'.join(L) + '\\n')\n    print('tvplay.inc', len(L), 'lines')\n"
assert old in s
new = ("    txt = '\\n'.join(L) + '\\n'\n"
       "    if pfx:\n"
       "        txt = re.sub(r'\\b(tvplay|tv_frame0|tv_frame|tv_row|tv_end|tv_exit)\\b', pfx + r'\\1', txt)\n"
       "    open(os.path.join(PROJ, 'game', outname), 'w').write(txt)\n"
       "    print(outname, len(L), 'lines')\n")
s = s.replace(old, new)
s = s.replace('import os, json\n', 'import os, json, re\n', 1)
open(p, 'w', encoding='utf8').write(s)
print('ok')
