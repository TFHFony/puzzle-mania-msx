"""docs/MANUAL.md -> PuzzleManiaXXXL_Manual_v1.0.pdf (markdown -> HTML with a print stylesheet -> headless Edge)"""
import os, sys, subprocess, markdown
PROJ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
src = os.path.join(PROJ, 'docs', 'MANUAL.md')
html = os.path.join(PROJ, 'docs', '_manual_print.html')
pdf = os.path.join(PROJ, 'PuzzleManiaXXXL_Manual_v1.0.pdf')
body = markdown.markdown(open(src, encoding='utf-8').read(), extensions=['tables', 'sane_lists'])
css = """
@page { size: A4; margin: 16mm 14mm; }
body { font-family: Segoe UI, Arial, sans-serif; font-size: 10.5pt; line-height: 1.45; color: #111; }
h1 { font-size: 24pt; margin: 0 0 4pt; } h2 { font-size: 15pt; margin: 18pt 0 6pt; border-bottom: 1px solid #bbb; padding-bottom: 2pt; break-after: avoid; }
img { max-width: 100%; height: auto; image-rendering: auto; border: 1px solid #ccc; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0; break-inside: avoid; }
td, th { border: 1px solid #ccc; padding: 4pt 6pt; vertical-align: top; } th:empty { display: none; }
td img { display: block; margin: 0 auto 3pt; }
blockquote { border-left: 4px solid #c33; margin: 8pt 0; padding: 4pt 10pt; background: #fbeaea; }
code { background: #f1f1f1; padding: 0 3pt; border-radius: 2pt; } hr { border: 0; border-top: 1px solid #ccc; }
p > img { display: block; max-width: 60%; margin: 6pt 0; }
"""
open(html, 'w', encoding='utf-8').write('<!doctype html><html><head><meta charset="utf-8"><title>Puzzle Mania XXXL - manual</title><style>%s</style></head><body>%s</body></html>' % (css, body))
edge = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
subprocess.run([edge, '--headless', '--disable-gpu', '--no-pdf-header-footer', '--print-to-pdf=' + pdf, 'file:///' + html.replace(os.sep, '/')], check=True, timeout=120)
os.remove(html)
print(pdf, os.path.getsize(pdf))
