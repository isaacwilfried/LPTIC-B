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

L'ancienne version (Vite + React, mars 2025) est conservée dans la branche `archive/version-react-2025`. Suivi du projet : `docs/SUIVI.md`.

## Publier une actualité

1. Ajouter les photos : déclarer chaque photo dans `PHOTOS` de `tools/images.py`, puis `python tools/images.py "<dossier des originaux>"`.
2. Créer `content/actualites/AAAA-MM-JJ-titre-court.md` :

```
---
title: Titre de l'actualité
date: 2026-11-20
summary: Une ou deux phrases affichées dans la liste.
photos: slug-photo-1, slug-photo-2
---
Texte de l'article. Paragraphes séparés par une ligne vide. **Gras** et [liens](https://exemple.com) acceptés.
```

3. `python tools/build.py`, vérifier, puis pousser sur `main`.

## Ajouter un partenaire

Déposer le logo dans `assets/partenaires/` (PNG ou WebP, fond transparent) et ajouter une entrée dans `content/partenaires.json` :
`{"name": "Nom du partenaire", "logo": "fichier.webp", "url": "https://..."}`. Les logos apparaissent sur l'accueil et sur la page Partenaires et remerciements.

## Aperçu sans serveur

`python tools/build.py --local` construit une version qui s'ouvre en double-cliquant sur `_site/index.html`.

## Règles

- Aucune donnée personnelle d'élève dans ce dépôt.
- Aucun mot de passe, jeton ou clé dans le dépôt : les secrets vont dans GitHub, Settings, Secrets and variables, Actions.
- Photos d'élèves publiées seulement avec autorisation (obtenue pour les photos actuelles).
