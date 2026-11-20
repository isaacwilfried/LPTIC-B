# Suivi du projet (fichier de reprise)

Document complet (décisions, cahier des charges, état de l'art) : « Projet LPTIC-B — Suivi, cahier des charges et état de l'art », partagé par Isaac. Ce fichier n'en garde que l'essentiel pour reprendre le travail à partir du dépôt.

## Contexte

- Site commun de trois établissements d'un même promoteur à Bobo-Dioulasso. Le LPTIC-B et le LPK partagent le même site (Kua, secteur 24, zone artisanale, à 100 m au sud du CSPS) ; le CAFOT est sur un autre site, adresse à venir. Établissements : LPTIC-B (enseignement technique et professionnel), LPK, Lycée Privé Kenntnis (enseignement général : post-primaire 6e-3e, puis séries A4 et D), CAFOT, Centre d'Apprentissage et de Formation Technique (dont mécanique automobile).
- Domaine : lpticb.com (GoDaddy, compte d'Isaac, payé jusqu'au 23/10/2027).
- Pilotage, développement et publication : Isaac (Jovian Labs), via ce dépôt.

## Décisions en vigueur

| # | Décision |
| --- | --- |
| D1 | Site statique, publié par GitHub Pages via `.github/workflows/pages.yml` |
| D2 | Code dans `isaacwilfried/LPTIC-B` ; l'ancienne version React (mars 2025) est archivée dans la branche `archive/version-react-2025` |
| D3 | Le futur portail élèves sera un projet séparé, jamais sur GitHub Pages (mots de passe, données de mineurs, loi burkinabè n°001-2021/AN) |
| D6 | Un seul site pour les trois établissements, une couleur par établissement : bleu LPTIC-B, vert LPK, rouge CAFOT |
| D7 | Générateur Python sans dépendance (`tools/build.py`), contenu dans `content/` |
| D9 | Coin Actualités à onglets : Vie de l'établissement, Examens et calendrier, Infos officielles, En images. Agenda des prochaines dates (`content/agenda.json`) mis à jour chaque matin par une reconstruction planifiée |
| D10 | Dépôt public (gratuit, aucun secret dedans) ; un dépôt privé avec Pages demanderait GitHub Pro, environ 4 $/mois |
| D11 | Offre affichée = affiches officielles 2026-2027. Une filière non ouverte est masquée (`"masque": true` dans `content/formations.json`), pas supprimée |
| D12 | Vidéos ré-encodées en H.264 540×720 (environ 1,3 Mo la minute), jamais préchargées, avec image d'attente et texte équivalent |
| D13 | Mention « Réalisation : Jovian Labs » approuvée par le promoteur |

## Règles

- Aucune donnée personnelle d'élève dans ce dépôt, aucun secret.
- Toute information officielle (ministère, examens) cite sa source avec un lien.
- Photos d'élèves : autorisations obtenues pour les photos actuelles ; toute nouvelle photo identifiable suppose l'accord des familles.

## En attente du promoteur

- Lien Google Maps précis du lycée (le repère actuel est décalé de quelques mètres) et adresse du CAFOT, qui est sur un autre site.
- Valider ou corriger le brouillon de plan `docs/plan/plan-campus-brouillon.png` (rôle de chaque bâtiment).
- Filières du CAFOT en plus de la mécanique automobile (liste, durée, conditions d'entrée).
- CAS et électromécanique : ouvertes en 2026-2027 ? (absentes de l'affiche). Agroalimentaire et F4 masquées en attendant.
- CAP : dans quelles filières est-il préparé ? Seconde TI toujours ouverte (l'affiche ne cite que les terminales F2 et F3) ?
- Le spot vidéo dit « établissement privé conventionné » : à confirmer avant de l'écrire sur le site.
- Pièces à fournir : la liste de l'affiche du LPK vaut-elle aussi pour le LPTIC-B ?
- Horaires du secrétariat ; e-mail à confirmer.
- Liste et logos des partenaires, nom du partenaire allemand.
- Nom du directeur de la publication.

## Journal

| Date | Fait |
| --- | --- |
| 20/11/2026 | Nouvelle version du site (31 pages) : établissements, formations, admission, actualités, galerie, contact, partenaires, mentions légales. Corrections du promoteur intégrées (accroche, CAFOT, CAP, électromécanique). |
| 20/11/2026 | Affiches et spot vidéo 2026-2027 : article « Les inscriptions 2026-2027 sont ouvertes » à la une, pièces à fournir sur la page Admission, adresse précise, téléphone 70 01 02 42, second WhatsApp 70 39 46 16, post-primaire du LPK, mécanique automobile au CAFOT, agroalimentaire et F4 masquées. Brouillon de plan du site. |
| 20/11/2026 | Le CAFOT est sur un autre site que les lycées : son adresse n'est plus confondue avec celle du LPTIC-B et du LPK (pied de page, contact, données Google). Domaine lpticb.com renseigné sur GitHub ; reste la zone DNS chez GoDaddy. |
