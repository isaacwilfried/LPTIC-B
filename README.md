# lpticb.com

Site du LPTIC-B (lycée technique et professionnel), du Lycée Privé Kenntnis (LPK, enseignement général) et du CAFOT (centre de formation technique), à Bobo-Dioulasso.

Site statique, construit par un script Python sans dépendance et publié sur GitHub Pages par le workflow `.github/workflows/pages.yml` à chaque push sur `main`.

## Arborescence

| Dossier | Contenu |
| --- | --- |
| `content/` | Tout le contenu : `site.json` (contacts), `etablissements.json`, `formations.json`, `galerie.json`, `partenaires.json`, `actualites/*.md` |
| `assets/` | Feuille de style, police (Barlow Condensed, licence OFL), logos, photos WebP, spots radio, icônes |
| `tools/build.py` | Générateur : `python tools/build.py` produit le site dans `_site/` |
| `tools/images.py` | Prépare les photos (recadrage, WebP 480/960/1600). Nécessite Pillow |

Ne jamais modifier le HTML produit : tout passe par `content/` puis `tools/build.py`.

## Publier une actualité

1. Ajouter les photos : déclarer chaque photo dans `PHOTOS` de `tools/images.py`, puis `python tools/images.py "<dossier des originaux>"`.
2. Créer `content/actualites/AAAA-MM-JJ-titre-court.md` :

```
---
title: Titre de l'actualité
date: 2026-11-20
summary: Une ou deux phrases affichées dans la liste.
photos: slug-photo-1, slug-photo-2
categorie: etablissement        (ou examens, officiel)
a_la_une: oui                   (facultatif : mise en avant sur l'accueil)
affiches: slug-affiche-1, slug-affiche-2   (facultatif : affiches jamais recadrées)
video: nom-video                (facultatif : assets/video/nom-video.mp4 et nom-video-poster.webp)
video_titre: Titre de la vidéo
video_duree: 1 min 7 s
og: nom-image                   (facultatif : assets/og/nom-image.jpg, 1200 x 630, pour WhatsApp et Facebook)
source: https://...             (obligatoire pour une info officielle)
source_nom: Nom de la source
---
Texte de l'article. Paragraphes séparés par une ligne vide. **Gras** et [liens](https://exemple.com) acceptés.
```

Dans le texte, `## Titre` crée un intertitre et les lignes commençant par `- ` une liste.

3. `python tools/build.py`, vérifier, puis pousser sur `main`.

Vidéo : ré-encoder avant de l'ajouter, par exemple
`ffmpeg -i source.mp4 -vf scale=540:-2 -c:v libx264 -preset veryfast -crf 27 -movflags +faststart -c:a aac -b:a 64k -ac 1 assets/video/nom-video.mp4`.

## Masquer une filière

Ajouter `"masque": true` à la filière dans `content/formations.json` : sa page disparaît du site sans perdre le texte.

## Ajouter un partenaire

Déposer le logo dans `assets/partenaires/` (PNG ou WebP, fond transparent) et ajouter une entrée dans `content/partenaires.json` :
`{"name": "Nom du partenaire", "logo": "fichier.webp", "url": "https://..."}`. Les logos apparaissent sur l'accueil et sur la page Partenaires et remerciements.

## Aperçu sans serveur

`python tools/build.py --local` construit une version qui s'ouvre en double-cliquant sur `_site/index.html`.

## Règles

- Aucune donnée personnelle d'élève dans ce dépôt.
- Aucun mot de passe, jeton ou clé dans le dépôt : les secrets vont dans GitHub, Settings, Secrets and variables, Actions.
- Photos d'élèves publiées seulement avec autorisation (obtenue pour les photos actuelles).
