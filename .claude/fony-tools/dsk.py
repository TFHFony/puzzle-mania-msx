"""minimal FAT12 reader for MSX .dsk: python dsk.py list|extract <dsk> [outdir]"""
import sys, os, struct
def load(p):
    d = open(p,'rb').read()
    bps, spc, res, nfat, nroot, tot, _, spf = struct.unpack('<HBHBHHBH', d[11:24])
    fat = d[res*bps:(res+spf)*bps]
    rootstart = (res+nfat*spf)*bps
    datastart = rootstart + nroot*32
    return d, bps, spc, fat, rootstart, nroot, datastart
def chain(fat, c):
    out=[]
    while 2 <= c < 0xFF0:
        out.append(c)
        o = c*3//2
        v = fat[o] | fat[o+1]<<8
        c = (v>>4) if c&1 else (v&0xFFF)
    return out
def entries(p):
    d,bps,spc,fat,rs,nroot,ds = load(p)
    res=[]
    for i in range(nroot):
        e = d[rs+i*32: rs+i*32+32]
        if e[0]==0: break
        if e[0]==0xE5 or e[11]&0x08: continue
        name = e[:8].decode('latin1').strip()+('.'+e[8:11].decode('latin1').strip() if e[8:11].strip() else '')
        cl = struct.unpack('<H', e[26:28])[0]; sz = struct.unpack('<I', e[28:32])[0]
        data = b''.join(d[ds+(c-2)*spc*bps: ds+(c-1)*spc*bps] for c in chain(fat,cl))[:sz]
        res.append((name, sz, data))
    return res
if __name__=='__main__':
    es = entries(sys.argv[2])
    for n,s,_ in es: print(f'{n:14s}{s}')
    if sys.argv[1]=='extract':
        os.makedirs(sys.argv[3], exist_ok=True)
        for n,s,dt in es: open(os.path.join(sys.argv[3],n),'wb').write(dt)
