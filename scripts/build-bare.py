#!/usr/bin/env python3
"""Build the bare home for every short-link domain.

Design: Claude Design canvas "Dok sites", board "Korte links".
Logged-out visitors see one line on what the links are; a signed-in admin of
a shortener domain gets the link console ({{content}}) on the same page.

Writes index.html (geert.link, the default tree) and hosts/<host>/index.html,
which the publish workflow copies over the tree per host.
Edit here, run `python3 scripts/build-bare.py`, commit the output.
"""

from html import escape as e
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DOMAINS = {
    # host: (name, tld, dot colour, line, parent, console)
    "geert.link": ("geert", ".link", "#111111", "Korte links van Geert Rozendom.", None, True),
    "nm.nu": ("nm", ".nu", "#111111", "Korte links van Geert Rozendom.", None, True),
    "koek.in": ("koek", ".in", "#B8732E", "Korte links van Geert Rozendom.", None, False),
    "dox.onl": ("dox", ".onl", "#2F5BD3", "Korte links naar documenten op thisdoc.online. Daar lees en onderteken je ze.", "thisdoc.online", False),
    "knst.link": ("knst", ".link", "#C2462B", "Korte links van Kunstmarkt: naar een aanmelding, een kraam of een kunstenaar.", "kunstmarkt.app", False),
}

# Only for a signed-in admin of a shortener domain: the dark link console.
CONSOLE = '''  <header class="landing-nav admin-only">
    <a href="/" class="landing-brand">
      <img class="brand-logo" src="{{brand_logo}}" width="28" height="28" alt="" decoding="async"
           onerror="this.onerror=null;this.src='/images/logo.png'">
      {{brand_name}}
    </a>
    <nav>
      <a href="/admin/links">Links</a>
      <a href="/admin/settings">Instellingen</a>
    </nav>
  </header>
  <!-- Link console (create form + recent links), injected by Rails (HomeController#index). -->
  <section class="console admin-only">
    {{content}}
  </section>
'''


def page(host: str) -> str:
    name, tld, dot, line, parent, console = DOMAINS[host]
    parent_html = f'\n    <p><a href="https://{parent}">{parent} ⟶</a></p>' if parent else ""
    console_css = '\n  <link rel="stylesheet" href="/css/landing.css">\n  <link rel="stylesheet" href="/css/links.css">' if console else ""
    return f'''<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  {{{{csrf_meta}}}}
  <title>{e(host)}</title>
  <meta name="description" content="{e(line)}">
  <meta name="robots" content="noindex">{console_css}
  <link rel="stylesheet" href="/css/bare.css">
  <link rel="icon" href="{{{{brand_logo}}}}">
</head>
<body data-role="{{{{user_role}}}}" style="--bare-dot:{dot}">
{CONSOLE if console else ""}  <main class="bare guest-only">
    <h1>{e(name)}<span class="tld">{e(tld)}</span><span class="rest">/…</span></h1>
    <p>{e(line)}</p>{parent_html}
    <p class="bare-note">Werkt een link niet? <a href="mailto:support@{host}">Mail me</a>.</p>
    <p class="bare-note bare-admin"><a href="/session/new">Inloggen</a></p>
  </main>
  {{{{footer}}}}
</body>
</html>
'''


def main() -> None:
    (ROOT / "index.html").write_text(page("geert.link"), encoding="utf-8")
    for host in DOMAINS:
        target = ROOT / "hosts" / host / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page(host), encoding="utf-8")


if __name__ == "__main__":
    main()
