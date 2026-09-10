#!/usr/bin/env python3
"""Confronte l'encodeur QR maison a segno, matrice a matrice.

Le controle porte son propre temoin : un cas SABOTE doit etre detecte comme different.
Si le sabotage passait inapercu, la comparaison ne vaudrait rien et le script sort en erreur.
"""
import json
import subprocess
import sys

import segno

S = "/tmp/claude-1000/-home-matt-mini-jeux/78d3de99-bd21-488d-8c2e-40bc76d86b7a/scratchpad"

CAS = [
    ("court ascii", "HELLO WORLD", "M"),
    ("court niveau L", "HELLO WORLD", "L"),
    ("accents utf8", "Snake'on — sauvegarde é à ü", "M"),
    ("url courte", "https://prolexai.github.io/mini-jeux/Snake'on/", "M"),
    ("120 octets", "x" * 120, "M"),
    ("300 octets", "y" * 300, "M"),
    ("801 caracteres (cas reel)", "https://prolexai.github.io/mini-jeux/Snake%27on/#s=" + "A" * 750, "M"),
    ("1200 caracteres", "z" * 1200, "L"),
]


def matrice_maison(texte, niveau, saboter=False):
    js = f"""
const {{ encoder }} = require('{S}/qr.js');
const r = encoder({json.dumps(texte)}, {json.dumps(niveau)});
let m = r.m.map(l => Array.from(l));
{'m[5][5] ^= 1;' if saboter else ''}
console.log(JSON.stringify({{ v: r.v, t: r.t, masque: r.masque, m }}));
"""
    out = subprocess.run(["node", "-e", js], capture_output=True, text=True)
    if out.returncode != 0:
        return None, out.stderr.strip()
    return json.loads(out.stdout), None


def matrice_segno(texte, niveau):
    q = segno.make(texte, error=niveau, mode="byte", boost_error=False, micro=False)
    lignes = [list(map(int, row)) for row in q.matrix]
    return {"v": q.version, "t": len(lignes), "m": lignes}


echecs = 0
print(f"{'cas':<28} {'version':>8} {'taille':>7}  verdict")
print("-" * 66)

for nom, texte, niveau in CAS:
    mien, err = matrice_maison(texte, niveau)
    if mien is None:
        print(f"{nom:<28} {'--':>8} {'--':>7}  ERREUR NODE : {err[:40]}")
        echecs += 1
        continue
    ref = matrice_segno(texte, niveau)
    if mien["v"] != ref["v"]:
        print(f"{nom:<28} {mien['v']:>8} {mien['t']:>7}  VERSION DIFFERENTE (segno: {ref['v']})")
        echecs += 1
        continue
    identique = mien["m"] == ref["m"]
    if identique:
        print(f"{nom:<28} {mien['v']:>8} {mien['t']:>7}  identique a segno")
    else:
        diff = sum(1 for a, b in zip(sum(mien["m"], []), sum(ref["m"], [])) if a != b)
        print(f"{nom:<28} {mien['v']:>8} {mien['t']:>7}  DIFFERENT ({diff} modules)")
        echecs += 1

# --- TEMOIN : un sabotage doit etre vu -----------------------------------------------------
print()
sab, _ = matrice_maison("HELLO WORLD", "M", saboter=True)
ref = matrice_segno("HELLO WORLD", "M")
if sab and sab["m"] != ref["m"]:
    print("temoin OK : une matrice sabotee d'UN SEUL module est bien detectee comme differente")
else:
    print("TEMOIN MUET : le sabotage n'a pas ete vu — la comparaison ne prouve rien")
    sys.exit(2)

print()
if echecs:
    print(f"ECHEC : {echecs} cas divergent de la reference.")
    sys.exit(1)
print(f"OK : {len(CAS)} cas identiques a segno, module par module.")
