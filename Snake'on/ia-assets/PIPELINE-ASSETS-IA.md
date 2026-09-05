# Pipeline de génération d'assets IA pour les skins

> **Ce document décrit l'installation Windows / DirectML.** Après la bascule vers
> Kubuntu 26.04, les chemins `C:\ComfyUI` et le backend `--directml` ne s'appliquent plus :
> voir la fiche **F1** de `docs/migration-linux/rapport-snakeon-2026-09-05.html` pour la
> reconstruction en **ROCm**, qui supporte officiellement la RX 7900 GRE. Le figeage sur
> le tag `v0.7.0` tombe avec DirectML : il venait d'une incompatibilité propre à
> `torch-directml`. Le dossier d'entrée se déclare désormais par la variable
> `COMFYUI_INPUT_DIR` (voir `build_style_sheet.py` et son contrôle `verifie-chemins.py`).

**Portée :** cette note documente une infrastructure installée le 2026-08-23 pour générer
des morceaux de skin (tête, segment de corps, décoration type aile/corne) en pièces
isolées et stylistiquement cohérentes, en vue de leur tamponnage sur la colonne
vertébrale du serpent — même mécanisme que celui déjà utilisé pour les auras
(`AURA_STEP`, `AURA_MAX_EXTENT` dans `index.html`).

**Le jeu reste 100 % procédural aujourd'hui** (aucune image bitmap, voir le README :
« aucune image, aucune lib »). Introduire des sprites bitmap tamponnés est un changement
d'architecture — à valider avec Matt avant intégration, cette note ne documente que la
génération, pas l'intégration en jeu.

## Infrastructure (niveau machine, hors dépôt)

- ComfyUI cloné dans `C:\ComfyUI` — outil partagé machine, pas versionné avec ce dépôt.
- GPU de la machine : AMD Radeon RX 7900 GRE, 16 Go VRAM. Pas de CUDA disponible → backend
  **DirectML** (`--directml`), pas ROCm (pas de support Windows pour les cartes grand public).
- venv Python 3.11 géré par `uv` dans `C:\ComfyUI\.venv` (Python système trop récent —
  3.13/3.14 — pour les wheels PyTorch au moment de l'installation).
- Démarrage :
  ```powershell
  cd C:\ComfyUI
  .\.venv\Scripts\python.exe main.py --directml
  ```
  API HTTP sur `http://127.0.0.1:8188`.

## Pièges rencontrés (mesurés cette session, à ne pas retraverser)

1. **ComfyUI mainline (v0.33+) casse `torch-directml`.** Depuis le commit introduisant
   `comfy_kitchen` (janvier 2026), le chargement exige une API torch que
   `torch-directml` (bloqué sur torch 2.4.1, non maintenu par Microsoft depuis plus d'un
   an) ne fournit pas — `ValueError: infer_schema()...`. **Le dépôt local est figé sur le
   tag `v0.7.0`** (`git checkout v0.7.0` dans `C:\ComfyUI`), dernier tag avant ce commit.
   Vérifier avant toute mise à jour : `git log --oneline -S "comfy-kitchen" -- requirements.txt`.

2. **Le README de `ComfyUI_IPAdapter_plus` piège sur l'encodeur CLIP-Vision SDXL.**
   Il indique de télécharger `h94/IP-Adapter/sdxl_models/image_encoder/model.safetensors`
   et de le renommer `CLIP-ViT-H-14-...`, mais ce fichier (3,44 Go) est en réalité un
   encodeur **bigG** (sortie 1664 dim), pas ViT-H (1280 dim) — mesuré au runtime via
   l'erreur `size mismatch ... torch.Size([1280, 1664])`. Pour les poids IPAdapter
   `*_vit-h` (ex. `ip-adapter-plus_sdxl_vit-h.safetensors`), télécharger plutôt
   `h94/IP-Adapter/models/image_encoder/model.safetensors` (2,35 Go, lignée SD1.5, sans
   ambiguïté sur la dimension).

3. **`IPAdapterUnifiedLoader` met le CLIP-Vision en cache mémoire process.** Remplacer le
   fichier sur disque sans redémarrer le serveur ComfyUI ne prend pas effet — le nœud
   réutilise l'instance déjà chargée. Toujours redémarrer le process après un changement
   de fichier modèle.

4. **`weight` IPAdapter au-delà de ~1.2 avec `weight_type="strong style transfer"` fait
   diverger la génération** en bruit saturé (testé à 1.4 : image verte uniforme, aucun
   contenu). Plage qui fonctionne : `weight=0.8-1.0`, `weight_type="style transfer"`.

5. **Le choix du checkpoint pèse plus que le réglage du poids IPAdapter** pour respecter
   un style de référence « rendu propre / plat » (par opposition à peint / anime) :
   - `illustrious-xl-v0.1.safetensors` (fort biais illustration peinte / anime) écrase le
     style de la référence quel que soit le poids IPAdapter testé (0.8 → 1.4).
     **Réfuté et supprimé** (2026-08-23, 6,9 Go libérés) — voir « Modèles réfutés ».
   - `sd_xl_base_1.0.safetensors` (SDXL 1.0 de base, neutre) laisse le style de la
     référence s'exprimer correctement, à poids identique.
   → **Choisir le checkpoint selon le style cible du skin**, pas un choix universel.

6. **Ne jamais générer l'illustration complète puis découper les morceaux après coup.**
   Un outil d'édition IA (testé : Claude Design) à qui on demande d'isoler une zone la
   **régénère** au lieu de l'extraire — résultat visuellement mauvais. Générer chaque
   pièce **séparément dès le départ**, avec IPAdapter conditionné sur un recadrage propre
   de l'image de référence (fond neutre, une seule vue, labels texte retirés).

7. **IPAdapter conditionné sur poids > ~0.5 recopie le SUJET de la référence, pas
   seulement son style — même avec `weight_type="style transfer"`.** Mesuré en tentant de
   générer une tête de serpent stylisée façon casque de football à partir d'un recadrage
   du casque seul (`crop_eyeshield_helmet.png`) : à `weight=1.0` comme à `weight=0.55`, le
   résultat est un casque de football photoréaliste **sans aucune tête de serpent** — le
   sujet de la référence (le casque) écrase le sujet du prompt texte. Descendre à
   `weight=0.2-0.35` restaure le sujet du prompt, au prix d'un style moins marqué.

8. **Le checkpoint de base (`sd_xl_base_1.0`) a un biais fort vers l'illustration
   figurative complète (bouche ouverte, crocs, yeux détaillés, scène), même quand le
   prompt ne le demande pas.** Repousser ce biais avec des negative prompts déplace juste
   *où* le modèle dérive (ex. : suppression du contour noir → le rendu bascule en 3D
   glossy avec reflet spéculaire et ombre portée). Symétriquement, demander une texture
   abstraite (« seamless tileable texture », sans mots figuratifs) ne corrige pas le
   problème : à poids IPAdapter élevé, le modèle recopie alors servilement le **bruit** de
   l'image de référence (grille de fond, pastilles de nourriture) plutôt qu'une texture de
   peau cohérente. Correctifs qui aident sans suffire seuls : référencer le **rendu réel du
   jeu** plutôt qu'un artwork d'inspiration externe (voir piège 9), et recadrer cette
   référence serré sur le sujet (peu de fond vide) pour renforcer le signal utile.

9. **Le style visuel réel du jeu (glow néon plat, liseré coloré fin, sans contour noir,
   sans écailles, yeux = 2 points noirs) ne se retrouve dans aucun LoRA de style testé** —
   ni `DD-vector-v2` (vector art à contours noirs épais type BD/clipart, réfuté), ni les
   LoRAs « neon glow » trouvés sur HuggingFace (orientés effet de lumière sur sujet
   classique, pas un registre « tube flat sans contour »). **Vérifier le style réel en jeu
   avant de juger un rendu IA « conforme »** — comparer aux artworks d'inspiration
   uniquement induit en erreur. La référence la plus fidèle mesurée est une **planche de
   captures du jeu lui-même** (pas un artwork externe) : voir [`build_style_sheet.py`](build_style_sheet.py)
   et le dataset versionné dans [`game_captures/`](game_captures). Résultat encore
   imparfait avec IPAdapter seul (yeux trop détaillés, liseré parfois mal interprété comme
   une forme de fond) mais nettement plus proche que tout artwork externe.

11. **`ComfyUI-GGUF` (quantification GGUF, utilisée pour faire tenir Flux.1 en VRAM) est
    incompatible avec le backend DirectML de cette machine.** Mesuré en tentant Flux.1-schnell
    `Q6_K.gguf` : le `KSampler` échoue avec `NotImplementedError: Cannot access storage of
    OpaqueTensorImpl` — le stockage packé des tenseurs quantifiés GGUF n'est pas exposé par
    torch-directml. Ce n'est pas un problème de lenteur (comme les pièges 7/10) mais un
    blocage dur. Non testé : Flux en fp8 safetensors classique (non quantifié GGUF), qui
    pourrait ne pas avoir le même problème de stockage — mais risque équivalent d'atteindre
    un autre opérateur non supporté par torch-directml (voir piège 10, DirectML est
    globalement mal maintenu).

## Dataset de style et entraînement cloud (Leonardo.ai)

Piste retenue face aux limites locales (pièges 7 à 11) : un dataset de captures du **vrai
jeu** (pas d'artwork externe), utilisé soit comme référence IPAdapter, soit comme dataset
d'entraînement d'un modèle de style custom sur un service cloud (Leonardo.ai — catégorie
« Style » de leur outil « Train New Model », pas DreamBooth/objet/personnage).

- **Dataset versionné** : [`game_captures/`](game_captures) — 17 captures manuelles du jeu
  (`dataset_01.png` à `dataset_17.png`), prises par Matt via le menu **Boutique → Couleurs**
  (pour varier les teintes) et l'**effet « Prédateur »** (Réglages en jeu) pour la variante
  avec crocs visibles. Régénérer la planche composite avec `python build_style_sheet.py`
  (sort dans `snakeon_style_sheet.png` et, si présent, `C:\ComfyUI\input\`).
- Pour un ré-entraînement futur avec un dataset plus riche : varier aussi la taille du
  serpent (petit/gros) et les angles de virage, viser 20+ images.
- Upload fait manuellement un par un sur Leonardo.ai par Matt (pas d'API utilisée depuis
  cette session — la clé API reste entièrement côté utilisateur, jamais manipulée ici).

10. **L'entraînement LoRA local sur cette machine (Windows + AMD RX 7900 GRE, backend
    DirectML) n'est pas praticable — mesuré, pas juste documenté ailleurs.** Trois preuves
    convergentes :
    - Test empirique direct : le backward pass de `GroupNorm` (omniprésent dans l'UNet
      SDXL) retombe sur CPU sous DirectML (`native_group_norm_backward` non supporté,
      warning PyTorch). Pas un blocage dur, mais un vrai risque de lenteur.
    - Microsoft déclare officiellement que LoRA/SDXL training n'est « pas supporté à ce
      jour » par son extension DirectML officielle.
    - Un développeur d'AUTOMATIC1111 confirme : `torch.autocast` n'est pas implémenté sous
      DirectML — bloquant pour un entraînement en précision mixte.
    Le seul chemin d'entraînement SDXL LoRA AMD documenté avec des rapports de succès est
    **Linux + ROCm** (`kohya_ss`/`sd-scripts`). ROCm 7.2 (mars 2026) supporte officiellement
    la RX 7900 GRE, mais son support Windows reste limité à un preview Ollama — pas la
    pile compute complète. → si un entraînement custom devient nécessaire, passer par un
    GPU cloud CUDA (le plus simple) ou un dual-boot/VM Linux+ROCm, pas cette machine telle
    quelle.

## Modèles installés (`C:\ComfyUI\models\`)

| Fichier | Rôle | Statut |
|---|---|---|
| `checkpoints\sd_xl_base_1.0.safetensors` | Checkpoint neutre | **Validé** pour un style rendu propre/plat |
| `checkpoints\cartoonxl_v10.safetensors` | Checkpoint SDXL « flat vector cartoon », civitai.com/models/391852 (6,46 Go) | En cours de test (2026-08-23) — biais figuratif de `sd_xl_base_1.0` pas encore résolu par le seul prompt+style sheet |
| `loras\SDXL-StickerSheet-Lora.safetensors` | LoRA sticker sheet, huggingface.co/Norod78/SDXL-StickerSheet-Lora (29 Mo, MIT) | Téléchargée, pas encore testée |
| `clip_vision\CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors` | Encodeur image IPAdapter | Le bon fichier (2,35 Go) — voir piège 2 |
| `ipadapter\ip-adapter-plus_sdxl_vit-h.safetensors` | Poids IPAdapter Plus SDXL | — |

**Modèles testés et supprimés** (VRAM/disque limités sur cette machine — un seul modèle de
style actif à la fois, les réfutés sont retirés) :

| Fichier | Rôle | Motif du rejet |
|---|---|---|
| `checkpoints\illustrious-xl-v0.1.safetensors` | Checkpoint peint/anime | Écrase le style de la référence quel que soit le poids IPAdapter (piège 5) |
| `loras\DD-vector-v2.safetensors` | LoRA vector art, huggingface.co/DoctorDiffusion (228 Mo) | Contours noirs épais type BD/clipart, incompatible avec le style sans-contour du jeu |

## Custom nodes installés (`C:\ComfyUI\custom_nodes\`)

- **ComfyUI_IPAdapter_plus** (cubiq) — conditionnement par image de référence. En mode
  maintenance depuis avril 2025 ; fork actif si besoin :
  `chflame163/ComfyUI_IPAdapter_plus_V2`.
- **ComfyUI-RMBG** (1038lab) — détourage unifié (RMBG-2.0, BiRefNet, **Lucida** —
  recommandé spécifiquement pour illustration/line-art —, BEN2, SAM). Installé mais pas
  encore utilisé en pratique : reste à faire.

## Recette validée (tête générée à partir d'un corps de référence sans tête)

- Checkpoint : `sd_xl_base_1.0.safetensors`
- Référence IPAdapter : recadrage propre du segment de corps (`ref_body.png`), pas
  l'image multi-panneaux brute
- `weight=1.0`, `weight_type="style transfer"`, preset `PLUS (high strength)`
- 1024×1024, 25 steps, cfg 6.0, sampler `dpmpp_2m` / scheduler `karras`
- ~70 s par génération sur cette machine (mesuré, DirectML)

Script réexécutable, versionné dans ce dossier : [`generate_piece.ps1`](generate_piece.ps1).
Exemple :
```powershell
.\generate_piece.ps1 -RefImage "ref_body.png" -Prompt "snake head, side view, closed mouth, calm expression, matching material and color of the reference" -FilenamePrefix "skin_ice_head"
```
Le fichier de référence (`-RefImage`) doit exister dans `C:\ComfyUI\input\`.

## Reste à faire (pas encore testé)

- Tuile de corps répétable tamponnée le long de la colonne (même mécanisme que
  `AURA_STEP` dans `index.html`, mais motif discret plutôt que dégradé continu)
- Décorations débordantes (ailes/cornes) alignées symétriquement gauche/droite
- Détourage effectif des pièces générées avec ComfyUI-RMBG (modèle Lucida)
- Décision d'intégration en jeu : introduire des sprites bitmap tamponnés est un
  changement d'architecture assumé, pas une contrainte technique — à valider avec Matt
