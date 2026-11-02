"""frames_msx1 / frames_msx2 -> jigsaw_msx1_msx2_<fps>fps.mp4 (left MSX1, right MSX2, 2x nearest) and the same at half the frame rate (every other frame, held)
usage: python make_mp4.py [FPS=25]"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, 'preview'); fps = float(sys.argv[1]) if len(sys.argv) > 1 else 25.0
for div in (1, 2):
    sel = r"select='not(mod(n\,%d))'," % div if div > 1 else ''
    out = os.path.join(P, 'jigsaw_msx1_msx2_%gfps.mp4' % (fps / div))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(fps), '-i', os.path.join(P, 'frames_msx1', '%03d.png'), '-framerate', str(fps), '-i', os.path.join(P, 'frames_msx2', '%03d.png'),
                    '-filter_complex', '[0][1]hstack,' + sel + 'setpts=N/(%g*TB),scale=1024:384:flags=neighbor' % (fps / div),
                    '-r', '%g' % (fps / div), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '14', out], check=True)
    print(out)
