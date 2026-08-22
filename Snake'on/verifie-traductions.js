/* Contrôle rejouable : aucune clé d'interface ne doit manquer dans une des six langues, et
   aucune clé référencée par le HTML (data-i18n / data-i18n-ph) ou par t() ne doit être absente
   du dictionnaire français, qui sert de repli.

   Usage :  node "Snake'on/verifie-traductions.js" [chemin/vers/index.html]
   Sortie 0 si tout est complet, 1 sinon. Le chemin optionnel sert à jouer le contrôle sur une
   copie sabotée, pour vérifier qu'il sait encore échouer.                                     */
'use strict';
const fs = require('fs');
const path = require('path');

const target = process.argv[2] || path.join(__dirname, 'index.html');
const html = fs.readFileSync(target, 'utf8');

// Le bloc TRANSLATIONS, isolé puis évalué : on lit les vraies clés, pas une approximation
// par expression régulière sur chaque ligne.
const start = html.indexOf('const TRANSLATIONS = {');
const end = html.indexOf('\n};', start);
if (start === -1 || end === -1) { console.error('TRANSLATIONS introuvable'); process.exit(1); }
const body = html.slice(start + 'const TRANSLATIONS = '.length, end + 2);
const TRANSLATIONS = eval('(' + body + ')');

const langs = Object.keys(TRANSLATIONS);
const fr = TRANSLATIONS.fr;
let failures = 0;

// 1. Chaque langue porte exactement les clés du français.
for (const lang of langs) {
    if (lang === 'fr') continue;
    const missing = Object.keys(fr).filter(k => TRANSLATIONS[lang][k] === undefined);
    const extra = Object.keys(TRANSLATIONS[lang]).filter(k => fr[k] === undefined);
    if (missing.length) { console.error(`[${lang}] ${missing.length} clé(s) manquante(s) : ${missing.join(', ')}`); failures++; }
    if (extra.length) { console.error(`[${lang}] ${extra.length} clé(s) orpheline(s) : ${extra.join(', ')}`); failures++; }
}

// 2. Chaque clé citée par le HTML existe côté français.
const used = new Set();
for (const m of html.matchAll(/data-i18n(?:-ph)?="([^"]+)"/g)) used.add(m[1]);
for (const m of html.matchAll(/\bt\('([^']+)'\)/g)) used.add(m[1]);
// Appels INDIRECTS : chercher seulement `t('…')` déclarerait mortes des clés bien vivantes.
// lobbySetStatus() traduit son argument ; cle() choisit entre deux clés selon la victoire.
for (const m of html.matchAll(/lobbySetStatus\('([^']+)'\)/g)) used.add(m[1]);
for (const m of html.matchAll(/\bcle\(g,\s*'([^']+)',\s*'([^']+)'\)/g)) { used.add(m[1]); used.add(m[2]); }
const unknown = Array.from(used).filter(k => fr[k] === undefined);
if (unknown.length) { console.error(`${unknown.length} clé(s) citée(s) mais absente(s) du français : ${unknown.join(', ')}`); failures++; }

// 3. Aucune clé morte : définie mais jamais citée.
const dead = Object.keys(fr).filter(k => !used.has(k));
if (dead.length) { console.error(`${dead.length} clé(s) définie(s) mais jamais utilisée(s) : ${dead.join(', ')}`); failures++; }

if (failures) { console.error(`\nÉCHEC : ${failures} anomalie(s).`); process.exit(1); }
console.log(`OK — ${langs.length} langues, ${Object.keys(fr).length} clés, ${used.size} citées par le HTML.`);
