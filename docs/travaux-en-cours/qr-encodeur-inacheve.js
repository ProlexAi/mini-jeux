// Encodeur QR minimal — mode octet uniquement, niveaux L et M, versions 1 a 40.
// Ecrit pour Snake'on, qui n'a aucune dependance : importer une bibliotheque tierce dans un
// fichier unique de 8400 lignes coutait plus cher que ces ~200 lignes ciblees.
//
// Verifie contre segno (implementation de reference, venv jetable) : matrice a matrice.

'use strict';

// Total de codewords (donnees + correction) par version, index 1..40.
const TOTAL_CW = [0,26,44,70,100,134,172,196,242,292,346,404,466,532,581,655,733,815,901,991,
  1085,1156,1258,1364,1474,1588,1706,1828,1921,2051,2185,2323,2465,2611,2761,2876,3034,3196,
  3362,3532,3706];

// Codewords de correction PAR BLOC, par niveau puis version.
const EC_PER_BLOCK = {
  L: [0,7,10,15,20,26,18,20,24,30,18,20,24,26,30,22,24,28,30,28,28,28,28,30,30,26,28,30,30,30,
      30,30,30,30,30,30,30,30,30,30,30],
  M: [0,10,16,26,18,24,16,18,22,22,26,30,22,22,24,24,28,28,26,26,26,26,28,28,28,28,28,28,28,28,
      28,28,28,28,28,28,28,28,28,28,28],
};
// Nombre de BLOCS, par niveau puis version.
const NUM_BLOCKS = {
  L: [0,1,1,1,1,1,2,2,2,2,4,4,4,4,4,6,6,6,6,7,8,8,9,9,10,12,12,12,13,14,15,16,17,18,19,19,20,
      21,22,24,25],
  M: [0,1,1,1,2,2,4,4,4,5,5,5,8,9,9,10,10,11,13,14,16,17,17,18,20,21,23,25,26,28,29,31,33,35,
      37,38,40,43,45,47,49],
};
// Coordonnees des motifs d'alignement par version.
const ALIGN = [[],[],[6,18],[6,22],[6,26],[6,30],[6,34],[6,22,38],[6,24,42],[6,26,46],[6,28,50],
  [6,30,54],[6,32,58],[6,34,62],[6,26,46,66],[6,26,48,70],[6,26,50,74],[6,30,54,78],[6,30,56,82],
  [6,30,58,86],[6,34,62,90],[6,28,50,72,94],[6,26,50,74,98],[6,30,54,78,102],[6,28,54,80,106],
  [6,32,58,84,110],[6,30,58,86,114],[6,34,62,90,118],[6,26,50,74,98,122],[6,30,54,78,102,126],
  [6,26,52,78,104,130],[6,30,56,82,108,134],[6,34,60,86,112,138],[6,30,58,86,114,142],
  [6,34,62,90,118,146],[6,30,54,78,102,126,150],[6,24,50,76,102,128,154],[6,28,54,80,106,132,158],
  [6,32,58,84,110,136,162],[6,26,54,82,110,138,166],[6,30,58,86,114,142,170]];

// --- Corps de Galois GF(256), polynome generateur 0x11D ---------------------------------
const EXP = new Uint8Array(512), LOG = new Uint8Array(256);
(function initGF() {
  let x = 1;
  for (let i = 0; i < 255; i++) { EXP[i] = x; LOG[x] = i; x <<= 1; if (x & 0x100) x ^= 0x11D; }
  for (let i = 255; i < 512; i++) EXP[i] = EXP[i - 255];
})();
const mul = (a, b) => (a === 0 || b === 0) ? 0 : EXP[LOG[a] + LOG[b]];

function polyGen(degre) {
  let p = [1];
  for (let i = 0; i < degre; i++) {
    const q = [...p, 0];
    for (let j = 0; j < p.length; j++) q[j + 1] ^= mul(p[j], EXP[i]);
    p = q;
  }
  return p;
}

function reedSolomon(donnees, nbEc) {
  const gen = polyGen(nbEc);
  const reste = new Uint8Array(nbEc);
  for (const octet of donnees) {
    const facteur = octet ^ reste[0];
    reste.copyWithin(0, 1); reste[nbEc - 1] = 0;
    for (let j = 0; j < nbEc; j++) reste[j] ^= mul(gen[j + 1], facteur);
  }
  return reste;
}

// --- Choix de version ---------------------------------------------------------------------
function capaciteDonnees(v, niv) {
  return TOTAL_CW[v] - EC_PER_BLOCK[niv][v] * NUM_BLOCKS[niv][v];
}
function choisirVersion(nbOctets, niv) {
  for (let v = 1; v <= 40; v++) {
    const enTete = 4 + (v <= 9 ? 8 : 16);           // indicateur de mode + longueur
    if (capaciteDonnees(v, niv) * 8 >= enTete + nbOctets * 8) return v;
  }
  return -1;
}

// --- Flux binaire -------------------------------------------------------------------------
function construireDonnees(octets, v, niv) {
  const bits = [];
  const push = (val, n) => { for (let i = n - 1; i >= 0; i--) bits.push((val >> i) & 1); };
  push(0b0100, 4);                                   // mode octet
  push(octets.length, v <= 9 ? 8 : 16);
  for (const o of octets) push(o, 8);
  const capaciteBits = capaciteDonnees(v, niv) * 8;
  push(0, Math.min(4, capaciteBits - bits.length));  // terminateur
  while (bits.length % 8) bits.push(0);
  const cw = [];
  for (let i = 0; i < bits.length; i += 8) cw.push(parseInt(bits.slice(i, i + 8).join(''), 2));
  const remplissage = [0xEC, 0x11];
  for (let i = 0; cw.length < capaciteDonnees(v, niv); i++) cw.push(remplissage[i % 2]);
  return cw;
}

// Entrelacement : les blocs sont repartis en deux groupes, le second ayant un codeword de plus.
function entrelacer(cw, v, niv) {
  const nbBlocs = NUM_BLOCKS[niv][v], nbEc = EC_PER_BLOCK[niv][v];
  const totalDonnees = cw.length;
  const court = Math.floor(totalDonnees / nbBlocs);
  const nbLongs = totalDonnees % nbBlocs;
  const blocs = [], blocsEc = [];
  let p = 0;
  for (let i = 0; i < nbBlocs; i++) {
    const taille = court + (i >= nbBlocs - nbLongs ? 1 : 0);
    const bloc = cw.slice(p, p + taille); p += taille;
    blocs.push(bloc);
    blocsEc.push(reedSolomon(bloc, nbEc));
  }
  const sortie = [];
  for (let i = 0; i < court + 1; i++) for (const b of blocs) if (i < b.length) sortie.push(b[i]);
  for (let i = 0; i < nbEc; i++) for (const b of blocsEc) sortie.push(b[i]);
  return sortie;
}

// --- Matrice ------------------------------------------------------------------------------
function nouvelleMatrice(taille) {
  return { m: Array.from({length: taille}, () => new Int8Array(taille).fill(-1)), taille };
}
function poserMotifsFixes(M, v) {
  const t = M.taille, g = M.m;
  const finder = (r, c) => {
    for (let i = -1; i <= 7; i++) for (let j = -1; j <= 7; j++) {
      const y = r + i, x = c + j;
      if (y < 0 || x < 0 || y >= t || x >= t) continue;
      const bord = (i >= 0 && i <= 6 && (j === 0 || j === 6)) || (j >= 0 && j <= 6 && (i === 0 || i === 6));
      const coeur = i >= 2 && i <= 4 && j >= 2 && j <= 4;
      g[y][x] = (bord || coeur) ? 1 : 0;
    }
  };
  finder(0, 0); finder(0, t - 7); finder(t - 7, 0);
  for (let i = 8; i < t - 8; i++) { const b = i % 2 === 0 ? 1 : 0; g[6][i] = b; g[i][6] = b; }
  const pos = ALIGN[v];
  for (const r of pos) for (const c of pos) {
    if ((r <= 8 && c <= 8) || (r <= 8 && c >= t - 9) || (r >= t - 9 && c <= 8)) continue;
    for (let i = -2; i <= 2; i++) for (let j = -2; j <= 2; j++)
      g[r + i][c + j] = (Math.abs(i) === 2 || Math.abs(j) === 2 || (i === 0 && j === 0)) ? 1 : 0;
  }
  g[t - 8][8] = 1;                                    // module toujours noir
  // Reserve des zones d'information de format et de version
  for (let i = 0; i < 9; i++) { if (g[8][i] === -1) g[8][i] = 0; if (g[i][8] === -1) g[i][8] = 0; }
  for (let i = 0; i < 8; i++) { if (g[8][t-1-i] === -1) g[8][t-1-i] = 0; if (g[t-1-i][8] === -1) g[t-1-i][8] = 0; }
  if (v >= 7) for (let i = 0; i < 18; i++) {
    const a = Math.floor(i / 3), b = i % 3;
    g[t - 11 + b][a] = 0; g[a][t - 11 + b] = 0;
  }
}
// Copie servant a savoir quels modules sont libres pour les donnees.
function masqueFonction(v, t) {
  const M = nouvelleMatrice(t); poserMotifsFixes(M, v);
  return M.m.map(l => Array.from(l, x => x !== -1));
}
function poserDonnees(M, flux, occupe) {
  const t = M.taille, g = M.m;
  let bit = 0, montant = true;
  const total = flux.length * 8;
  for (let cd = t - 1; cd > 0; cd -= 2) {
    if (cd === 6) cd--;                               // la colonne de timing est sautee
    for (let i = 0; i < t; i++) {
      const y = montant ? t - 1 - i : i;
      for (const x of [cd, cd - 1]) {
        if (occupe[y][x]) continue;
        let b = 0;
        if (bit < total) { b = (flux[bit >> 3] >> (7 - (bit & 7))) & 1; bit++; }
        g[y][x] = b;
      }
    }
    montant = !montant;
  }
}
const MASQUES = [
  (r,c)=>(r+c)%2===0, (r,c)=>r%2===0, (r,c)=>c%3===0, (r,c)=>(r+c)%3===0,
  (r,c)=>(Math.floor(r/2)+Math.floor(c/3))%2===0, (r,c)=>((r*c)%2)+((r*c)%3)===0,
  (r,c)=>(((r*c)%2)+((r*c)%3))%2===0, (r,c)=>(((r+c)%2)+((r*c)%3))%2===0,
];
function penalite(g, t) {
  let p = 0;
  const serie = (get) => {
    for (let a = 0; a < t; a++) {
      let n = 1;
      for (let b = 1; b < t; b++) {
        if (get(a,b) === get(a,b-1)) { n++; if (n === 5) p += 3; else if (n > 5) p++; }
        else n = 1;
      }
    }
  };
  serie((a,b)=>g[a][b]); serie((a,b)=>g[b][a]);
  for (let r = 0; r < t-1; r++) for (let c = 0; c < t-1; c++)
    if (g[r][c] === g[r][c+1] && g[r][c] === g[r+1][c] && g[r][c] === g[r+1][c+1]) p += 3;
  const motifs = [[1,0,1,1,1,0,1,0,0,0,0],[0,0,0,0,1,0,1,1,1,0,1]];
  const cherche = (get) => {
    for (let a = 0; a < t; a++) for (let b = 0; b + 11 <= t; b++)
      for (const mo of motifs) {
        let ok = true;
        for (let k = 0; k < 11; k++) if (get(a,b+k) !== mo[k]) { ok = false; break; }
        if (ok) p += 40;
      }
  };
  cherche((a,b)=>g[a][b]); cherche((a,b)=>g[b][a]);
  let noirs = 0;
  for (let r = 0; r < t; r++) for (let c = 0; c < t; c++) noirs += g[r][c];
  p += Math.floor(Math.abs(noirs * 100 / (t*t) - 50) / 5) * 10;
  return p;
}
const BITS_NIVEAU = { L: 0b01, M: 0b00 };
function infoFormat(niv, masque) {
  const donnees = (BITS_NIVEAU[niv] << 3) | masque;
  let reste = donnees << 10;
  for (let i = 14; i >= 10; i--) if ((reste >> i) & 1) reste ^= 0b10100110111 << (i - 10);
  return ((donnees << 10) | reste) ^ 0b101010000010010;
}
function infoVersion(v) {
  let reste = v << 12;
  for (let i = 17; i >= 12; i--) if ((reste >> i) & 1) reste ^= 0b1111100100101 << (i - 12);
  return (v << 12) | reste;
}

function encoder(texte, niveau) {
  const niv = niveau || 'M';
  const octets = Array.from(new TextEncoder().encode(texte));
  const v = choisirVersion(octets.length, niv);
  if (v < 0) throw new Error('donnees trop longues pour un QR');
  const flux = entrelacer(construireDonnees(octets, v, niv), v, niv);
  const t = 17 + 4 * v;
  const occupe = masqueFonction(v, t);
  let meilleur = null;
  for (let k = 0; k < 8; k++) {
    const M = nouvelleMatrice(t);
    poserMotifsFixes(M, v);
    poserDonnees(M, flux, occupe);
    for (let r = 0; r < t; r++) for (let c = 0; c < t; c++)
      if (!occupe[r][c] && MASQUES[k](r, c)) M.m[r][c] ^= 1;
    const fmt = infoFormat(niv, k);
    for (let i = 0; i < 15; i++) {
      const b = (fmt >> i) & 1;
      if (i < 6) M.m[8][i] = b; else if (i < 8) M.m[8][i + 1] = b;
      else if (i === 8) M.m[7][8] = b; else M.m[14 - i][8] = b;
      // Seconde copie : les bits 0-7 descendent la COLONNE 8 depuis le bas,
      // les bits 8-14 parcourent la LIGNE 8 vers la droite. Les inverser produit
      // un QR dont le format est illisible — c'etait le defaut initial.
      if (i < 7) M.m[t - 1 - i][8] = b; else M.m[8][t - 15 + i] = b;
    }
    M.m[t - 8][8] = 1;
    if (v >= 7) {
      const vi = infoVersion(v);
      for (let i = 0; i < 18; i++) {
        const b = (vi >> i) & 1, a = Math.floor(i / 3), c = i % 3;
        M.m[t - 11 + c][a] = b; M.m[a][t - 11 + c] = b;
      }
    }
    const p = penalite(M.m, t);
    if (!meilleur || p < meilleur.p) meilleur = { p, m: M.m, v, t, masque: k };
  }
  return meilleur;
}

module.exports = { encoder };
