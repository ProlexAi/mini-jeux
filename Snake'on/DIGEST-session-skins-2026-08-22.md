# Digest de session — Skins et prédation par masse

**22/08/2026 · branche `claude/snakeon-skins-system-af98cf` · 17 commits depuis `c9dcf73`**

---

## En une phrase

Les skins changent enfin le serpent et non plus sa seule couleur ; la prédation se joue
désormais sur une masse sans plafond selon le modèle agar.io ; et un liseré de menace dit d'un
coup d'œil s'il faut foncer ou fuir.

---

## Les cinq décisions actées

1. **Un skin est une forme + éventuellement une aura.** Le cœur du corps reste intact sur tous :
   c'est le repère de lisibilité, et il est non négociable.
2. **La masse décide de tout** — prédation et vitesse. Elle n'a aucun plafond ; la longueur
   affichée et le rayon en ont, mais ce sont des contraintes de rendu, pas des règles.
3. **Modèle agar.io : +25 % de masse pour absorber.** Pas de marge nulle, pas de comparaison sur
   une grandeur plafonnée.
4. **La lisibilité passe par l'ordre de dessin**, pas par la retenue. L'aura déborde franchement,
   le liseré et le cœur sont tracés par-dessus.
5. **Le monde suit l'échelle d'agar.io** — 58 écrans — et son peuplement suit sa taille.

---

## Les chiffres qui comptent

| Grandeur | Valeur | Note |
|---|---|---|
| Skins | 13 | 10 formes + 3 auras |
| Seuil de prédation | +25 % de masse | modèle agar.io |
| Monde | 13872 × 8670 | 120,3 Mpx², agar.io en fait 121 |
| Bots | 150 | 10,4 visibles à l'écran en moyenne |
| Pastilles | 5467 | densité inchangée |
| Plafond de masse des bots | 1500 | le joueur n'en a aucun |
| Coût image médian | 2,6 ms | budget 16,67 ms |
| Ancrages d'aura | 18 à 90 | borné, ne suit pas la longueur |

---

## Les six défauts corrigés

Chacun est documenté avec sa preuve dans le rapport de session.

- Pointillés avalés par `lineCap:'round'` — **0 pixel** modifié.
- Traînée émise à la tête, recouverte en permanence par le corps.
- Éclairs figés sur trois positions à vie : `(k*A + t*B) % 23` avec `B` multiple de 23.
- Aura débordant à 3 r pour un plafond de 1,8 : le plafond portait sur le centre des taches.
- Masse tombant au plancher après amputation.
- Bot atteignant 31 574 de masse et saturant l'écran.

---

## L'enseignement de méthode

**Quatre faux diagnostics sont venus de l'instrument, aucun du code.** Canvas non effacé entre
les passes, tête du serpent hors cadre, écart mesuré entre deux points encadrant l'élément
cherché, et `window.innerWidth` à zéro dans un panneau non composité.

> Avant de conclure qu'un correctif ne marche pas : vérifier le cache du navigateur, vérifier
> que le viewport n'est pas nul, et vérifier que la mesure couvre exactement ce que
> l'affirmation prétend.

---

## Ce qui attend une décision

**Un seul point, et il revient à Matt.** Une découpe joue le son de kill et les particules de
mort mais ne compte pas comme un kill — mesuré, la cible perd la moitié de son corps, survit, et
le compteur reste à zéro. Le compteur fonctionne ; c'est le retour sensoriel qui ment.
Recommandation : distinguer le retour sensoriel plutôt que faire compter la découpe, sans quoi
le même serpent serait « tué » dix fois.

---

## Documents produits

| Fichier | Rôle |
|---|---|
| `analyse-concurrence.md` | Mémoire des recherches sur les concurrents, pour ne plus les refaire |
| `PROMPT-effets-succes-boutique.md` | Passation : effets déblocables, succès, boutique |
| `RAPPORT-session-skins-2026-08-22.md` | Rapport détaillé de cette session |
| `cahier-des-charges-ui.md` | Addenda v0.4 et v0.5, validés avant écriture |

---

## Prochaine session

`PROMPT-effets-succes-boutique.md` est prêt : découpler forme et effet, pour que les dix formes
puissent recevoir des effets débloqués via succès, séries de kills ou boutique. Il porte les six
questions à trancher et les pièges déjà rencontrés.
