"""Builds the tutorial in every combination of language and level and serves it locally.

    python build.py            # render + preview server
    python build.py --no-serve # render only

Result:
    docs/index.html          -> redirects to de/, en/, sv/, no/ or da/ by browser language
    docs/<lang>/index.html   -> start page (profile root): choose a level
    docs/<lang>/<level>/     -> beg, int, exp

Each run has two profiles active, one from each group (see _quarto.yml), e.g.
    quarto render --profile int,english --output-dir docs/en/int
The start page of each language is rendered FIRST: Quarto empties the output
directory when rendering, and docs/de/ contains the level folders.

Afterwards the rendered pages are post-processed (no JavaScript, see postprocess()):
Quarto cannot link across profiles, so the _quarto-<language>.yml files only contain
placeholders, which are turned into fixed relative links here:
    #sprache-de ... #sprache-da  -> the same page in the other language
    #niveau-beg/-int/-exp        -> start page of that level in the current language
    navbar title                 -> start page of the language (Quarto only knows the profile root)
In addition, an "Expand all" button is added at the bottom of the sidebar (a checkbox,
the effect comes from CSS in styles.css). Neither exists in `quarto preview`.
"""
import http.server
import os
import re
import socketserver
from urllib.parse import quote
import subprocess
import sys
import webbrowser

BASE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(BASE, "docs")
LANGUAGES = {"de": "deutsch", "en": "english", "sv": "svenska", "no": "norsk", "da": "dansk"}
# level -> start page
LEVELS = {
    "beg": "Qmd Files/Example Page/index_beg.html",
    "int": "Qmd Files/Getting Started/getting_started.html",
    "exp": "Qmd Files/Tipps and Tricks/index_exp.html",
}

REDIRECT = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>Weiterleitung / Redirect</title>
<script>
  // browser language -> folder; Norwegian comes as nb, nn or no. English otherwise.
  var FOLDER = { de: "de", en: "en", sv: "sv", nb: "no", nn: "no", no: "no", da: "da" };
  var lang = (navigator.language || "de").slice(0, 2).toLowerCase();
  window.location.replace((FOLDER[lang] || "en") + "/");
</script>
<noscript><meta http-equiv="refresh" content="0; url=de/"></noscript>
</head>
<body>
<p><a href="de/">Deutsch</a> · <a href="en/">English</a> · <a href="sv/">Svenska</a> · <a href="no/">Norsk</a> · <a href="da/">Dansk</a></p>
</body>
</html>
"""

# Standalone page without Quarto: the address it is served under is arbitrary,
# so the script looks for the root of the tutorial itself.
NOT_FOUND = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>404 – Seite nicht gefunden / Page Not Found</title>
<style>
  body { font-family: system-ui, sans-serif; text-align: center; padding: 3rem 1rem; }
  a { display: inline-block; margin-top: 1rem; padding: .5rem 1rem; border-radius: .375rem;
      background: #0d6efd; color: #fff; text-decoration: none; }
</style>
</head>
<body>
<h1>🚧 🔍</h1>
<p><strong>Diese Seite gibt es nicht, oder der Link hat nicht funktioniert.</strong></p>
<p><strong>This page does not exist, or the link did not work.</strong></p>
<a id="home-btn" href="/">← Zurück zum Tutorial / Back to the Tutorial</a>
<script>
  (function () {
    var root = "/";
    if (location.hostname.endsWith("github.io")) {
      var seg = location.pathname.split("/").filter(Boolean)[0];
      if (seg) root = "/" + seg + "/";
    }
    document.getElementById("home-btn").href = root;
  })();
</script>
</body>
</html>
"""

LEVEL_INDEX = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="0; url={target}">
<title>Weiterleitung / Redirect</title></head>
<body><p><a href="{target}">{target}</a></p></body></html>
"""


def render(profile, output_dir):
    command = ["quarto", "render", "--profile", profile, "--output-dir", output_dir]
    print(f"\n  > {' '.join(command)}")
    run = subprocess.run(command, cwd=BASE, capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    for line in (run.stdout + run.stderr).splitlines():
        if line.strip():
            print(f"    {line}")
    if run.returncode != 0:
        print(f"  ERROR with --profile {profile}. Aborting.")
        sys.exit(1)


LANGUAGE_LINK = re.compile(r'<a class="dropdown-item" href="[^"]*#sprache-(de|en|sv|no|da)">')
LEVEL_LINK = re.compile(r'<a class="nav-link" href="[^"]*#niveau-(beg|int|exp)">')
# the same placeholders as links in the text (start page: "start with the first steps")
LEVEL_TEXT_LINK = re.compile(r'<a href="[^"]*#niveau-(beg|int|exp)">')
TITLE_LINK = re.compile(r'<a [^>]*class="navbar-brand[^"]*"[^>]*>')
BUTTON_TEXT = {
    "de": ("Alle ausklappen", "Alle einklappen"),
    "en": ("Expand all", "Collapse all"),
    "sv": ("Fäll ut alla", "Fäll ihop alla"),
    "no": ("Fold ut alle", "Fold sammen alle"),
    "da": ("Fold alle ud", "Fold alle sammen"),
}
# end of the sidebar: </ul> of the menu, </div> of the menu container, </nav>
SIDEBAR_END = re.compile(r"(\s*</ul>\s*)(</div>\s*</nav>)")


def postprocess(html, lang, rel):
    """rel: path of the page below docs/<lang>/, e.g. "int/Qmd Files/Getting Started/beg_book_1.html"."""
    depth = rel.count("/")
    to_lang_root = "../" * depth          # from the page to docs/<lang>/
    level = rel.split("/", 1)[0] if "/" in rel else None

    def language_link(m):
        target = m.group(1)
        # no #anchor: heading ids differ between the languages
        href = "../" + to_lang_root + target + "/" + quote(rel)
        if target == lang:
            return f'<a class="dropdown-item active" aria-current="true" href="{href}">'
        return f'<a class="dropdown-item" href="{href}">'

    def level_link(m):
        target = m.group(1)
        href = to_lang_root + target + "/" + quote(LEVELS[target])
        if target == level:
            return f'<a class="nav-link active" aria-current="page" href="{href}">'
        return f'<a class="nav-link" href="{href}">'

    def title_link(m):
        return re.sub(r'href="[^"]*"', f'href="{to_lang_root or "./"}index.html"', m.group(0))

    html = LANGUAGE_LINK.sub(language_link, html)
    html = LEVEL_LINK.sub(level_link, html)
    html = LEVEL_TEXT_LINK.sub(
        lambda m: f'<a href="{to_lang_root}{m.group(1)}/{quote(LEVELS[m.group(1)])}">', html)
    html = TITLE_LINK.sub(title_link, html)

    start = html.find('<nav id="quarto-sidebar"')
    if start != -1 and "sidebar-expand-all" not in html:
        m = SIDEBAR_END.search(html, start)
        # only if there are collapsible sections at all
        if m and "sidebar-section" in html[start:m.end()]:
            expand, collapse = BUTTON_TEXT[lang]
            button = ('<label class="sidebar-expand-all"><input type="checkbox">'
                      f'<span class="label-expand">▼ {expand}</span>'
                      f'<span class="label-collapse">▲ {collapse}</span></label>\n    ')
            html = html[:m.end(1)] + button + html[m.start(2):]
    return html


def postprocess_all(lang):
    folder = os.path.join(DOCS, lang)
    count = 0
    for root, subdirs, files in os.walk(folder):
        subdirs[:] = [d for d in subdirs if d != "site_libs"]
        for name in files:
            if not name.endswith(".html"):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, folder).replace(os.sep, "/")
            with open(path, encoding="utf-8", newline="") as f:
                old = f.read()
            new = postprocess(old, lang, rel)
            if new != old:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(new)
                count += 1
    print(f"  post-processed: {count} page(s) in docs/{lang}/")


for lang, profile in LANGUAGES.items():
    print(f"\n=== {profile} ===")
    render(f"root,{profile}", f"docs/{lang}")
    for level, start_page in LEVELS.items():
        render(f"{level},{profile}", f"docs/{lang}/{level}")
        # Quarto writes an index.html that redirects to the alphabetically first page.
        # docs/<lang>/<level>/ should lead to the start page of the level instead.
        with open(os.path.join(DOCS, lang, level, "index.html"), "w", encoding="utf-8") as f:
            f.write(LEVEL_INDEX.format(target=start_page.replace(" ", "%20")))
    postprocess_all(lang)

with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8") as f:
    f.write(REDIRECT)
# GitHub Pages serves docs/404.html for every unknown address.
with open(os.path.join(DOCS, "404.html"), "w", encoding="utf-8") as f:
    f.write(NOT_FOUND)
print("\nDone: docs/index.html, docs/404.html, docs/<lang>/ for " + ", ".join(LANGUAGES))

if "--no-serve" in sys.argv:
    sys.exit(0)

PORT = 8000


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DOCS, **kwargs)


socketserver.TCPServer.allow_reuse_address = True
print(f"\nPreview: http://localhost:{PORT}/  (Ctrl+C to stop)")
webbrowser.open(f"http://localhost:{PORT}/")
try:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\nServer stopped.")
