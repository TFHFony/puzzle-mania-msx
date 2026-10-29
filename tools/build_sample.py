"""Short test ROMs that only play the in-game music (PM.wav), one per PSG table, for a real MSX (1.4 MB, NEO16):
   python tools/build_sample.py            -> PM_Sample_JOINT.rom, PM_Sample_AY.rom, PM_Sample_YM.rom
   python tools/build_sample.py --curve ay  (one table)"""
import os, sys, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
NAMES = {'joint': 'JOINT (AY + YM)', 'ay': 'AY-3-8910', 'ym': 'YM2149'}


def build(curve, scale=0):
    os.environ['PSG_CURVE'] = curve
    os.environ['PSG_SCALE'] = str(scale)
    arg = lambda name, default=None: sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default
    open(os.path.join(PROJ, 'game', 'opts.inc'), 'w').write('SFRAMED equ %d\nSJOB equ %d\n' % (1 if '--framed' in sys.argv else 0, 1 if '--job' in sys.argv else 0))
    open(os.path.join(PROJ, 'game', 'cfg.inc'), 'w').write('ASCII16 equ 0\nDIAG equ 0\nFREE equ 0\nTITLEVIDEO equ 0\nTVBANK equ 0\nTVFRAMES equ 0\nPLR_BANK equ 254\nTIETONLY equ 0\nBUILDID equ 0\nSCC equ 0\nMSX2PAL equ 0\nPBOFFS equ 0\nWELCOME2 equ 0\n')
    sys.path.insert(0, HERE)
    subprocess.run([sys.executable, os.path.join(HERE, 'gen_slots.py')], check=True, capture_output=True)
    import music
    pm = music.track('pm', os.path.join(PROJ, 'PM.wav'), gapk=int(arg('--fixk', '0')))
    nb = len(pm) // 16384
    clock = json.load(open(os.path.join(HERE, 'clock.json')))
    gdir = os.path.join(PROJ, 'game')
    open(os.path.join(gdir, 'clk.inc'), 'w').write('MDELAY equ %d\nFI_PAL equ %d\nFI_NTSC equ %d\n' % (clock['MDELAY'], clock['FI_PAL'], clock['FI_NTSC']))
    open(os.path.join(gdir, 'sgen.inc'), 'w').write('mustab:\n        dw 1,%d\n        db 1,%d,%d,%d\ns_table: db "%s",0\n' % (1 + nb, int(arg('--fixk', '0')), int(arg('--fixkb', arg('--fixk', '0'))), int(arg('--fixkb', arg('--fixk', '0'))), NAMES[curve]))
    pt = ''
    for s, t in enumerate(music.fade_sets()):
        for ch in range(3):
            vals = [x[ch] for x in t]
            pt += ('tabA:\n' if s == 0 and ch == 0 else '') + ''.join('        db ' + ','.join(str(v) for v in vals[i:i + 16]) + '\n' for i in range(0, 256, 16))
    open(os.path.join(gdir, 'psgtab.inc'), 'w').write(pt)
    open(os.path.join(gdir, 'plrsize.inc'), 'w').write('PLR_SIZE equ 0\n')
    sj = r'F:\MSX Projects\Dev27\.claude\msx-video-tools\sjasmplus\sjasmplus-1.24.0.win\sjasmplus.exe'
    r = subprocess.run([sj, '--nologo', 'sample.asm'], cwd=gdir, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout + r.stderr); sys.exit('assembly failed')
    code = open(os.path.join(gdir, 'sample.bin'), 'rb').read()
    out = os.path.join(PROJ, arg('--out', 'PM_Sample_%s%s.rom' % (curve.upper(), ('_s%g' % scale) if scale else '')))
    with open(out, 'wb') as f:
        f.write(code); f.write(pm)
    print(out, os.path.getsize(out), 'bytes,', nb, 'banks of music')


if __name__ == '__main__':
    if '--curve' in sys.argv:
        build(sys.argv[sys.argv.index('--curve') + 1], float(sys.argv[sys.argv.index('--scale') + 1]) if '--scale' in sys.argv else 0)
    else:
        for c in ('joint', 'ay', 'ym'):
            subprocess.run([sys.executable, __file__, '--curve', c], check=True)
