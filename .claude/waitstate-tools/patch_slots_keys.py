"""one-time patch: the derived key state of the game moves into work slots of the player (they run inside sample iterations, so the gap of the music stays short):
  mus_any   = anykey (NZ: a key that the game uses, or the joystick, is down)
  mus_sel   = SELECT went down (latched, the consumer clears it)
  mus_dkey  = getkey (orthogonal direction 1,3,5,7 on a press / auto repeat, else 0)
  mus_ke    = keyedge bits L, C, T (latched, the consumer clears it)
8 new slots are inserted before the last slot of tools/gen_slots.py; heads.inc gets their burns (to be tuned); the callers get the vars (the old code stays for a game without music)."""
import re
P = 'F:/MSX Projects/PMdev26/'
s = open(P + 'tools/gen_slots.py', encoding='utf8').read()
assert 'mus_any' not in s
a = "LAST = ('page 1 shows the ROM bank of the job"
assert s.count(a) == 1
new = '''task('derived keys 1/8: anykey part 1 (rows 8, 7, 3)', [
    'ld a,(k8)', 'or 0x0E', 'ld b,a', 'ld a,(k7)', 'or 0x7B', 'and b', 'ld b,a', 'ld a,(k3)', 'or 0xDE', 'and b', 'ld (mus_t2),a'])
task('derived keys 2/8: anykey part 2 (rows 4, 5, the joystick): mus_any = NZ when a key is down', [
    'ld a,(mus_t2)', 'ld b,a', 'ld a,(k4)', 'or 0xF5', 'and b', 'ld b,a', 'ld a,(k5)', 'or 0xFD', 'and b', 'ld b,a', 'ld a,(joy)', 'or 0xC0', 'and b', 'inc a', 'ld (mus_any),a'])
task('derived keys 3/8: SELECT went down (mus_sel, latched; the consumer clears it)', [
    'ld a,(k7)', 'and 0x40', 'ld b,a', 'ld a,(sel_prev)', 'ld c,a', 'ld a,b', 'ld (sel_prev),a', 'or a', 'jr nz,.pae', 'ld a,c', 'or a', 'jr z,.pae', 'ld a,1', 'ld (mus_sel),a', '.pae:'])
task('derived keys 4/8: the cursor keys as an index (the keys that are down, the nibble of row 8)', [
    'ld a,(k8)', 'cpl', 'and 0xF0', 'rrca', 'rrca', 'rrca', 'rrca', 'ld (mus_t3),a'])
task('derived keys 5/8: one cursor key = 1 up, 3 right, 5 down, 7 left (getdir), else 0', [
    'ld a,(mus_t3)', 'ld e,a', 'ld d,0', 'ld ix,dirtab', 'add ix,de', 'ld a,(ix+0)', 'ld (mus_dk),a'])
task('derived keys 6/8: getkey: the direction on a press and at the auto repeat (mus_dkey), else 0', [
    'ld a,(mus_dk)', 'ld b,a', 'and 1', 'jr z,.n1', 'ld a,(v_pdir)', 'cp b', 'jr nz,.n2', 'ld a,(v_rep)', 'dec a', 'jr nz,.n3', 'ld a,4', 'ld (v_rep),a', 'ld a,b', 'jr .n4',
    '.n3:', 'ld (v_rep),a', 'xor a', 'jr .n4', '.n2:', 'ld a,b', 'ld (v_pdir),a', 'ld a,16', 'ld (v_rep),a', 'ld a,b', 'jr .n4', '.n1:', 'xor a', 'ld (v_pdir),a', '.n4:', 'ld (mus_dkey),a'])
task('derived keys 7/8: the keys L, C, T (keyedge, part 1)', [
    'ld a,(k4)', 'cpl', 'rrca', 'and 1', 'ld c,a', 'ld a,(k3)', 'cpl', 'and 1', 'add a,a', 'or c', 'ld c,a',
    'ld a,(k5)', 'cpl', 'rrca', 'and 1', 'add a,a', 'add a,a', 'or c', 'ld (mus_t4),a'])
task('derived keys 8/8: the keys L, C, T that went down since the last frame (mus_ke, latched; the consumer clears it)', [
    'ld a,(mus_t4)', 'ld c,a', 'ld a,(p_ek)', 'cpl', 'and c', 'ld b,a', 'ld a,c', 'ld (p_ek),a', 'ld a,(mus_ke)', 'or b', 'ld (mus_ke),a'])
'''
s = s.replace(a, new + a)
old = "re.sub(r'\\.(c0|c1|c2|n1|n2|n3|n4|n5|pae|pbe|pce|pde)\\b'"
assert old in s, 'fmt regexp'
open(P + 'tools/gen_slots.py', 'w', encoding='utf8').write(s)

pl = open(P + 'game/player.asm', encoding='utf8').read()
pl = pl.replace("wxtab:", """dirtab: ; the cursor keys that are down (index: bit 0 left, 1 up, 2 down, 3 right of row 8 inverted, high nibble) -> 1 up, 3 right, 5 down, 7 left; two keys or none: 0
        REPT 16, d
        db (d == 2) * 1 + (d == 8) * 3 + (d == 4) * 5 + (d == 1) * 7
        ENDR

wxtab:""", 1)
open(P + 'game/player.asm', 'w', encoding='utf8').write(pl)

e = open(P + 'game/wtequ.inc', encoding='utf8').read()
e += """mus_any equ 0xC396      ; (slots of the player) NZ = a key that the game uses, or the joystick, is down
mus_sel equ 0xC397      ; SELECT went down (latched: the consumer clears it)
mus_dk  equ 0xC398      ; one cursor key: 1 up, 3 right, 5 down, 7 left, else 0
mus_ke  equ 0xC399      ; the keys L, C, T that went down (bits 0..2, latched: the consumer clears it)
mus_t2  equ 0xC39A      ; temporaries of the slots
mus_t3  equ 0xC39B
mus_t4  equ 0xC39C
mus_dkey equ 0xC39D     ; getkey: the direction on a press / auto repeat, else 0
"""
open(P + 'game/wtequ.inc', 'w', encoding='utf8').write(e)

# heads.inc: the old last slot (47) becomes 55, the new slots 47..54 get a first guess (tuned afterwards)
h = open(P + 'game/heads.inc', encoding='utf8').read()
h = re.sub(r'^B47 equ (\d+)\nN47 equ (\d+)\n', lambda m: 'B47 equ 4\nN47 equ 0\nB48 equ 4\nN48 equ 0\nB49 equ 4\nN49 equ 0\nB50 equ 4\nN50 equ 0\nB51 equ 4\nN51 equ 0\nB52 equ 4\nN52 equ 0\nB53 equ 4\nN53 equ 0\nB54 equ 4\nN54 equ 0\nB55 equ %s\nN55 equ %s\n' % (m.group(1), m.group(2)), h, flags=re.M)
assert 'B55 equ' in h
open(P + 'game/heads.inc', 'w', encoding='utf8').write(h)
print('ok')
