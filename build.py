"""Baut das Tutorial in allen Kombinationen aus Sprache und Niveau und zeigt es lokal an.

    python build.py            # rendern + Vorschau-Server
    python build.py --no-serve # nur rendern

Ergebnis:
    docs/index.html            -> leitet nach Browsersprache auf de/, en/, sv/, no/ oder da/ weiter
    docs/<sprache>/index.html  -> Startseite (Profil root): Wahl des Niveaus
    docs/<sprache>/<niveau>/   -> beg, int, exp

Je Lauf sind zwei Profile aktiv, eins aus jeder Gruppe (siehe _quarto.yml), z. B.
    quarto render --profile int,english --output-dir docs/en/int
Die Startseite wird je Sprache ZUERST gebaut: Quarto leert beim Rendern den
Ausgabeordner, und docs/de/ enthält die Niveau-Ordner.
Navigation zwischen Sprachen und Niveaus: navigation.html (kein Nachbearbeiten nötig).
"""
import http.server
import os
import socketserver
import subprocess
import sys
import webbrowser

BASIS = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(BASIS, "docs")
SPRACHEN = {"de": "deutsch", "en": "english", "sv": "svenska", "no": "norsk", "da": "dansk"}
# Niveau -> Startseite (gleiche Liste wie START in navigation.html)
NIVEAUS = {
    "beg": "Qmd Files/Example Page/index_beg.html",
    "int": "Qmd Files/Getting Started/getting_started.html",
    "exp": "Qmd Files/Tipps and Tricks/index_exp.html",
}

WEITERLEITUNG = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>Weiterleitung / Redirect</title>
<script>
  // Browsersprache -> Ordner; Norwegisch kommt als nb, nn oder no. Sonst Englisch.
  var ORDNER = { de: "de", en: "en", sv: "sv", nb: "no", nn: "no", no: "no", da: "da" };
  var sprache = (navigator.language || "de").slice(0, 2).toLowerCase();
  window.location.replace((ORDNER[sprache] || "en") + "/");
</script>
<noscript><meta http-equiv="refresh" content="0; url=de/"></noscript>
</head>
<body>
<p><a href="de/">Deutsch</a> · <a href="en/">English</a> · <a href="sv/">Svenska</a> · <a href="no/">Norsk</a> · <a href="da/">Dansk</a></p>
</body>
</html>
"""

# Eigenständige Seite ohne Quarto: Die Adresse, unter der sie erscheint, ist
# beliebig, deshalb sucht das Skript die Wurzel des Tutorials selbst.
NICHT_GEFUNDEN = """<!DOCTYPE html>
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

NIVEAU_INDEX = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="0; url={ziel}">
<title>Weiterleitung / Redirect</title></head>
<body><p><a href="{ziel}">{ziel}</a></p></body></html>
"""


def render(profile, ausgabe):
    befehl = ["quarto", "render", "--profile", profile, "--output-dir", ausgabe]
    print(f"\n  > {' '.join(befehl)}")
    lauf = subprocess.run(befehl, cwd=BASIS, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    for zeile in (lauf.stdout + lauf.stderr).splitlines():
        if zeile.strip():
            print(f"    {zeile}")
    if lauf.returncode != 0:
        print(f"  FEHLER bei --profile {profile}. Abbruch.")
        sys.exit(1)


for kurz, sprache in SPRACHEN.items():
    print(f"\n=== {sprache} ===")
    render(f"root,{sprache}", f"docs/{kurz}")
    for niveau, start in NIVEAUS.items():
        render(f"{niveau},{sprache}", f"docs/{kurz}/{niveau}")
        # Quarto legt als index.html eine Weiterleitung auf die alphabetisch erste Seite an.
        # docs/<sprache>/<niveau>/ soll aber auf die Startseite des Niveaus führen.
        with open(os.path.join(DOCS, kurz, niveau, "index.html"), "w", encoding="utf-8") as f:
            f.write(NIVEAU_INDEX.format(ziel=start.replace(" ", "%20")))

with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8") as f:
    f.write(WEITERLEITUNG)
# GitHub Pages liefert docs/404.html bei jeder unbekannten Adresse aus.
with open(os.path.join(DOCS, "404.html"), "w", encoding="utf-8") as f:
    f.write(NICHT_GEFUNDEN)
print("\nFertig: docs/index.html, docs/404.html, docs/<sprache>/ für " + ", ".join(SPRACHEN))

if "--no-serve" in sys.argv:
    sys.exit(0)

PORT = 8000


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DOCS, **kwargs)


socketserver.TCPServer.allow_reuse_address = True
print(f"\nVorschau: http://localhost:{PORT}/  (Strg+C beendet)")
webbrowser.open(f"http://localhost:{PORT}/")
try:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\nServer beendet.")
