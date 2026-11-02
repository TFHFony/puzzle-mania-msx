"""one-time patch: the title video player with a calibrated variant (equ.inc, pm.asm, screens.asm)"""
P = r'F:\MSX Projects\PMdev26\game'
p = P + r'\equ.inc'; s = open(p).read()
assert 'v_tvc' not in s
s = s.replace("tv_f    equ 0xC1EF", "v_tvc    equ 0xC1E8     ; title video: 1 = the loop speed was measured (tvcal.asm)\nv_tvi    equ 0xC1E9     ; the variant of the loop that fits this machine\ntv_f    equ 0xC1EF", 1)
open(p, 'w').write(s)
p = P + r'\pm.asm'; s = open(p).read()
assert '        INCLUDE "tvplay.inc"\n' in s
s = s.replace('        INCLUDE "tvplay.inc"\n', '        INCLUDE "tvcal.inc"\n        INCLUDE "tvcal.asm"\n', 1)
open(p, 'w').write(s)
p = P + r'\screens.asm'; s = open(p).read()
a = "        call tvplay                     ; video and music in one stream (tvplay.inc)"
assert a in s
s = s.replace(a, "        call tvrun                      ; video and music in one stream (a variant of tvplay.inc, tvcal.asm)", 1)
b = "        inc a\n        ld (v_tit),a\n        ld a,PAL_TMS\n        call need_pal\n        ld hl,TITLEV"
assert b in s
s = s.replace(b, "        inc a\n        ld (v_tit),a\n        call tvcalib                    ; (once) the speed of the loop of this machine\n        ld a,PAL_TMS\n        call need_pal\n        ld hl,TITLEV", 1)
open(p, 'w').write(s)
print('patched')
