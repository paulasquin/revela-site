"""Builds revela.aidiligence.eu from the texts kept in the Revela repository.

The privacy policy and the terms are written in `revela/docs/play/*.md`; this script turns them
into static pages. Run from the repository root:

    uv run --with markdown python tools/build.py [path/to/revela]
"""

import html
import re
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
REVELA = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT.parent.parent / "revela")
PLAY = REVELA / "docs" / "play"

CONTACT = "contact.aidiligence@gmail.com"
PUBLISHER = "Guardia SAS — SIREN 910 991 140"

STYLE = """
:root { color-scheme: light dark; --fg: #1b1b1f; --muted: #5c5c66; --bg: #fff; --line: #e4e4ea; --accent: #2f6fde; }
@media (prefers-color-scheme: dark) { :root { --fg: #e9e9ee; --muted: #a0a0ab; --bg: #121217; --line: #2a2a33; --accent: #7aa7ff; } }
* { box-sizing: border-box; }
body { font: 16px/1.6 -apple-system, system-ui, "Segoe UI", Roboto, sans-serif; color: var(--fg); background: var(--bg); margin: 0; }
main { max-width: 720px; margin: 0 auto; padding: 32px 20px 64px; }
header { display: flex; align-items: center; gap: 12px; padding-bottom: 16px; border-bottom: 1px solid var(--line); }
header img { width: 40px; height: 40px; border-radius: 10px; }
header a { color: inherit; text-decoration: none; font-weight: 600; font-size: 1.15em; }
nav { margin-left: auto; display: flex; gap: 16px; font-size: .95em; }
nav a { font-weight: 400; font-size: 1em; color: var(--muted); }
h1 { font-size: 1.7em; line-height: 1.25; margin: 1.2em 0 .4em; }
h2 { font-size: 1.2em; margin-top: 2em; }
a { color: var(--accent); }
.lead { font-size: 1.15em; color: var(--muted); }
footer { margin-top: 48px; padding-top: 16px; border-top: 1px solid var(--line); color: var(--muted); font-size: .85em; }
"""


def unfinished(name: str) -> bool:
    """A text still holding placeholders such as [TÉLÉPHONE] is not published."""
    return bool(re.search(r"\[[A-ZÀ-Ý][A-ZÀ-Ý ]+\]", (PLAY / name).read_text()))


TERMS_READY = not unfinished("conditions.md")


def page(title: str, body: str, depth: int) -> str:
    up = "../" * depth
    terms = f'<a href="{up}conditions/">Conditions</a>' if TERMS_READY else ""
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="icon" href="{up}assets/icon.png">
<style>{STYLE}</style>
</head>
<body>
<main>
<header>
  <img src="{up}assets/icon.png" alt="">
  <a href="{up}">Revela</a>
  <nav>{terms}<a href="{up}confidentialite/">Confidentialité</a></nav>
</header>
{body}
<footer>{html.escape(PUBLISHER)} — <a href="mailto:{CONTACT}">{CONTACT}</a></footer>
</main>
</body>
</html>
"""


def from_markdown(name: str) -> tuple[str, str]:
    """Title and HTML body of a text in docs/play, without its editorial notes."""
    text = (PLAY / name).read_text()
    # Notes for us (drafting status, links to internal docs) are blockquotes; never publish them.
    text = "\n".join(line for line in text.splitlines() if not line.startswith(">"))
    title = re.search(r"^# (.+)$", text, re.M).group(1)
    return title, markdown.markdown(text, extensions=["extra", "sane_lists"])


def write(path: str, content: str) -> None:
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content)
    print("wrote", path)


INDEX = f"""
<h1>Revela — Éditeur photo</h1>
<p class="lead">Retouchez vos photos sur Android avec les réglages de Lightroom : mêmes curseurs, rendu
proche, presets <code>.xmp</code>. Tout est traité sur votre téléphone.</p>

<h2>Assistance</h2>
<p>Une question, un problème, une idée ? Écrivez-nous à <a href="mailto:{CONTACT}">{CONTACT}</a>.</p>

<h2>Gratuit ou Revela Pro</h2>
<p>La retouche est gratuite : tous les curseurs, le recadrage et les presets, avec l'export jusqu'à
720 px. Revela Pro ajoute l'export en pleine résolution et aux formats Instagram, et Auto,
l'amélioration IA de la lumière et des couleurs : essai gratuit de 7 jours, puis 1,99 € par mois ou
19,99 € par an. L'abonnement se gère et se résilie dans Google Play, rubrique
<a href="https://play.google.com/store/account/subscriptions">Abonnements</a>, ou depuis les réglages de
l'application.</p>

<h2>Documents</h2>
<ul>
  {{terms}}<li><a href="confidentialite/">Politique de confidentialité / Privacy policy</a></li>
</ul>

<h2>English</h2>
<p>Revela is a photo editor for Android with Lightroom-compatible settings. Editing is free;
Revela Pro adds full-resolution exports and Auto. Support:
<a href="mailto:{CONTACT}">{CONTACT}</a>. Manage or cancel your subscription in Google Play ›
Subscriptions. <a href="confidentialite/">Privacy policy</a>.</p>

<p><small>Lightroom est une marque d'Adobe. Revela n'est ni affiliée à Adobe, ni approuvée par Adobe.</small></p>
"""

REDIRECT = """<!doctype html>
<meta charset="utf-8">
<title>Revela</title>
<meta http-equiv="refresh" content="0; url=../confidentialite/">
<link rel="canonical" href="../confidentialite/">
<a href="../confidentialite/">Privacy policy</a>
"""


def main() -> None:
    terms = "<li><a href=\"conditions/\">Conditions d'utilisation et d'abonnement</a></li>\n  " if TERMS_READY else ""
    write("index.html", page("Revela — Éditeur photo", INDEX.replace("{terms}", terms), 0))
    for path, source in [("conditions/index.html", "conditions.md"), ("confidentialite/index.html", "privacy-policy.md")]:
        if unfinished(source):
            (ROOT / path).unlink(missing_ok=True)
            print("skipped", source, "(placeholders left)")
            continue
        title, body = from_markdown(source)
        write(path, page(title, body, 1))
    write("privacy/index.html", REDIRECT)


if __name__ == "__main__":
    main()
