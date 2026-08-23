# Digest de session — Boutique et gouvernance documentaire

**23/08/2026 · branche `claude/snakeon-skins-system-af98cf`**

---

## En une phrase

Le dépôt se dote d'un routeur de lecture inspiré de Profundus, et l'entrée `A01` devient une
**boutique à deux catégories** — ce qui a d'abord exigé de découpler l'effet de la forme.

---

## Les deux livrables

### `_MANIFEST.md` — gouvernance

Routeur de lecture, calqué sur le `_MANIFEST.md` de Profundus mais ramené à l'échelle de ce
dépôt : huit documents, pas cent. Il **ne duplique rien et ne porte aucun chiffre**.

Ce qui a été repris, et pourquoi :

| Idée reprise | Ce qu'elle apporte ici |
|---|---|
| Routeur, pas source de vérité | dit quoi lire et dans quel ordre, sans se périmer |
| Table « où est la vérité » | supprime la question « où est-ce écrit ? » |
| **Classification par nature** | canon / vivant / log / machinerie, avec le geste quand chacun devient faux |
| Aucun chiffre dans un document | la valeur vit dans `CONFIG`, le document cite la commande qui la relit |

Ce qui a été **écarté** volontairement : archives, index de rapports à vocabulaire fermé,
arborescence auto-synchronisée par hook, classification de péremption N1-N4. Utiles à un projet
de cent documents, purement encombrants pour huit.

### La boutique

Entrée `A01` renommée **« 🛒 Boutique »** (`Shop` en anglais), deux catégories :

- **Effets** — ouverte par défaut, comme demandé.
- **Skins** — la grille des dix formes, inchangée. Son enrichissement revient à une autre session.

---

## Ce que la boutique a exigé au préalable

**Découpler l'effet de la forme.** Les trois auras étaient des skins à part entière, aux index
10 à 12, donc **exclusives** des dix formes : porter du feu imposait de renoncer à sa forme. Une
catégorie « Effets » n'aurait rien eu à contenir.

Elles vivent maintenant dans `CONFIG.EFFECTS` et se posent **par-dessus** une forme.
`currentStyle()` fusionne les deux, l'effet l'emportant sur les clés qu'il définit. **40
combinaisons** au lieu de 13 choix exclusifs.

**Migration des sauvegardes.** Un joueur revenant avec une aura la retrouve — conversion en
forme 0 + effet correspondant — plutôt que d'être remis en Cyan sans explication.

---

## Mesures

| Contrôle | Résultat |
|---|---|
| Combinaisons forme × effet jouées | **40 / 40**, rendu et minimap compris, zéro erreur |
| Migration des anciens index | correcte sur 4 cas (10, 11, 12 et un index normal) |
| Verrou de niveau | repli silencieux sur « aucun », jamais d'erreur |
| Fusion des styles | le pointillé de la forme et l'aura de l'effet coexistent |
| Catégorie par défaut | « Effets », avec `aria-selected` correct à la bascule |
| Sélection d'un effet | ne touche pas la forme |
| Traductions | 6 langues, aucune clé brute |

---

## Coordination

Cette session et celle de la partie privée ont travaillé le même fichier en parallèle.
Enseignement partagé, formulé par l'autre session : **deux sessions qui commitent sur la même
branche locale finissent par pousser le travail l'une de l'autre sans l'avoir relue.** C'est
arrivé — j'ai publié un de ses commits en poussant `main`. Il était légitime et testé, mais je
ne l'avais pas relu. La parade est de travailler chacun dans sa branche, et de ne merger
qu'après s'être annoncé.

**Un trou trouvé chez elle par ricochet** : le protocole ne transporte pas l'apparence. Un joueur
distant apparaît chez les autres avec sa seule couleur, sans forme ni aura. Le défaut préexistait
à mes skins — à l'époque un skin n'était qu'une couleur, et la couleur voyageait. Le découplage
le rend simplement visible. **Le sujet lui appartient**, il est inscrit à ce qui reste ouvert.

---

## Ce qui attend une décision

**Le cahier des charges est périmé sur un point** et ne peut pas être modifié en autonomie : la
table du §3.A décrit encore l'entrée `A01` comme « 🎨 Skins — Grille de 13 skins ». Elle en porte
désormais dix, plus quatre effets, sous le nom « Boutique ». Un bloc « MODIFICATIONS DOC
PROPOSÉES » est soumis à Matt.

**Non tranché, et volontairement laissé ouvert :** la boutique n'a **aucune monnaie**. Les effets
s'y débloquent par niveau, comme les formes. Introduire une monnaie gagnée en partie est une
décision de conception qui n'a pas été prise — elle figure parmi les six questions de
`PROMPT-effets-succes-boutique.md`.
