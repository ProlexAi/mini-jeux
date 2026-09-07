# Compose une planche de style a partir de captures du VRAI rendu du jeu
# (pas d'artwork externe - voir PIPELINE-ASSETS-IA.md piege 9). Les captures
# versionnees dans game_captures/ (dataset_NN.png) viennent de screenshots
# manuels du jeu (menu Couleurs + effet "predateur" pour les dents, tailles
# et virages varies). Reprendre de nouvelles captures si le rendu du jeu
# change - voir la methode canvas.toBlob() documentee dans PIPELINE-ASSETS-IA.md
# si un script de capture automatique est prefere a des screenshots manuels.
#
# Usage : python3 build_style_sheet.py
#         COMFYUI_INPUT_DIR=/chemin/vers/ComfyUI/input python3 build_style_sheet.py

from PIL import Image
import os
import math

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(SCRIPT_DIR, "game_captures")
# Dossier d'entree de ComfyUI, ou la planche est aussi deposee pour servir de
# reference. Il change d'une machine a l'autre (C:\ComfyUI\input sous Windows,
# ~/ComfyUI/input sous Linux) : on le declare par la variable d'environnement
# COMFYUI_INPUT_DIR, sinon on retombe sur le defaut de la plateforme courante.
# La copie reste optionnelle (voir le os.path.isdir en fin de fichier) : le
# livrable est OUT_REPO, versionne dans le depot.
OUT_DIR = os.environ.get(
    "COMFYUI_INPUT_DIR",
    r"C:\ComfyUI\input" if os.name == "nt" else os.path.expanduser("~/ComfyUI/input"),
)
OUT_REPO = os.path.join(SCRIPT_DIR, "snakeon_style_sheet.png")

TILE_W, TILE_H = 320, 260

files = sorted(f for f in os.listdir(SRC) if f.lower().endswith(".png"))
print(f"{len(files)} captures : {files}")

COLS = 5
ROWS = math.ceil(len(files) / COLS)

sheet = Image.new("RGB", (TILE_W * COLS, TILE_H * ROWS), (10, 10, 15))

for i, fname in enumerate(files):
    im = Image.open(os.path.join(SRC, fname)).convert("RGB")
    # contain-fit : redimensionne sans rogner, complete au fond noir du jeu
    ratio = min(TILE_W / im.width, TILE_H / im.height)
    new_w, new_h = int(im.width * ratio), int(im.height * ratio)
    im = im.resize((new_w, new_h), Image.LANCZOS)
    col = i % COLS
    row = i // COLS
    x0 = col * TILE_W + (TILE_W - new_w) // 2
    y0 = row * TILE_H + (TILE_H - new_h) // 2
    sheet.paste(im, (x0, y0))

sheet.save(OUT_REPO)
print("saved (repo)", OUT_REPO, sheet.size)

if os.path.isdir(OUT_DIR):
    sheet.save(os.path.join(OUT_DIR, "snakeon_style_sheet.png"))
    print("saved (comfyui input)", os.path.join(OUT_DIR, "snakeon_style_sheet.png"))
