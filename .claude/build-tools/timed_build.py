"""runs tools/build_game.py with timers round the heavy stages; usage: python timed_build.py <build_game args>"""
import sys, os, time, runpy, importlib
PROJ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(PROJ, 'tools')); sys.path.insert(0, r'F:\MSX Projects\Dev27\msx1-video-player\tools')
T = []
def wrap(modname, names):
    m = importlib.import_module(modname)
    for n in names:
        f = getattr(m, n)
        def w(*a, __f=f, __n=modname + '.' + n, **k):
            t = time.time(); r = __f(*a, **k); T.append((__n, time.time() - t)); return r
        setattr(m, n, w)
wrap('title_video', ['build', 'frames16', 'build16'])
wrap('music', ['track16', 'track'] if hasattr(importlib.import_module('music'), 'track') else ['track16'])
wrap('jingle', ['psg', 'scc', 'boom'])
wrap('fony_video', ['build'])
wrap('choice_thumbs', ['build'])
wrap('xxxl_logo', ['banks'])
wrap('memory_cards', ['build'])
if __name__ == "__main__":
    import build_game
    for n in ('build_assets', 'build_msx2_assets', 'build_jigsaw'):
        f = getattr(build_game, n)
        def w(*a, __f=f, __n=n, **k):
            t = time.time(); r = __f(*a, **k); T.append(('build_game.' + n, time.time() - t)); return r
        setattr(build_game, n, w)
    sys.argv = ['build_game.py'] + sys.argv[1:]
    t0 = time.time()
    try:
        build_game.main()
    finally:
        print('\n== TIMES (s) ==')
        for n, s in T: print('%7.1f  %s' % (s, n))
        print('%7.1f  total' % (time.time() - t0))
