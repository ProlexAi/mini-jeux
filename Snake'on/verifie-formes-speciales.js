#!/usr/bin/env node
/* Controle rejouable : une forme a teinte imposee doit etre LUE la ou elle est ECRITE.
 *
 * Pourquoi ce controle existe. Les deux formes speciales declarent `fixedColor:true` a
 * l'interieur de leur objet `style`. Trois endroits du code le lisaient a la RACINE du skin
 * (`skin.fixedColor`), ce qui vaut toujours undefined : la teinte identitaire ne s'appliquait
 * pas, et les degrades d'auteur etaient repeints avec la couleur choisie en boutique.
 * Le defaut etait invisible en lecture — les deux orthographes se ressemblent — et aucun test
 * ne le voyait.
 *
 * Ce que le controle verifie :
 *   1. chaque forme qui declare une teinte imposee la declare a UN SEUL endroit connu ;
 *   2. tout code qui lit `fixedColor` le lit au meme endroit que la declaration.
 *
 * Usage :  node "Snake'on/verifie-formes-speciales.js"
 * Sortie :  EXIT=0 si conforme, EXIT=1 sinon.
 */
'use strict';

const fs = require('fs');
const path = require('path');

const SRC = path.join(__dirname, 'index.html');
const code = fs.readFileSync(SRC, 'utf8');

/* --- Extraction du litteral CONFIG.SKINS ---------------------------------------------- */
function extraitTableau(source, cle) {
    const debut = source.indexOf(cle + ': [');
    if (debut === -1) return null;
    let i = source.indexOf('[', debut);
    let profondeur = 0;
    for (let j = i; j < source.length; j++) {
        const c = source[j];
        if (c === '[') profondeur++;
        else if (c === ']') {
            profondeur--;
            if (profondeur === 0) return source.slice(i, j + 1);
        }
    }
    return null;
}

const litteral = extraitTableau(code, 'SKINS');
if (!litteral) {
    console.error('ECHEC : bloc SKINS introuvable dans index.html — controle inapplicable.');
    process.exit(2);
}

let SKINS;
try {
    SKINS = eval('(' + litteral + ')');   // litteral du depot, pas une entree externe
} catch (e) {
    console.error('ECHEC : le bloc SKINS ne s evalue pas (' + e.message + ')');
    process.exit(2);
}

/* --- TEMOIN : l'instrument attrape-t-il bien ce qu'il croit attraper ? ------------------
 * Si l'extraction rendait un tableau vide ou tronque, tous les controles ci-dessous
 * passeraient sans rien avoir examine. On exige donc de retrouver au moins une forme
 * declarant une teinte imposee : c'est le cas dont on connait deja la reponse. */
const imposees = SKINS.filter(s => s.style && s.style.fixedColor);
if (SKINS.length === 0 || imposees.length === 0) {
    console.error(
        `TEMOIN MUET : ${SKINS.length} forme(s) extraite(s), ${imposees.length} a teinte imposee. ` +
        'L instrument ne voit rien a controler — il ne conclut pas.'
    );
    process.exit(2);
}
console.log(`temoin OK : ${SKINS.length} formes extraites, dont ${imposees.length} a teinte imposee`);
console.log();

const anomalies = [];

/* --- 1. La declaration est-elle a un seul endroit ? ------------------------------------ */
for (const s of SKINS) {
    const racine = Object.prototype.hasOwnProperty.call(s, 'fixedColor');
    const dansStyle = !!(s.style && Object.prototype.hasOwnProperty.call(s.style, 'fixedColor'));
    if (racine && dansStyle) {
        anomalies.push(`${s.name} : fixedColor declare DEUX fois (racine et style)`);
    }
    if (dansStyle && !s.color) {
        anomalies.push(`${s.name} : teinte imposee sans propriete \`color\` a lire`);
    }
}

/* --- 2. Le code lit-il fixedColor la ou il est declare ? ------------------------------- */
const lecturesRacine = [];
const re = /(\w+)\.fixedColor/g;
let m;
while ((m = re.exec(code)) !== null) {
    const avant = code.lastIndexOf('\n', m.index);
    const ligne = code.slice(0, m.index).split('\n').length;
    const texte = code.slice(avant + 1, code.indexOf('\n', m.index)).trim();
    if (texte.startsWith('//') || texte.startsWith('*')) continue;   // commentaire : il en PARLE
    if (m[1] === 'style') continue;                                   // lecture correcte
    lecturesRacine.push({ ligne, variable: m[1], texte });
}

const declareDansStyle = imposees.length > 0;
if (declareDansStyle && lecturesRacine.length) {
    for (const l of lecturesRacine) {
        anomalies.push(
            `ligne ${l.ligne} : lit \`${l.variable}.fixedColor\` (toujours undefined) ` +
            `alors que la declaration est dans \`style\` — ${l.texte.slice(0, 72)}`
        );
    }
}

/* --- Verdict --------------------------------------------------------------------------- */
if (anomalies.length === 0) {
    console.log(`OK — ${imposees.length} forme(s) a teinte imposee, lues la ou elles sont declarees.`);
    process.exit(0);
}
console.log(`${anomalies.length} anomalie(s) :`);
for (const a of anomalies) console.log('  - ' + a);
console.log();
console.log(`ECHEC : ${anomalies.length} anomalie(s).`);
process.exit(1);
