# Travaux en cours — code qui ne marche PAS encore

Ce dossier ne contient **rien qui tourne dans le jeu**. Il garde du travail interrompu dont
l'état est connu, pour qu'une reprise ne reparte pas de zéro.

Rien ici n'est chargé par `Snake'on/index.html`. Si un fichier de ce dossier se met à
fonctionner, il quitte ce dossier.

---

## Encodeur QR — tâche `T-008`

**État : le placement des modules est faux. Ne pas utiliser.**

Écrit pour transporter une sauvegarde par code QR (le lien de reprise, lui, est livré et
fonctionne — voir Réglages → Sauvegarde). Arrêté sur critère d'arrêt, faute de méthode assumée :
ce critère n'avait pas été posé avant de commencer.

| Fichier | Rôle |
|---|---|
| `qr-encodeur-inacheve.js` | l'encodeur : mode octet, niveaux L et M, versions 1 à 40 |
| `qr-compare-a-segno.py` | confronte sa matrice à celle de **segno**, cas par cas |
| `qr-codewords-reference.py` | recalcule les codewords d'après la spec, sans réutiliser le JS |

### Ce qui est vérifié et tient — ne pas re-chercher

- tables de capacité et choix de version : les versions concordent sur 8 cas, de la v1 à la v25 ;
- polynômes générateurs Reed-Solomon : **conformes** aux valeurs officielles (degrés 7, 10, 13, 16) ;
- information de format : **les 16 valeurs L/M conformes** à la table ISO ;
- codewords données + correction : **identiques** à un calcul indépendant ;
- comptage des modules : 233 réservés, 208 libres = 26 codewords × 8, exact en v1.

### Ce qui reste faux

**Le placement, et lui seul.** En relisant la matrice de référence avec le parcours de
l'encodeur, on obtient **13 codewords exacts, puis un codeword parasite qui décale tout**.

### Deux corrections déjà trouvées, déjà appliquées

La seconde copie de l'information de format se place **7 modules dans la colonne 8, puis 8 dans
la ligne 8** — le module noir fixe occupe la huitième place de la colonne. Elle a été écrite dans
les deux mauvais sens successifs avant d'être corrigée.

### Une fausse piste à ne pas reprendre

Déduire la carte des modules de fonction en comparant des QR de contenus aléatoires **ne marche
pas** : à longueur égale, des modules de données ne varient jamais et passent pour de la
fonction. Le diagnostic qui en sort ne vaut rien.

### Pour reprendre

```sh
python3 -m venv /tmp/venv-qr && /tmp/venv-qr/bin/pip install segno
/tmp/venv-qr/bin/python docs/travaux-en-cours/qr-compare-a-segno.py
```

Les deux scripts ont un chemin `S = "…/scratchpad"` en tête, à faire pointer sur ce dossier.
`qr-compare-a-segno.py` porte son propre témoin : un module saboté doit être vu comme différent,
sinon il s'arrête au lieu de conclure.
