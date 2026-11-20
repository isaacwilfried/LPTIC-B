"""Prépare les photos du site : recadrage, suppression des dates incrustées,
conversion en WebP à plusieurs largeurs.

Usage (sur l'ordinateur qui contient les originaux) :
    python tools/images.py "D:/SITE_LPTIC/Photos site Web"

Dépendance : Pillow (pip install pillow). Les fichiers produits vont dans
assets/photos/ et sont versionnés ; le site lui-même n'a besoin d'aucune
dépendance pour être construit.
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "photos"
WIDTHS = (480, 960, 1600)
QUALITY = 72

# slug -> (fichier d'origine, recadrage en fractions (gauche, haut, droite, bas))
# Les photos DSC_* portent une date incrustée en bas à droite : on retire 11 % en bas.
STAMP = (0, 0, 1, 0.89)
PHOTOS = {
    # Affiches officielles : jamais recadrées (texte jusqu'aux bords)
    "affiche-lptic-b-2026": ("Affiche inscriptions LPTIC-B 2026-2027.jpg", None),
    "affiche-lpk-2026": ("Affiche inscriptions LPK 2026-2027.jpg", None),
    "atelier-percage": ("DSC_0081.JPG", STAMP),
    "tableau-electrique": ("DSC_0054.JPG", STAMP),
    "dessin-atelier": ("DSC_0044.JPG", STAMP),
    "chantier-ecole": ("DSC_9928.JPG", STAMP),
    "fondations": ("DSC_9935.JPG", STAMP),
    "groupe-genie-civil": ("DSC_9950.JPG", STAMP),
    "atelier-neuf": ("DSC_9962.JPG", STAMP),
    "batiments": ("IMG_20190823_103902.jpg", (0, 0.12, 1, 1)),
    "montee-des-couleurs": ("IMG-20221024-WA0004.jpg", None),
    "visite-cimasso": ("IMG-20210519-WA0006.jpg", None),
    "visite-usine": ("PICT0003.JPG", None),
    "panneaux-solaires": ("IMG_20201008_173554_2.jpg", None),
    "oscilloscopes": ("IMG-20220406-WA0017.jpg", None),
    "montage-electronique": ("PICT0053.JPG", None),
    "cablage": ("PICT0041.JPG", None),
    "maconnerie": ("IMG_20210413_102034_7.jpg", None),
    "parpaings": ("IMG_20210318_102809_6.jpg", None),
    "metallerie": ("PICT0027.JPG", None),
    "cadres-metalliques": ("Cadres des tables.JPG", None),
    "salle-informatique": ("PICT0449.JPG", None),
    "salle-de-classe": ("PICT0427.JPG", None),
    "eleves-en-classe": ("PICT0430.JPG", None),
    "eleves-devant-les-classes": ("PICT0443.JPG", None),
    "apprenti-etabli": ("PICT0032.JPG", None),
    "ceremonie-tenues-traditionnelles": ("PICT0132.JPG", None),
    "sortie-pedagogique": ("SAM_0688.JPG", None),
    "banc-electrotechnique": ("IMG_20221104_141242_1.jpg", None),
}


def save_og(im: Image.Image, slug: str) -> None:
    """Vignette de partage 1200x630 en JPEG : WhatsApp et Facebook l'affichent quand on partage la page."""
    target = 1200 / 630
    w, h = im.size
    if w / h > target:
        nw = round(h * target)
        im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = round(w / target)
        top = round((h - nh) * 0.4)
        im = im.crop((0, top, w, top + nh))
    (OUT.parent / "og").mkdir(exist_ok=True)
    im.resize((1200, 630), Image.LANCZOS).save(OUT.parent / "og" / f"{slug}.jpg", quality=74, optimize=True, progressive=True)


def process(src_dir: Path) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for slug, (name, crop) in PHOTOS.items():
        im = ImageOps.exif_transpose(Image.open(src_dir / name)).convert("RGB")
        if crop:
            w, h = im.size
            l, t, r, b = crop
            im = im.crop((round(l * w), round(t * h), round(r * w), round(b * h)))
        widths = []
        for target in WIDTHS:
            if target > im.width and widths:
                break
            w = min(target, im.width)
            out = im if w == im.width else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
            out.save(OUT / f"{slug}-{w}.webp", "WEBP", quality=QUALITY, method=6)
            widths.append(w)
        manifest[slug] = {"widths": widths, "ratio": round(im.width / im.height, 4)}
        save_og(im, slug)
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    m = process(Path(sys.argv[1]))
    print(f"{len(m)} photos traitées dans {OUT}")
