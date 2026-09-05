# Controle rejouable : OUT_DIR de build_style_sheet.py doit rendre un chemin
# adapte a la plateforme courante, et ceder devant COMFYUI_INPUT_DIR.
#
# Usage :  python3 verifie-chemins.py [chemin/vers/build_style_sheet.py]
# Sortie 0 si les deux branches sont correctes ET distinctes, 1 sinon.
#
# Pourquoi la plateforme n'est PAS simulee : une premiere version forcait
# os.name a "posix" tout en gardant le vrai os.path de Windows ; expanduser
# rendait alors un hybride du genre C:\Users\Matth/ComfyUI/input et le
# controle criait au defaut alors que le code etait juste. L'instrument
# etait faux. On joue donc sur la plateforme reelle : chaque cote prouve la
# branche qu'il atteint, et jouer le controle sous Windows ET sous Linux
# couvre les deux. Un seul cote ne prouve pas l'autre.
#
# Le bloc teste est EXTRAIT du fichier source par analyse syntaxique, pas
# recopie ici : si build_style_sheet.py change, ce controle suit.

import ast
import io
import os
import os.path
import sys

cible = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "build_style_sheet.py")

source = io.open(cible, "r", encoding="utf-8").read()
bloc = None
for noeud in ast.parse(source).body:
    if isinstance(noeud, ast.Assign) and getattr(noeud.targets[0], "id", None) == "OUT_DIR":
        bloc = ast.get_source_segment(source, noeud)
if bloc is None:
    print("ECHEC : aucune affectation OUT_DIR trouvee dans " + cible)
    sys.exit(2)


def evalue(surcharge):
    """Execute le bloc OUT_DIR avec un environnement controle, puis restaure."""
    garde = dict(os.environ)
    os.environ.pop("COMFYUI_INPUT_DIR", None)
    os.environ.update(surcharge)
    espace = {"os": os}
    try:
        exec(bloc, espace)
    finally:
        os.environ.clear()
        os.environ.update(garde)
    return espace["OUT_DIR"]


PREFIXE_WINDOWS = "C:" + chr(92) + "ComfyUI"
FORCE = "/srv/comfy/input"

plateforme = "Windows" if os.name == "nt" else "Linux"
print("plateforme reelle : %s (os.name=%s)" % (plateforme, os.name))
print("fichier controle  : %s" % cible)
print()

defaut = evalue({})
force = evalue({"COMFYUI_INPUT_DIR": FORCE})
print("  branche DEFAUT   (%s, sans variable) -> %s" % (plateforme, defaut))
print("  branche VARIABLE (COMFYUI_INPUT_DIR) -> %s" % force)
print()

ok = True
if force != FORCE:
    print("ECHEC : la variable d'environnement ne prime pas (obtenu %s)" % force)
    ok = False
if defaut == force:
    print("ECHEC : les deux branches rendent la meme valeur, une seule est exercee")
    ok = False

if os.name == "nt":
    if not defaut.startswith(PREFIXE_WINDOWS):
        print("ECHEC : sous Windows le defaut devrait commencer par %s, obtenu %s"
              % (PREFIXE_WINDOWS, defaut))
        ok = False
    print("  (branche Linux non atteignable ici : elle se prouve sous Linux)")
else:
    if chr(92) in defaut or not defaut.startswith("/") or not defaut.endswith("/ComfyUI/input"):
        print("ECHEC : sous Linux le defaut devrait etre un chemin POSIX absolu "
              "finissant par /ComfyUI/input, obtenu %s" % defaut)
        ok = False
    print("  (branche Windows non atteignable ici : elle se prouve sous Windows)")

print()
print("VERDICT : %s" % ("branches correctes sur cette plateforme" if ok else "DEFAUT"))
sys.exit(0 if ok else 1)
