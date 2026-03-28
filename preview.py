"""
preview.py — render all Quarto profiles and open a local preview.

Usage:  python preview.py
        python preview.py --port 8080
        python preview.py --no-render      (skip rendering, just serve)
"""

import argparse
import http.server
import os
import re
import subprocess
import sys
import threading
import webbrowser

# ── Config ────────────────────────────────────────────────────────────────────

PROFILES   = ["root", "beg", "int", "exp"]  # must match _quarto-<profile>.yml files
DOCS_DIR   = "docs"
START_PAGE = "index.html"                   # opened in browser after serving

# ── Argument parsing ──────────────────────────────────────────────────────────

parser = argparse.ArgumentParser()
parser.add_argument("--port",      type=int, default=8000)
parser.add_argument("--no-render", action="store_true")
args = parser.parse_args()

# ── Render ────────────────────────────────────────────────────────────────────

if not args.no_render:
    print("Rendering Quarto profiles...\n")
    for profile in PROFILES:
        print(f"  → quarto render --profile {profile}")
        result = subprocess.run(
            ["quarto", "render", "--profile", profile],
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        if result.returncode != 0:
            print(f"    ⚠  Profile '{profile}' failed — skipping.\n")
        else:
            print(f"    ✓  Done.\n")

# ── Fix cross-profile navbar links ────────────────────────────────────────────

def fix_cross_profile_links(docs_dir, profiles):
    """
    Quarto converts all navbar hrefs to relative paths (e.g. ./int/...).
    This breaks cross-profile links on subpages. We rewrite them so they
    navigate correctly relative to each file's depth in the output tree.
    """
    # Match any relative prefix (./  ../  ../../  etc.) followed by a profile name.
    # Quarto generates different depths depending on where the source .qmd lives.
    profile_pattern = re.compile(
        r'href="(?:\.\.?/)*(' + '|'.join(profiles) + r')/(.*?)"'
    )
    docs_path = os.path.abspath(docs_dir)
    fixed = 0

    for profile in profiles:
        profile_dir = os.path.join(docs_path, profile)
        if not os.path.isdir(profile_dir):
            continue
        for dirpath, _, filenames in os.walk(profile_dir):
            for filename in filenames:
                if not filename.endswith('.html'):
                    continue
                html_file = os.path.join(dirpath, filename)
                rel = os.path.relpath(html_file, docs_path)
                # depth = number of directories between docs/ and the file
                depth = len(rel.replace('\\', '/').split('/')) - 1
                prefix = '../' * depth

                def make_replacement(prefix):
                    def replacement(m):
                        return f'href="{prefix}{m.group(1)}/{m.group(2)}"'
                    return replacement

                with open(html_file, encoding='utf-8') as f:
                    content = f.read()
                new_content = profile_pattern.sub(make_replacement(prefix), content)
                if new_content != content:
                    with open(html_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    fixed += 1

    print(f"  ✓  Fixed cross-profile links in {fixed} HTML file(s).\n")

if not args.no_render:
    fix_cross_profile_links(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), DOCS_DIR),
        PROFILES,
    )

# ── Serve ─────────────────────────────────────────────────────────────────────

docs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DOCS_DIR)

if not os.path.isdir(docs_path):
    print(f"Error: '{DOCS_DIR}/' not found. Run without --no-render first.")
    sys.exit(1)

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """SimpleHTTPRequestHandler with request logging suppressed."""
    def log_message(self, *_):
        pass
    def log_request(self, *_):
        pass

os.chdir(docs_path)
httpd = http.server.HTTPServer(("", args.port), QuietHandler)

url = f"http://localhost:{args.port}/{START_PAGE}"
print(f"Serving at  {url}")
print("Press Ctrl+C to stop.\n")

threading.Timer(0.5, lambda: webbrowser.open(url)).start()

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\nServer stopped.")
