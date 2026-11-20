"""Générateur du site lpticb.com (LPTIC-B, LPK, CAFOT).

Aucune dépendance : Python 3.10+ suffit.

    python tools/build.py            # construit le site dans _site/ (mise en ligne)
    python tools/build.py --local    # liens en .../index.html pour ouvrir les pages sans serveur

Tout le contenu se modifie dans content/ ; ne jamais retoucher le HTML produit.
"""

from __future__ import annotations

import html
import json
import re
import shutil
import urllib.parse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
ASSETS = ROOT / "assets"
OUT = ROOT / "_site"
LOCAL = "--local" in sys.argv

SITE = json.loads((CONTENT / "site.json").read_text(encoding="utf-8"))
ETABS = json.loads((CONTENT / "etablissements.json").read_text(encoding="utf-8"))
ETAB = {e["slug"]: e for e in ETABS}
FORM = json.loads((CONTENT / "formations.json").read_text(encoding="utf-8"))
GROUPS = {g["id"]: g for g in FORM["groups"]}
ITEMS = [it for it in FORM["items"] if not it.get("masque")]  # "masque": true retire une filière non ouverte
GALERIE = json.loads((CONTENT / "galerie.json").read_text(encoding="utf-8"))
PARTNERS = json.loads((CONTENT / "partenaires.json").read_text(encoding="utf-8"))
PHOTOS = json.loads((ASSETS / "photos" / "manifest.json").read_text(encoding="utf-8"))
AGENDA = json.loads((CONTENT / "agenda.json").read_text(encoding="utf-8"))
TODAY = date.today().isoformat()

# Onglets du coin Actualités : catégorie -> (libellé, page)
FORM_LEAD = "Filières professionnelles par apprentissage au CAFOT, technologiques et professionnelles au LPTIC-B et générales au LPK."

CATS = {
    "etablissement": ("Vie de l'établissement", "actualites/etablissement/"),
    "examens": ("Examens et calendrier", "actualites/examens/"),
    "officiel": ("Infos officielles", "actualites/officiel/"),
}

NAV = [
    ("Établissements", "etablissements/"),
    ("Formations", "formations/"),
    ("Admission", "admission/"),
    ("Actualités", "actualites/"),
    ("Contact", "contact/"),
]
MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
          "septembre", "octobre", "novembre", "décembre"]

e = html.escape
SITEMAP: list[str] = []


# ---------------------------------------------------------------- utilitaires

def link(page: str, target: str) -> str:
    """Lien relatif de la page `page` vers `target` (chemins sans / initial)."""
    depth = page.count("/") if page.endswith("/") else page.count("/")
    prefix = "../" * depth
    if LOCAL and (target == "" or target.endswith("/")):
        target += "index.html"
    return (prefix + target) or "./"


def tel(number: str) -> str:
    return "tel:" + re.sub(r"[^\d+]", "", number)


def wa_url(message: str | None = None) -> str:
    num = re.sub(r"\D", "", SITE["whatsapp"])
    msg = message or SITE["whatsapp_message"]
    return f"https://wa.me/{num}?text={urllib.parse.quote(msg)}"


def mo(path: Path) -> str:
    """Taille d'un fichier en mégaoctets, à la française : les parents savent ce que la vidéo va consommer."""
    return f"{path.stat().st_size / 1_000_000:.1f} Mo".replace(".", ",")


def fr_date(d: str) -> str:
    y, m, day = d.split("-")
    return f"{int(day)} {MONTHS[int(m) - 1]} {y}"


def photo(page: str, slug: str | None, alt: str, sizes: str, cls: str = "", eager: bool = False) -> str:
    if not slug or slug not in PHOTOS:
        return ""
    p = PHOTOS[slug]
    ws = p["widths"]
    srcset = ", ".join(f"{link(page, f'assets/photos/{slug}-{w}.webp')} {w}w" for w in ws)
    w0 = ws[-1]
    h0 = round(w0 / p["ratio"])
    mid = ws[1] if len(ws) > 1 else ws[0]
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="{link(page, f"assets/photos/{slug}-{mid}.webp")}" srcset="{srcset}" '
            f'sizes="{sizes}" width="{w0}" height="{h0}" alt="{e(alt)}" {load}>')


def logo(page: str, slug: str, cls: str = "logo", height: int = 64) -> str:
    et = ETAB[slug]
    return (f'<img class="{cls}" src="{link(page, f"assets/logos/{et["logo"]}.webp")}" '
            f'height="{height}" alt="Logo {e(et["short"])}">')


def street_full() -> str:
    a = SITE["address"]
    return a["street"] + (", " + a["landmark"] if a.get("landmark") else "")


def wa_numbers() -> str:
    """Les numéros WhatsApp du secrétariat, chacun cliquable."""
    out = []
    for n in [SITE["whatsapp"]] + SITE.get("whatsapp_autres", []):
        num = re.sub(r"\D", "", n)
        out.append(f'<a href="https://wa.me/{num}?text={urllib.parse.quote(SITE["whatsapp_message"])}">{e(n.replace("+226 ", ""))}</a>')
    return " ou ".join(out)


def phones(nums: list[str]) -> str:
    return "<br>".join(f'<a href="{tel(n)}">{e(n)}</a>' for n in nums)


def org_schema(et: dict) -> dict:
    a = SITE["address"]
    return {
        "@type": et["schema_type"],
        "name": et["name"],
        "alternateName": et["short"],
        "url": f'{SITE["url"]}/etablissements/{et["slug"]}/',
        "logo": f'{SITE["url"]}/assets/logos/{et["logo"]}.webp',
        "telephone": et["phones"][0],
        "email": SITE["email"],
        "slogan": SITE["motto"],
        "address": {"@type": "PostalAddress", "streetAddress": street_full(), "addressLocality": a["locality"],
                    "addressRegion": a["region"], "addressCountry": a["country"], "postOfficeBoxNumber": a["po_box"]},
    }


def breadcrumb(trail: list[tuple[str, str]]) -> dict:
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": f'{SITE["url"]}/{p}'}
        for i, (n, p) in enumerate(trail)]}


def crumbs(page: str, trail: list[tuple[str, str]]) -> str:
    parts = [f'<a href="{link(page, p)}">{e(n)}</a>' for n, p in trail[:-1]]
    parts.append(f'<span aria-current="page">{e(trail[-1][0])}</span>')
    return '<nav class="crumbs" aria-label="Fil d\'Ariane">' + '<span class="sep">/</span>'.join(parts) + "</nav>"


# Carré magique de Jupiter : discrète signature graphique du réalisateur.
JUPITER = [4, 14, 15, 1, 9, 7, 6, 12, 5, 11, 10, 8, 16, 2, 3, 13]


def jupiter_mark() -> str:
    dots = []
    for i, v in enumerate(JUPITER):
        x, y = 2 + (i % 4) * 4, 2 + (i // 4) * 4
        r = 0.45 + 1.35 * (v / 16) ** 0.5
        fill = "#fff" if v == 1 else "currentColor"
        dots.append(f'<circle cx="{x}" cy="{y}" r="{r:.2f}" fill="{fill}"/>')
    return f'<svg class="jm" viewBox="0 0 16 16" width="12" height="12" aria-hidden="true">{"".join(dots)}</svg>'


CHEVRONS = (
    '<svg class="chevrons" viewBox="0 0 120 108" aria-hidden="true">'
    '<path d="M0 44 60 0l60 44-16 8-44-32-44 32z" fill="#d8263b"/>'
    '<path d="M0 72 60 28l60 44-16 8-44-32-44 32z" fill="#f5b91a"/>'
    '<path d="M0 100 60 56l60 44-16 8-44-32-44 32z" fill="#4f8a3a"/>'
    "</svg>"
)


# ---------------------------------------------------------------- gabarit

def page_html(page: str, title: str, desc: str, body: str, schema: list[dict] | None = None,
              og_image: str = "assets/og.jpg", active: str = "") -> str:
    canonical = f'{SITE["url"]}/{page}'
    full_title = title if title.startswith("LPTIC-B") else f"{title} | LPTIC-B Bobo-Dioulasso"
    ld = ""
    if schema:
        ld = ('<script type="application/ld+json">'
              + json.dumps({"@context": "https://schema.org", "@graph": schema}, ensure_ascii=False)
              + "</script>")
    nav = "".join(
        f'<li><a href="{link(page, p)}"{" aria-current=\"page\"" if active == p else ""}>{e(n)}</a></li>'
        for n, p in NAV)
    a = SITE["address"]
    foot_etabs = "".join(
        f'<div class="f-etab key-{et["key"]}"><p class="f-name">{e(et["short"])}</p>'
        f'<p>{e(et["role"])}</p><p>{phones(et["phones"])}</p></div>' for et in ETABS)
    SITEMAP.append(page)
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="{e(SITE['site_name'])}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE['url']}/{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1f4fa3">
<link rel="icon" href="{link(page, 'assets/favicon.ico')}" sizes="48x48">
<link rel="icon" href="{link(page, 'assets/favicon.svg')}" type="image/svg+xml">
<link rel="manifest" href="{link(page, 'assets/site.webmanifest')}">
<link rel="apple-touch-icon" href="{link(page, 'assets/apple-touch-icon.png')}">
{'' if LOCAL else f'<link rel="preload" href="{link(page, "assets/fonts/barlow-condensed-latin-700-normal.woff2")}" as="font" type="font/woff2" crossorigin>'}
<link rel="stylesheet" href="{link(page, 'assets/style.css')}">
<meta name="generator" content="Jovian Labs">
<script>document.documentElement.classList.add("js")</script>
{ld}
</head>
<body>
<a class="skip" href="#contenu">Aller au contenu</a>
<header class="top">
  <div class="wrap top-in">
    <a class="brand" href="{link(page, '')}">
      {logo(page, 'lptic-b', 'brand-logo', 44)}
      <span class="brand-text"><span class="brand-name">LPTIC-B</span><span class="brand-sub">avec le LPK et le CAFOT, Bobo-Dioulasso</span></span>
    </a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu">Menu</button>
    <nav id="menu" class="menu" aria-label="Navigation principale"><ul>{nav}</ul></nav>
  </div>
</header>
<main id="contenu">
{body}
</main>
<footer class="foot">
  <div class="wrap">
    <div class="f-grid">
      <div class="f-intro">
        <p class="f-motto">{e(SITE['motto'])}</p>
        <p>{e(a['street'])}<br>{e(a.get('landmark', ''))}<br>{e(a['locality'])}, Burkina Faso<br>{e(a['po_box'])}</p>
        <p><a href="mailto:{e(SITE['email'])}">{e(SITE['email'])}</a></p>
      </div>
      {foot_etabs}
    </div>
    <div class="f-bottom">
      <p><a href="{link(page, 'partenaires/')}">Partenaires et remerciements</a><a href="{link(page, 'mentions-legales/')}">Mentions légales</a></p>
      <p class="credit">Réalisation : <a href="{SITE['credit']['url']}">{jupiter_mark()} {e(SITE['credit']['name'])}</a></p>
    </div>
  </div>
</footer>
<script src="{link(page, 'assets/site.js')}" defer></script>
</body>
</html>
"""


def write(page: str, content: str) -> None:
    path = OUT / (page + "index.html" if page.endswith("/") or page == "" else page)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def cta_band(page: str, title: str = "Une question sur les inscriptions ?") -> str:
    return f"""<section class="band">
  <div class="wrap band-in">
    <div>
      <h2>{e(title)}</h2>
      <p>Le secrétariat répond sur WhatsApp et au téléphone : places disponibles, pièces à fournir, frais de scolarité.</p>
    </div>
    <p class="actions"><a class="btn btn-sun" href="{wa_url()}">Écrire sur WhatsApp</a><a class="btn btn-line" href="{tel(SITE['whatsapp'])}">Appeler le {e(SITE['whatsapp'].replace('+226 ', ''))}</a></p>
  </div>
</section>"""


def formation_link(page: str, it: dict) -> str:
    abbr = f'<span class="abbr">{e(it["abbr"])}</span>' if it.get("abbr") and len(it["abbr"]) > 2 else ""
    return f'<li><a href="{link(page, "formations/" + it["slug"] + "/")}">{e(it["title"])}</a>{abbr}</li>'


def formations_board(page: str, group_ids: list[str] | None = None) -> str:
    out = []
    for g in FORM["groups"]:
        if group_ids and g["id"] not in group_ids:
            continue
        et = ETAB[g["etablissement"]]
        items = "".join(formation_link(page, it) for it in ITEMS if it["group"] == g["id"])
        if not items:
            items = f'<li class="board-empty"><span>{e(g.get("empty", ""))}</span> <a href="{link(page, "etablissements/" + et["slug"] + "/")}">Contacter le {e(et["short"])}</a></li>'
        out.append(f"""<div class="board-col key-{et['key']}">
  <h3>{e(g['title'])} <span class="board-etab">{e(et['short'])}</span></h3>
  <p class="board-meta">{e(g['diplomas'])}</p>
  <ul class="board-list">{items}</ul>
</div>""")
    return '<div class="board">' + "".join(out) + "</div>"


# ---------------------------------------------------------------- actualités

def parse_article(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    _, fm, body = raw.split("---", 2)
    meta = {}
    for line in fm.strip().splitlines():
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    meta["photos"] = [s.strip() for s in meta.get("photos", "").split(",") if s.strip()]
    meta["affiches"] = [s.strip() for s in meta.get("affiches", "").split(",") if s.strip()]
    meta.setdefault("categorie", "etablissement")
    assert meta["categorie"] in CATS, f"catégorie inconnue dans {path.name}"
    meta["slug"] = path.stem[11:]
    meta["body"] = body.strip()
    return meta


def md(text: str) -> str:
    def inline(s: str) -> str:
        s = e(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        return re.sub(r"\[(.+?)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', s)
    blocks = []
    for b in re.split(r"\n\s*\n", text):
        lines = b.strip().splitlines()
        if not lines:
            continue
        if len(lines) == 1 and lines[0].startswith("## "):
            blocks.append(f"<h2>{inline(lines[0][3:])}</h2>")
        elif all(l.startswith("- ") for l in lines):
            blocks.append("<ul>" + "".join(f"<li>{inline(l[2:])}</li>" for l in lines) + "</ul>")
        else:
            blocks.append(f"<p>{inline(' '.join(lines))}</p>")
    return "\n".join(blocks)


ARTICLES = sorted((parse_article(p) for p in (CONTENT / "actualites").glob("*.md")),
                  key=lambda a: (a["date"], a.get("a_la_une") == "oui"), reverse=True)


def news_list(page: str, articles: list[dict]) -> str:
    rows = []
    for a in articles:
        if a["photos"]:
            img = photo(page, a["photos"][0], "", "(min-width: 760px) 240px, 100vw", "news-img")
        else:
            img = photo(page, a["affiches"][0] if a["affiches"] else None, "", "(min-width: 760px) 240px, 100vw", "news-img is-poster")
        rows.append(f"""<li class="news-item">
  <a class="news-link{'' if img else ' no-img'}" href="{link(page, 'actualites/' + a['slug'] + '/')}">
    {img}
    <span class="news-text"><span class="news-meta"><span class="tag tag-{a['categorie']}">{e(CATS[a['categorie']][0])}</span><time datetime="{a['date']}">{fr_date(a['date'])}</time></span>
    <span class="news-title">{e(a['title'])}</span>
    <span class="news-sum">{e(a['summary'])}</span></span>
  </a>
</li>""")
    return '<ul class="news">' + "".join(rows) + "</ul>"


CAPTION = {g["photo"]: g["caption"] for g in GALERIE}


def upcoming() -> list[dict]:
    """Dates à venir : celles déjà passées disparaissent toutes seules (le site est reconstruit chaque jour)."""
    return sorted((a for a in AGENDA if (a.get("fin") or a["debut"]) >= TODAY), key=lambda a: a["debut"])


def date_range(a: dict) -> str:
    if a.get("fin") and a["fin"] != a["debut"]:
        return f"Du {fr_date(a['debut'])} au {fr_date(a['fin'])}"
    return fr_date(a["debut"])


def agenda_list(page: str, items: list[dict], limit: int | None = None) -> str:
    if not items:
        return '<p class="empty">Aucune date annoncée pour le moment.</p>'
    rows = []
    for a in items[:limit]:
        label = e(a["titre"])
        if a.get("article"):
            label = f'<a href="{link(page, "actualites/" + a["article"] + "/")}">{label}</a>'
        rows.append(f'<li><time datetime="{a["debut"]}">{date_range(a)}</time><span>{label}</span></li>')
    return '<ol class="agenda">' + "".join(rows) + "</ol>"


def featured(page: str) -> str:
    """Bloc « à la une » de l'accueil : l'actualité marquée a_la_une (sinon la plus récente) avec ses photos."""
    if not ARTICLES:
        return ""
    a = next((x for x in ARTICLES if x.get("a_la_une") == "oui"), ARTICLES[0])
    url = link(page, "actualites/" + a["slug"] + "/")
    ph = a["photos"][:4]
    media = ""
    if a["affiches"]:
        posters = "".join(photo(page, s, f"Affiche : {a['title']}", "(min-width: 900px) 20vw, 50vw", "feat-poster") for s in a["affiches"][:2])
        media = f'<a class="feat-media feat-posters" href="{url}" tabindex="-1">{posters}</a>'
    elif ph:
        thumbs = "".join(photo(page, s, CAPTION.get(s, ""), "(min-width: 900px) 12vw, 30vw", "feat-thumb") for s in ph[1:])
        media = (f'<a class="feat-media" href="{url}" tabindex="-1">{photo(page, ph[0], CAPTION.get(ph[0], ""), "(min-width: 900px) 40vw, 100vw", "feat-main")}'
                 + (f'<span class="feat-thumbs">{thumbs}</span>' if thumbs else "") + "</a>")
    cat_name, cat_page = CATS[a["categorie"]]
    return f"""<article class="feat">{media}
  <p class="news-meta"><a class="tag tag-{a['categorie']}" href="{link(page, cat_page)}">{e(cat_name)}</a><time datetime="{a['date']}">{fr_date(a['date'])}</time></p>
  <h3><a href="{url}">{e(a['title'])}</a></h3>
  <p>{e(a['summary'])}</p>
</article>"""


# ---------------------------------------------------------------- pages

def build_home() -> None:
    page = ""
    etab_cols = "".join(f"""<article class="etab key-{et['key']}">
  {logo(page, et['slug'], 'etab-logo', 72)}
  <h3><a href="{link(page, 'etablissements/' + et['slug'] + '/')}">{e(et['short'])}</a></h3>
  <p class="etab-role">{e(et['role'])}</p>
  <p>{e(et['summary'])}</p>
</article>""" for et in ETABS)
    shots = [("tableau-electrique", "Câblage d'un tableau électrique"),
             ("chantier-ecole", "Chantier école en génie civil"),
             ("oscilloscopes", "Mesures à l'oscilloscope en électronique")]
    strip = "".join(f'<figure>{photo(page, s, c, "(min-width: 760px) 33vw, 100vw")}<figcaption>{e(c)}</figcaption></figure>'
                    for s, c in shots)
    partners = ""
    if PARTNERS["partners"]:
        logos = "".join(f'<img src="{link(page, "assets/partenaires/" + p["logo"])}" alt="{e(p["name"])}" height="48" loading="lazy">'
                        for p in PARTNERS["partners"])
        partners = f'<section class="sec"><div class="wrap"><h2>Ils nous accompagnent</h2><div class="partner-row">{logos}</div></div></section>'
    body = f"""<section class="hero">
  <div class="hero-photo">{photo(page, 'atelier-percage', "Élèves en blouse bleue à l'atelier de perçage", '(min-width: 900px) 55vw, 100vw', 'hero-img', eager=True)}</div>
  <div class="hero-panel">
    {CHEVRONS}
    <h1>Apprendre un métier ou préparer son BAC en enseignement technique ou général à <span class="nw">Bobo-Dioulasso</span></h1>
    <p class="lead">Trois établissements d'un même promoteur : le Lycée Privé Technique Industriel et Commercial de Bobo-Dioulasso (LPTIC-B), le Lycée Privé Kenntnis (LPK) et le Centre d'Apprentissage et de Formation Technique (CAFOT).</p>
    <p class="actions"><a class="btn btn-sun" href="{wa_url()}">Écrire sur WhatsApp</a><a class="btn btn-ghost" href="{link(page, 'formations/')}">Voir les formations</a></p>
  </div>
</section>
<section class="sec">
  <div class="wrap">
    <h2>Trois établissements, une même devise</h2>
    <p class="sec-lead">Excellence, discipline, succès : la devise commune du LPTIC-B, du LPK et du CAFOT.</p>
    <div class="etabs">{etab_cols}</div>
  </div>
</section>
<section class="sec sec-tint">
  <div class="wrap">
    <h2>Formations</h2>
    <p class="sec-lead">{e(FORM_LEAD)}</p>
    {formations_board(page)}
  </div>
</section>
<section class="sec">
  <div class="wrap">
    <h2>On apprend en atelier et sur le chantier</h2>
    <div class="strip">{strip}</div>
    <p class="more"><a href="{link(page, 'vie-scolaire/')}">Toutes les photos de la vie scolaire</a></p>
  </div>
</section>
<section class="sec sec-line">
  <div class="wrap">
    <h2>Actualités</h2>
    <div class="news-layout">
      {featured(page)}
      <aside class="dates"><h3>Prochaines dates</h3>{agenda_list(page, upcoming(), 4)}
        <p class="more"><a href="{link(page, 'actualites/examens/')}">Examens et calendrier</a></p></aside>
    </div>
    <p class="more"><a href="{link(page, 'actualites/')}">Toutes les actualités</a></p>
  </div>
</section>
{partners}
{cta_band(page)}"""
    schema = [{"@type": "WebSite", "name": SITE["site_name"], "url": SITE["url"] + "/", "inLanguage": "fr"}] + \
             [org_schema(et) for et in ETABS]
    write(page, page_html(page, "LPTIC-B, LPK et CAFOT : lycées et formation technique à Bobo-Dioulasso",
                          SITE["description"], body, schema))


def build_etablissements() -> None:
    page = "etablissements/"
    cols = "".join(f"""<article class="etab key-{et['key']}">
  {logo(page, et['slug'], 'etab-logo', 72)}
  <h2><a href="{link(page, 'etablissements/' + et['slug'] + '/')}">{e(et['name'])} ({e(et['short'])})</a></h2>
  <p class="etab-role">{e(et['role'])}</p>
  <p>{e(et['summary'])}</p>
</article>""" for et in ETABS)
    trail = [("Accueil", ""), ("Établissements", page)]
    body = f"""<div class="wrap page-head">{crumbs(page, trail)}<h1>Nos établissements</h1>
<p class="lead">Trois établissements d'un même promoteur à Bobo-Dioulasso, réunis par une même devise : excellence, discipline, succès.</p></div>
<section class="sec sec-tight"><div class="wrap"><div class="etabs">{cols}</div></div></section>
{cta_band(page)}"""
    write(page, page_html(page, "Nos établissements", "LPTIC-B, Lycée Privé Kenntnis (LPK) et CAFOT : trois établissements d'un même promoteur à Bobo-Dioulasso.",
                          body, [breadcrumb(trail)], active=page))
    for et in ETABS:
        build_etablissement(et)


def build_etablissement(et: dict) -> None:
    page = f"etablissements/{et['slug']}/"
    trail = [("Accueil", ""), ("Établissements", "etablissements/"), (et["short"], page)]
    paras = "".join(f"<p>{e(p)}</p>" for p in et["body"])
    groups = [g["id"] for g in FORM["groups"] if g["etablissement"] == et["slug"]]
    forms = ""
    if groups:
        forms = f'<section class="sec sec-tint"><div class="wrap"><h2>Formations du {e(et["short"])}</h2>{formations_board(page, groups)}</div></section>'
    audio = ""
    if et.get("audio"):
        players = "".join(f'<figure class="audio"><figcaption>{e(a["label"])}</figcaption>'
                          f'<audio controls preload="none" src="{link(page, "assets/audio/" + a["file"])}"></audio></figure>'
                          for a in et["audio"])
        audio = f'<h2 class="h-small">Écouter notre spot radio</h2><div class="audios">{players}</div>'
    body = f"""<div class="wrap page-head key-{et['key']}">{crumbs(page, trail)}
<div class="etab-head">{logo(page, et['slug'], 'etab-logo-lg', 112)}<div><h1>{e(et['name'])}</h1><p class="etab-role">{e(et['short'])}, {e(et['role'].lower())}</p></div></div></div>
<section class="sec sec-tight"><div class="wrap split">
  <div class="prose">{paras}{audio}</div>
  <aside class="side">{photo(page, et['photo'], '', '(min-width: 900px) 40vw, 100vw', 'side-img')}
    <div class="contact-box"><p class="cb-title">Contacter le {e(et['short'])}</p><p>{phones(et['phones'])}</p>
    <p><a href="mailto:{e(SITE['email'])}">{e(SITE['email'])}</a></p></div></aside>
</div></section>
{forms}
{cta_band(page)}"""
    write(page, page_html(page, f"{et['short']} : {et['name']}", f"{et['name']} ({et['short']}), {et['role'].lower()} à Bobo-Dioulasso. {et['summary']}",
                          body, [org_schema(et), breadcrumb(trail)], og_image=f"assets/og/{et['photo']}.jpg", active="etablissements/"))


def build_formations() -> None:
    page = "formations/"
    trail = [("Accueil", ""), ("Formations", page)]
    body = f"""<div class="wrap page-head">{crumbs(page, trail)}<h1>Formations</h1>
<p class="lead">{e(FORM_LEAD)}</p></div>
<section class="sec sec-tight"><div class="wrap">{formations_board(page)}</div></section>
{cta_band(page)}"""
    schema = [breadcrumb(trail), {"@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "url": f'{SITE["url"]}/formations/{it["slug"]}/', "name": it["title"]}
        for i, it in enumerate(ITEMS)]}]
    write(page, page_html(page, "Formations : filières professionnelles, bacs technologiques et généraux",
                          "Électrotechnique, électronique, génie civil, maintenance industrielle, agroalimentaire, comptabilité, secrétariat, bacs G2, F2, F3, F4, séries A4 et D à Bobo-Dioulasso.",
                          body, schema, active=page))
    for it in ITEMS:
        build_formation(it)


def build_formation(it: dict) -> None:
    page = f"formations/{it['slug']}/"
    g = GROUPS[it["group"]]
    et = ETAB[g["etablissement"]]
    trail = [("Accueil", ""), ("Formations", "formations/"), (it["title"], page)]
    learn = "".join(f"<li>{e(x)}</li>" for x in it["learn"])
    jobs = "".join(f"<li>{e(x)}</li>" for x in it["jobs"])
    access = "".join(f"<li>{e(x)}</li>" for x in g["access"])
    others = "".join(formation_link(page, o) for o in ITEMS if o["group"] == it["group"] and o["slug"] != it["slug"])
    img = photo(page, it.get("photo"), "", "(min-width: 900px) 40vw, 100vw", "side-img")
    jobs_title = it.get("jobs_title") or ("Exemples de métiers" if it["group"] in ("pro", "apprentissage") else "Débouchés et poursuite d'études")
    nxt = it.get("next", g["next"])
    title = it["title"] + (f" ({it['abbr']})" if it.get("abbr") and it["group"] == "pro" else "")
    body = f"""<div class="wrap page-head key-{et['key']}">{crumbs(page, trail)}
<p class="kicker"><a href="{link(page, 'etablissements/' + et['slug'] + '/')}">{e(et['short'])}</a>, {e(it['family'].lower())}</p>
<h1>{e(title)}</h1><p class="lead">{e(it['intro'])}</p></div>
<section class="sec sec-tight"><div class="wrap split">
  <div class="prose">
    <h2 class="h-small">Ce que vous apprenez</h2><ul class="ticks">{learn}</ul>
    <h2 class="h-small">Diplômes et accès</h2><p>{e(g['diplomas'])}.</p><ul>{access}</ul>
    <h2 class="h-small">{jobs_title}</h2><ul>{jobs}</ul>{f"<p>{e(nxt)}</p>" if nxt else ""}
  </div>
  <aside class="side">{img}<div class="contact-box"><p class="cb-title">{e(it.get('cta') or "S'inscrire en " + (it.get('abbr') or it['title'].lower()))}</p>
  <p><a class="btn btn-sun btn-block" href="{wa_url('Bonjour, je souhaite des informations sur la formation ' + it['title'] + '.')}">Écrire sur WhatsApp</a></p>
  <p>{phones(et['phones'])}</p></div></aside>
</div></section>
<section class="sec sec-tint"><div class="wrap"><h2>{e(g["others_title"])}</h2><ul class="board-list board-list-inline">{others}</ul></div></section>"""
    schema = [breadcrumb(trail), {"@type": "Course", "name": it["title"], "description": it["intro"], "inLanguage": "fr",
                                  "provider": {"@type": et["schema_type"], "name": et["name"], "url": f'{SITE["url"]}/etablissements/{et["slug"]}/'}}]
    write(page, page_html(page, f"{title}, {et['short']} Bobo-Dioulasso",
                          f"{it['title']} au {et['short']} à Bobo-Dioulasso : {it['intro']} Programme, diplômes, conditions d'accès et débouchés.",
                          body, schema, og_image=f"assets/og/{it['photo']}.jpg" if it.get("photo") else "assets/og.jpg", active="formations/"))


def pieces_block() -> str:
    ins = SITE.get("inscription")
    if not ins:
        return ""
    lis = "".join(f"<li>{e(x)}</li>" for x in ins["pieces"])
    return f"""<section class="sec sec-tint"><div class="wrap">
<h2>Pièces à fournir pour l'inscription en {e(ins['annee'])}</h2>
<div class="prose"><ul class="ticks">{lis}</ul><p class="note">{e(ins['pieces_note'])}</p></div>
</div></section>"""


def build_admission() -> None:
    page = "admission/"
    trail = [("Accueil", ""), ("Admission", page)]
    rows = "".join(f"""<div class="adm key-{ETAB[g['etablissement']]['key']}"><h2 class="h-small">{e(g['title'])} <span class="nw">({e(ETAB[g['etablissement']]['short'])})</span></h2>
<p>{e(g['diplomas'])}.</p><ul>{''.join(f'<li>{e(a)}</li>' for a in g['access'])}</ul></div>""" for g in FORM["groups"])
    body = f"""<div class="wrap page-head">{crumbs(page, trail)}<h1>Admission</h1>
<p class="lead">Les inscriptions pour l'année {e(SITE['inscription']['annee'])} sont ouvertes. Elles se font auprès du secrétariat : contactez-le pour connaître les places disponibles et les frais de scolarité.</p></div>
<section class="sec sec-tight"><div class="wrap"><h2>Conditions d'accès</h2><div class="adms">{rows}</div>
</div></section>
{pieces_block()}
{cta_band(page, "Prêt à vous inscrire ?")}"""
    write(page, page_html(page, "Admission et inscriptions", "Conditions d'accès et inscriptions au LPTIC-B, au LPK et au CAFOT à Bobo-Dioulasso : BEP, bac professionnel, bacs technologiques, séries A4 et D.",
                          body, [breadcrumb(trail)], active=page))


def tabs(page: str, active: str) -> str:
    """Onglets du coin Actualités : de vrais liens, utilisables sans JavaScript et indexés par Google."""
    items = [("Toutes", "actualites/")] + [v for v in CATS.values()] + [("En images", "vie-scolaire/")]
    lis = "".join(f'<li><a href="{link(page, p)}"{" aria-current=\"page\"" if p == active else ""}>{e(n)}</a></li>'
                  for n, p in items)
    return f'<nav class="tabs" aria-label="Rubriques des actualités"><ul>{lis}</ul></nav>'


CAT_LEADS = {
    None: "Les nouvelles du LPTIC-B, du LPK et du CAFOT, le calendrier scolaire et des examens, et les informations officielles des ministères.",
    "etablissement": "Événements, cérémonies, visites d'entreprises et réussites de nos élèves.",
    "examens": "Dates des examens nationaux, calendrier scolaire et résultats.",
    "officiel": "Décisions et communiqués des ministères en charge de l'éducation, toujours avec le lien vers la source.",
}
CAT_EMPTY = {
    "etablissement": "Les prochains événements de l'établissement seront publiés ici.",
    "examens": "Les dates des examens de la session 2027 (CEP, BEPC, CAP, BEP et baccalauréat) seront publiées ici dès leur annonce officielle.",
    "officiel": "Les prochaines informations officielles seront publiées ici, avec leur source.",
}


def build_actualites() -> None:
    pages = [("actualites/", None, "Actualités")] + [(v[1], k, v[0]) for k, v in CATS.items()]
    for page, cat, title in pages:
        arts = [a for a in ARTICLES if cat is None or a["categorie"] == cat]
        trail = [("Accueil", ""), ("Actualités", "actualites/")] + ([(title, page)] if cat else [])
        listing = news_list(page, arts) if arts else f'<p class="empty">{e(CAT_EMPTY[cat])}</p>'
        if cat == "examens" and arts:
            listing += f'<p class="empty">{e(CAT_EMPTY["examens"])}</p>'
        side = ""
        if cat in (None, "examens"):
            side = f'<aside class="dates"><h2 class="h-small">Prochaines dates</h2>{agenda_list(page, upcoming())}</aside>'
        body = f"""<div class="wrap page-head">{crumbs(page, trail)}<h1>{e(title)}</h1>
<p class="lead">{e(CAT_LEADS[cat])}</p>{tabs(page, page)}</div>
<section class="sec sec-tight"><div class="wrap{' news-layout' if side else ''}"><div>{listing}</div>{side}</div></section>"""
        desc = f"{title} du LPTIC-B, du LPK et du CAFOT à Bobo-Dioulasso. {CAT_LEADS[cat]}"
        write(page, page_html(page, f"{title} : LPTIC-B, LPK et CAFOT" if cat else "Actualités", desc, body,
                              [breadcrumb(trail)], active="actualites/"))
    for a in ARTICLES:
        build_article(a)


def build_article(a: dict) -> None:
    ap = f"actualites/{a['slug']}/"
    cat_name, cat_page = CATS[a["categorie"]]
    t2 = [("Accueil", ""), ("Actualités", "actualites/"), (cat_name, cat_page), (a["title"], ap)]
    ph = a["photos"]
    imgs = ""
    if ph:
        imgs = photo(ap, ph[0], CAPTION.get(ph[0], ""), "(min-width: 760px) 720px, 100vw", "art-img")
        if len(ph) > 1:
            imgs += '<div class="art-grid">' + "".join(
                f'<figure>{photo(ap, s, CAPTION.get(s, ""), "(min-width: 760px) 240px, 50vw")}'
                f'{"<figcaption>" + e(CAPTION[s]) + "</figcaption>" if s in CAPTION else ""}</figure>' for s in ph[1:]) + "</div>"
    if a["affiches"]:
        figs = "".join(
            f'<figure><a href="{link(ap, "assets/photos/" + s + "-" + str(PHOTOS[s]["widths"][-1]) + ".webp")}">'
            f'{photo(ap, s, "Affiche des inscriptions " + ("du LPK" if "lpk" in s else "du LPTIC-B"), "(min-width: 760px) 360px, 50vw", "poster")}</a>'
            f'<figcaption>Agrandir l\'affiche {"du LPK" if "lpk" in s else "du LPTIC-B"}</figcaption></figure>' for s in a["affiches"] if s in PHOTOS)
        imgs = f'<div class="posters">{figs}</div>' + imgs
    vid = ""
    if a.get("video"):
        v = a["video"]
        vid = (f'<figure class="video"><video controls preload="none" playsinline width="540" height="720" '
                 f'poster="{link(ap, "assets/video/" + v + "-poster.webp")}">'
                 f'<source src="{link(ap, "assets/video/" + v + ".mp4")}" type="video/mp4"></video>'
                 f'<figcaption>{e(a.get("video_titre", ""))} ({e(a.get("video_duree", ""))}{", " if a.get("video_duree") else ""}{mo(ASSETS / "video" / (v + ".mp4"))}). Son contenu est repris dans le texte ci-dessus.</figcaption></figure>')
    source = ""
    if a.get("source"):
        source = f'<p class="source">Source : <a href="{e(a["source"])}">{e(a.get("source_nom", a["source"]))}</a></p>'
    abody = f"""<article class="wrap article">{crumbs(ap, t2)}
<p class="news-meta"><a class="tag tag-{a['categorie']}" href="{link(ap, cat_page)}">{e(cat_name)}</a><time datetime="{a['date']}">{fr_date(a['date'])}</time></p>
<h1>{e(a['title'])}</h1>
{imgs}<div class="prose">{md(a['body'])}{source}</div>{vid}</article>
{cta_band(ap)}"""
    schema = [breadcrumb(t2), {"@type": "NewsArticle", "headline": a["title"], "datePublished": a["date"], "inLanguage": "fr",
                               "image": [f'{SITE["url"]}/assets/og/{s}.jpg' for s in ([a["og"]] if a.get("og") else ph[:1])],
                               "publisher": {"@type": "HighSchool", "name": ETAB["lptic-b"]["name"]}}]
    og = f"assets/og/{a['og']}.jpg" if a.get("og") else (f"assets/og/{ph[0]}.jpg" if ph else "assets/og.jpg")
    write(ap, page_html(ap, a["title"], a["summary"], abody, schema, og_image=og, active="actualites/"))


def build_vie_scolaire() -> None:
    page = "vie-scolaire/"
    trail = [("Accueil", ""), ("Actualités", "actualites/"), ("En images", page)]
    figs = "".join(f"""<figure><a href="{link(page, 'assets/photos/' + g['photo'] + '-' + str(PHOTOS[g['photo']]['widths'][-1]) + '.webp')}">
{photo(page, g['photo'], g['caption'], '(min-width: 900px) 33vw, (min-width: 560px) 50vw, 100vw')}</a><figcaption>{e(g['caption'])}</figcaption></figure>"""
                   for g in GALERIE)
    body = f"""<div class="wrap page-head">{crumbs(page, trail)}<h1>La vie scolaire en images</h1>
<p class="lead">Travaux pratiques, chantiers, visites d'entreprises et cérémonies.</p>{tabs(page, page)}</div>
<section class="sec sec-tight"><div class="wrap"><div class="gallery">{figs}</div></div></section>"""
    write(page, page_html(page, "La vie scolaire en images", "Photos de la vie scolaire du LPTIC-B, du LPK et du CAFOT à Bobo-Dioulasso : ateliers, chantiers, visites et cérémonies.",
                          body, [breadcrumb(trail)], active="actualites/"))


def build_contact() -> None:
    page = "contact/"
    trail = [("Accueil", ""), ("Contact", page)]
    a = SITE["address"]
    boxes = "".join(f"""<div class="contact-card key-{et['key']}"><h2 class="h-small">{e(et['short'])}</h2><p class="etab-role">{e(et['name'])}</p><p>{phones(et['phones'])}</p></div>"""
                    for et in ETABS)
    body = f"""<div class="wrap page-head">{crumbs(page, trail)}<h1>Contact</h1>
<p class="lead">Le plus rapide : un message WhatsApp au secrétariat.</p>
<p class="actions"><a class="btn btn-sun" href="{wa_url()}">Écrire sur WhatsApp</a><a class="btn btn-line" href="mailto:{e(SITE['email'])}">Envoyer un e-mail</a></p></div>
<section class="sec sec-tight"><div class="wrap">
<div class="contacts">{boxes}</div>
<div class="address"><h2 class="h-small">Adresse</h2><p>{e(a['street'])}, {e(a.get('landmark', ''))}<br>{e(a['locality'])}, Burkina Faso<br>Courrier : {e(a['po_box'])}</p>
<p>WhatsApp : {wa_numbers()}<br>E-mail : <a href="mailto:{e(SITE['email'])}">{e(SITE['email'])}</a></p></div>
</div></section>"""
    write(page, page_html(page, "Contact", "Téléphones, WhatsApp, e-mail et adresse du LPTIC-B, du LPK et du CAFOT, secteur 24, Bobo-Dioulasso.",
                          body, [breadcrumb(trail)] + [org_schema(et) for et in ETABS], active=page))


def build_partenaires() -> None:
    page = "partenaires/"
    trail = [("Accueil", ""), ("Partenaires et remerciements", page)]
    grid = ""
    if PARTNERS["partners"]:
        cells = "".join(f"""<li><a href="{e(p.get('url', '#'))}"><img src="{link(page, 'assets/partenaires/' + p['logo'])}" alt="{e(p['name'])}" loading="lazy" height="72"></a><span>{e(p['name'])}</span></li>"""
                        for p in PARTNERS["partners"])
        grid = f'<ul class="partners">{cells}</ul>'
    body = f"""<div class="wrap page-head">{crumbs(page, trail)}<h1>Partenaires et remerciements</h1>
<p class="lead">{e(PARTNERS['intro'])}</p></div>
<section class="sec sec-tight"><div class="wrap">{grid}
<div class="prose"><h2 class="h-small">Soutenir nos établissements</h2><p>Entreprise, association ou institution : pour accueillir des stagiaires, organiser une visite ou soutenir un projet, écrivez-nous à <a href="mailto:{e(SITE['email'])}">{e(SITE['email'])}</a>.</p></div>
</div></section>"""
    write(page, page_html(page, "Partenaires et remerciements", "Les partenaires du LPTIC-B, du LPK et du CAFOT à Bobo-Dioulasso et nos remerciements.",
                          body, [breadcrumb(trail)]))


def build_mentions() -> None:
    page = "mentions-legales/"
    trail = [("Accueil", ""), ("Mentions légales", page)]
    body = f"""<div class="wrap page-head">{crumbs(page, trail)}<h1>Mentions légales</h1></div>
<section class="sec sec-tight"><div class="wrap prose">
<h2 class="h-small">Éditeur</h2><p>{e(ETAB['lptic-b']['name'])} (LPTIC-B), {e(street_full())}, {e(SITE['address']['locality'])}, Burkina Faso. Courrier : {e(SITE['address']['po_box'])}. E-mail : <a href="mailto:{e(SITE['email'])}">{e(SITE['email'])}</a>.</p>
<h2 class="h-small">Directeur de la publication</h2><p>{e(SITE['publication_director'])}.</p>
<h2 class="h-small">Hébergement</h2><p>{e(SITE['host'])}.</p>
<h2 class="h-small">Données personnelles</h2><p>Ce site ne collecte aucune donnée personnelle et n'utilise aucun cookie. Les boutons WhatsApp ouvrent l'application WhatsApp, dont la politique de confidentialité s'applique à vos échanges.</p>
<h2 class="h-small">Photos et droit à l'image</h2><p>Les photos appartiennent aux établissements. Elles sont publiées avec l'autorisation des personnes photographiées ou de leurs parents. Pour demander le retrait d'une photo, écrivez à l'adresse ci-dessus.</p>
<h2 class="h-small">Crédits</h2><p>Police de caractères Barlow Condensed, licence SIL Open Font License. Conception et réalisation du site : <a href="{SITE['credit']['url']}">{e(SITE['credit']['name'])}</a>.</p>
</div></section>"""
    write(page, page_html(page, "Mentions légales", "Mentions légales du site lpticb.com.", body, [breadcrumb(trail)]))


def build_404() -> None:
    body = f"""<div class="wrap page-head"><h1>Cette page n'existe pas</h1>
<p class="lead">L'adresse a peut-être changé. Repartez de l'accueil ou consultez les formations.</p>
<p class="actions"><a class="btn btn-sun" href="/">Revenir à l'accueil</a><a class="btn btn-line" href="/formations/">Voir les formations</a></p></div>"""
    html_ = page_html("404.html", "Page introuvable", "Cette page n'existe pas.", body).replace('href="assets/', 'href="/assets/').replace('src="assets/', 'src="/assets/')
    SITEMAP.remove("404.html")
    (OUT / "404.html").write_text(html_, encoding="utf-8")


def build_meta_files() -> None:
    today = date.today().isoformat()
    urls = "".join(f"<url><loc>{SITE['url']}/{p}</loc><lastmod>{today}</lastmod></url>" for p in SITEMAP)
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n', encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.xml\n", encoding="utf-8")
    (OUT / "CNAME").write_text(SITE["url"].split("//")[1] + "\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUT / "humans.txt").write_text(f"/* TEAM */\nConception et réalisation : {SITE['credit']['name']}\nSite : {SITE['credit']['url']}\n", encoding="utf-8")
    for f in (ROOT / "verification").glob("*.html"):  # fichier de vérification Google Search Console
        shutil.copy(f, OUT / f.name)


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ASSETS, OUT / "assets", ignore=shutil.ignore_patterns("manifest.json"))
    if LOCAL:  # navigateurs : pas de police chargée depuis file:// ; on l'intègre au CSS
        import base64
        css = (OUT / "assets" / "style.css").read_text(encoding="utf-8")
        for w in ("600", "700"):
            f = f"fonts/barlow-condensed-latin-{w}-normal.woff2"
            b64 = base64.b64encode((ASSETS / f).read_bytes()).decode()
            css = css.replace(f'url("{f}")', f'url("data:font/woff2;base64,{b64}")')
        (OUT / "assets" / "style.css").write_text(css, encoding="utf-8")
    build_home()
    build_etablissements()
    build_formations()
    build_admission()
    build_actualites()
    build_vie_scolaire()
    build_contact()
    build_partenaires()
    build_mentions()
    build_404()
    build_meta_files()
    print(f"{len(SITEMAP)} pages construites dans {OUT}{' (mode local)' if LOCAL else ''}")


if __name__ == "__main__":
    main()
