#!/usr/bin/env python3
"""Calcul INDEPENDANT des codewords QR (mode octet), pour confronter l'encodeur JS.

Ecrit d'apres la specification, sans reutiliser une ligne du JS : c'est tout l'interet.
"""
import json
import subprocess
import sys

S = "/tmp/claude-1000/-home-matt-mini-jeux/78d3de99-bd21-488d-8c2e-40bc76d86b7a/scratchpad"

TOTAL_CW = [0,26,44,70,100,134,172,196,242,292,346,404,466,532,581,655,733,815,901,991,1085]
EC_PB = {"M": [0,10,16,26,18,24,16,18,22,22,26,30,22,22,24,24,28,28,26,26,26,26]}
NB_BLOCS = {"M": [0,1,1,1,2,2,4,4,4,5,5,5,8,9,9,10,10,11,13,14,16,17]}

# --- GF(256) ---
EXP = [0]*512; LOG = [0]*256
x = 1
for i in range(255):
    EXP[i] = x; LOG[x] = i
    x <<= 1
    if x & 0x100:
        x ^= 0x11D
for i in range(255, 512):
    EXP[i] = EXP[i-255]

def mul(a, b):
    return 0 if a == 0 or b == 0 else EXP[LOG[a] + LOG[b]]

def gen_poly(d):
    p = [1]
    for i in range(d):
        q = p + [0]
        for j in range(len(p)):
            q[j+1] ^= mul(p[j], EXP[i])
        p = q
    return p

def rs(data, nb):
    g = gen_poly(nb)
    r = [0]*nb
    for oct_ in data:
        f = oct_ ^ r[0]
        r = r[1:] + [0]
        for j in range(nb):
            r[j] ^= mul(g[j+1], f)
    return r

def codewords(texte, v, niv):
    octets = list(texte.encode("utf-8"))
    cap = TOTAL_CW[v] - EC_PB[niv][v] * NB_BLOCS[niv][v]
    bits = "0100" + format(len(octets), "08b" if v <= 9 else "016b")
    bits += "".join(format(o, "08b") for o in octets)
    bits += "0" * min(4, cap*8 - len(bits))
    while len(bits) % 8:
        bits += "0"
    cw = [int(bits[i:i+8], 2) for i in range(0, len(bits), 8)]
    pad = [0xEC, 0x11]
    i = 0
    while len(cw) < cap:
        cw.append(pad[i % 2]); i += 1
    return cw

TEXTE, NIV, V = "HELLO WORLD", "M", 1
ref_cw = codewords(TEXTE, V, NIV)
ref_ec = rs(ref_cw, EC_PB[NIV][V])
ref_flux = ref_cw + ref_ec

js = f"""
const fs = require('fs');
const src = fs.readFileSync('{S}/qr.js','utf8');
const mod = {{ exports: {{}} }};
new Function('module','exports','require', src + '\\nmodule.exports.__d = {{ construireDonnees, entrelacer }};')(mod, mod.exports, require);
const d = mod.exports.__d;
const octets = Array.from(new TextEncoder().encode({json.dumps(TEXTE)}));
const cw = d.construireDonnees(octets, {V}, {json.dumps(NIV)});
console.log(JSON.stringify({{ cw, flux: d.entrelacer(cw, {V}, {json.dumps(NIV)}) }}));
"""
out = subprocess.run(["node", "-e", js], capture_output=True, text=True)
if out.returncode != 0:
    print("ERREUR NODE :", out.stderr[:500]); sys.exit(1)
mien = json.loads(out.stdout)

print("codewords de DONNEES")
print("  reference :", " ".join(f"{c:3d}" for c in ref_cw))
print("  maison    :", " ".join(f"{c:3d}" for c in mien["cw"]))
print("  ->", "identiques" if ref_cw == mien["cw"] else "DIFFERENTS")
print()
print("flux complet (donnees + correction)")
print("  reference :", " ".join(f"{c:3d}" for c in ref_flux))
print("  maison    :", " ".join(f"{c:3d}" for c in mien["flux"]))
print("  ->", "identiques" if ref_flux == mien["flux"] else "DIFFERENTS")
