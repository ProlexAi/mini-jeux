# Digest — session « Partie privée », 22/08/2026

**Livré sur `main` (`303f5dd`), poussé et déployé.** 19 commits.
Vérifié en téléchargeant le fichier réellement servi : identique à `main` hors fins de ligne.

Jouer : <https://prolexai.github.io/mini-jeux/Snake%27on/>

---

## Ce que le jeu sait faire en plus

Plusieurs joueurs dans **la même arène**, réunis par un **code de 5 caractères** qu'on se dicte
(alphabet sans `0`/`O` ni `1`/`I`/`L`). Bouton **🌐 Partie Privée** (`A06`) à l'Accueil, écran de
**Salon** pour créer ou rejoindre. On peut **rejoindre en cours de partie** : on apparaît aussitôt,
protégé par le bouclier d'apparition.

**Pair-à-pair (WebRTC/PeerJS)** : la partie ne transite par aucun serveur, seule la mise en
relation passe par un annuaire public. Aucun compte, aucune donnée hors de l'appareil — la
progression reste dans le navigateur, comme en solo. Le solo n'a acquis aucune dépendance : PeerJS
n'est chargé qu'à l'ouverture du Salon, le jeu reste jouable hors-ligne.

---

## Décisions actées

| # | Décision | Motif |
|---|---|---|
| §5.23 | **Quitter ne coûte plus rien** — toute sortie compte la vie (XP, stats, historique) | Une partie brève interrompue par un rendez-vous ne doit pas s'effacer. La punition ne protégeait rien : le jeu n'a pas de fin. |
| §5.24 | **Bannière spectateur : Continuer / Quitter** | Les deux encaissent identiquement ; seule la destination diffère. |
| §5.25 | Bouton `A06` **désactivé hors ligne, motif affiché** | Un bouton absent ne s'explique pas. |
| §5.26 | **Sortie subie ≠ sortie choisie** | On ne fait pas payer une panne au joueur. |
| §5.27 | **Un kill est une élimination complète, jamais une découpe** | Le compteur avait raison ; le retour sensoriel mentait. Faire compter la découpe aurait « tué » dix fois le même serpent. |
| §6 | **La pause ne fige plus le monde des autres** — le serpent passe sous IA | Un joueur en pause reste mangeable, et le jeu le lui dit. |

---

## Chiffres, tous mesurés dans un vrai Chrome (deux fenêtres visibles)

| | |
|---|---|
| Horloges hôte / client | +5001 ms / +5001 ms sur **5010 ms réels** |
| Latence du geste à son application chez l'hôte | **16 ms** (médiane, 5 mesures sur 5) |
| Serpents transmis à un client | **21 sur 149** — le filtrage par intérêt |
| Débit reçu par client | **6,58 ko/s** (≈59 ko/s en montée à 9 joueurs) |
| Erreurs console | **0** |
| Langues | 90 clés, 6 langues, complètes |

**Trajectoire du budget réseau** : ~200 ko/s (tout en JSON) → 125 (filtrage) → 39 (binaire) → 59
après le passage à 150 bots du chantier skins. Le filtrage absorbe le peuplement : le nombre de
serpents transmis n'augmente que de 43 % quand la population triple.

---

## Ce que seul un vrai navigateur a révélé

**Le navigateur suspend `requestAnimationFrame` dans une fenêtre cachée.** Mesuré chez un client :
**57 instantanés en 4 s hôte visible, 0 hôte minimisé.** L'hôte qui changeait d'onglet une seconde
figeait la partie de tout le monde sans le savoir — exactement ce que le §6 interdit, mais subi au
lieu d'être choisi. Corrigé par un Web Worker qui sert d'horloge de secours à l'hôte : 52
instantanés au lieu de 0. Aucun test hors navigateur réel ne pouvait le voir.

---

## Trois pièges de méthode, pour la prochaine fois

1. **Deux onglets d'une même fenêtre ne se mesurent pas.** Un seul est visible, l'autre est gelé.
   Il faut deux fenêtres réellement visibles — c'est écrit dans la procédure de test du README.
2. **Un critère de filtrage doit porter sur ce qui est vrai, pas sur ce qui est grand.** Ma
   première marge était proportionnelle à la longueur du serpent : 26 688 px pour un serpent de
   4448 segments, soit plus que le monde entier. Le filtrage ne filtrait plus rien (gain retombé
   de 65 % à 13 %). La boîte englobante réelle a réglé ça — un long serpent enroulé tient dans un
   mouchoir de poche.
3. **Mesurer le déplacement net n'est pas mesurer la distance parcourue.** Un serpent qui tourne
   en rond parcourt 476 px pour un déplacement net de 185 : mon instrument me l'a fait croire
   immobile. Valider l'instrument avant la conclusion.

---

## Coordination avec le chantier « skins et équilibrage »

Les deux sessions touchaient le même fichier et avaient résolu **le même problème** (prédation
figée, bots qui ne lâchent pas) de deux façons incompatibles. Matt a tranché : **le modèle masse
du chantier skins fait autorité**, le mien avait été repris d'un patch préexistant sans arbitrage.
J'ai retiré mes deux critères concurrents avant fusion — ce qui a réduit le merge à **cinq zones
de conflit**, toutes résolues en gardant les deux apports.

Trois apports de cette coordination ont directement changé le code livré :
- **`massValue` sur 4 octets et non 2** : sa mesure réelle (31 574 en quinze minutes, ~126 000
  projetés à une heure) contre ma simulation (57 500). Un Uint16 aurait bouclé en silence.
- **`innerWidth = 0`** dans un panneau non composité : m'a fait documenter un garde-fou qu'un
  refactor aurait supprimé faute d'en connaître la raison.
- **La minimap muette** : elle montre tous les serpents, y compris ceux que le filtrage exclut —
  ceux-là n'ont donc aucune masse à jour, et ce sont justement les menaces lointaines qu'on veut
  y repérer.

---

## Ce qui reste ouvert (§8 du cahier des charges)

- **Minimap d'un client** : points de taille fixe, sans liseré de menace. Conception arrêtée (un
  octet : 2 bits de menace + 4 d'amplitude, paquet devenu propre à chaque destinataire), reste à
  implémenter.
- **Reconnexion après coupure brève** : une coupure d'une seconde compte comme un départ. Assumé.
- **Écran de Salon en paysage mobile** : non maquetté, comme les autres écrans.

---

## Contrôles rejouables laissés au dépôt

```bash
node "Snake'on/verifie-traductions.js"
```

Échoue si une langue perd une clé, si le HTML en cite une inexistante, ou si une clé devient
morte. **Saboté dans ses trois sens** pour vérifier qu'il sait encore échouer.

La procédure de test de la partie privée à deux navigateurs est au README, section
« Tester en local ».
