#!/usr/bin/env python3
"""Build the bare home for every short-link domain.

Design: Claude Design canvas "Dok sites", board "Korte links".
Logged-out visitors see one line on what the links are; a signed-in admin of
a shortener domain gets the link console ({{content}}) on the same page.

Writes index.html (geert.link, the default tree) and hosts/<host>/index.html,
which the publish workflow copies over the tree per host.
Edit here, run `python3 scripts/build-bare.py`, commit the output.
"""

import json
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

# Search and share text per host: what the page says, a little longer.
# Canonical and share tags point at production, also on staging and accept.
# The bare home is Dutch only, so the canonical is the bare host, no hreflang.
SEO = {
    # host: (title, description, who the links are of, for JSON-LD)
    "geert.link": (
        "geert.link: korte links van Geert Rozendom",
        "geert.link is het domein voor de korte links van Geert Rozendom. Kreeg je zo'n link en werkt hij niet? Mail dan naar support@geert.link.",
        {"publisher": {"@type": "Person", "name": "Geert Rozendom"}},
    ),
    "nm.nu": (
        "nm.nu: korte links van Geert Rozendom",
        "nm.nu is een kort domein voor de links van Geert Rozendom: een paar letters in plaats van een lang adres. Werkt een link niet? Mail support@nm.nu.",
        {"publisher": {"@type": "Person", "name": "Geert Rozendom"}},
    ),
    "koek.in": (
        "koek.in: korte links van Geert Rozendom",
        "koek.in is een kort domein voor de links van Geert Rozendom: een paar letters in plaats van een lang adres. Werkt een link niet? Mail support@koek.in.",
        {"publisher": {"@type": "Person", "name": "Geert Rozendom"}},
    ),
    "dox.onl": (
        "dox.onl: korte links naar documenten op thisdoc.online",
        "dox.onl is het korte domein voor documenten op thisdoc.online. Een dox.onl-link brengt je naar een document, dat je daar leest en ondertekent.",
        {"isPartOf": {"@type": "WebSite", "name": "thisdoc.online", "url": "https://thisdoc.online/"}},
    ),
    "knst.link": (
        "knst.link: korte links van Kunstmarkt",
        "knst.link is het korte domein van Kunstmarkt: korte links naar een aanmelding, een kraam of een kunstenaar. Werkt een link niet? Mail support@knst.link.",
        {"isPartOf": {"@type": "WebSite", "name": "Kunstmarkt", "url": "https://kunstmarkt.app/"}},
    ),
}


def head_meta(host: str) -> str:
    name, tld, _dot, line, _parent, _console = DOMAINS[host]
    title, description, owner = SEO[host]
    url = f"https://{host}/"
    image = f"https://{host}/images/og.png"  # 1200x630, built by scripts/build-og.py
    alt = f"{name}{tld}/… {line}"
    tags = [
        f'<title>{e(title)}</title>',
        f'<meta name="description" content="{e(description)}">',
        f'<link rel="canonical" href="{url}">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{e(host)}">',
        f'<meta property="og:title" content="{e(title)}">',
        f'<meta property="og:description" content="{e(description)}">',
        f'<meta property="og:url" content="{url}">',
        '<meta property="og:locale" content="nl_NL">',
        f'<meta property="og:image" content="{image}">',
        '<meta property="og:image:type" content="image/png">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{e(alt)}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{e(title)}">',
        f'<meta name="twitter:description" content="{e(description)}">',
        f'<meta name="twitter:image" content="{image}">',
        f'<meta name="twitter:image:alt" content="{e(alt)}">',
    ]
    website = {"@context": "https://schema.org", "@type": "WebSite", "@id": f"{url}#website",
               "name": host, "url": url, "description": line, "inLanguage": "nl", **owner}
    ld = json.dumps(website, ensure_ascii=False, indent=2).replace("</", "<\\/")
    ld = "\n".join("  " + row for row in ld.splitlines())
    return "\n".join("  " + t for t in tags) + f'\n  <script type="application/ld+json">\n{ld}\n  </script>'


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
{head_meta(host)}{console_css}
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
