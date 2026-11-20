# Suivi du projet (fichier de reprise)

Document complet (décisions, cahier des charges, état de l'art) : « Projet LPTIC-B — Suivi, cahier des charges et état de l'art », partagé par Isaac. Ce fichier n'en garde que l'essentiel pour reprendre le travail à partir du dépôt.

## Contexte

- Site commun de trois établissements d'un même promoteur à Bobo-Dioulasso (secteur 24) : LPTIC-B (enseignement technique et professionnel), LPK, Lycée Privé Kenntnis (enseignement général, séries A4 et D), CAFOT, Centre d'Apprentissage et de Formation Technique.
- Domaine : lpticb.com (GoDaddy, compte d'Isaac, payé jusqu'au 23/10/2027).
- Pilotage : Isaac. Développement, contenus et publication : Claude, via ce dépôt.

## Décisions en vigueur

| # | Décision |
| --- | --- |
| D1 | Site statique, publié par GitHub Pages via `.github/workflows/pages.yml` |
| D2 | Code dans `isaacwilfried/LPTIC-B` ; l'ancienne version React (mars 2025) est archivée dans la branche `archive/version-react-2025` |
| D3 | Le futur portail élèves sera un projet séparé, jamais sur GitHub Pages (mots de passe, données de mineurs, loi burkinabè n°001-2021/AN) |
| D6 | Un seul site pour les trois établissements, une couleur par établissement : bleu LPTIC-B, vert LPK, rouge CAFOT |
| D7 | Générateur Python sans dépendance (`tools/build.py`), contenu dans `content/` |
| D9 | Coin Actualités à onglets : Vie de l'établissement, Examens et calendrier, Infos officielles, En images. Agenda des prochaines dates (`content/agenda.json`) mis à jour chaque matin par une reconstruction planifiée |

## Règles

- Aucune donnée personnelle d'élève dans ce dépôt, aucun secret.
- Toute information officielle (ministère, examens) cite sa source avec un lien.
- Photos d'élèves : autorisations obtenues pour les photos actuelles ; toute nouvelle photo identifiable suppose l'accord des familles.

## En attente du promoteur

- Position GPS du lycée et lien Google Maps.
- Filières du CAFOT (liste, durée, conditions d'entrée).
- Agroalimentaire et série F4 : toujours ouvertes ? (absentes de sa correction du 20/11/2026)
- Électromécanique et CAP : dans quelles filières le CAP est-il préparé ?
- Contacts à confirmer (numéro WhatsApp du secrétariat, e-mail), horaires du secrétariat.
- Liste et logos des partenaires, nom du partenaire allemand.
- Directeur de la publication, accord pour la mention « Réalisation : Jovian Labs ».

## Journal

| Date | Fait |
| --- | --- |
| 20/11/2026 | Nouvelle version du site (31 pages) : établissements, formations, admission, actualités, galerie, contact, partenaires, mentions légales. Corrections du promoteur intégrées (accroche, CAFOT, CAP, électromécanique). |
