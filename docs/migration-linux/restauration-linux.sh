#!/usr/bin/env bash
#
# ============================================================================
#  RELIRE AVANT DE LANCER. Ce script n'a JAMAIS ete execute.
# ============================================================================
#
#  Il a ete ecrit sur la machine Windows d'origine, ou il ne pouvait pas etre
#  joue : il n'existait pas encore de Kubuntu pour l'accueillir. Son seul
#  controle est un analyseur statique (shellcheck -S warning). Traite-le comme
#  une procedure a valider pas a pas, pas comme un installeur eprouve.
#
#  PERIMETRE : POSTE DE DEVELOPPEMENT personnel sous Kubuntu 26.04 (KDE
#  Plasma 6). Rien ici n'est ecrit pour un serveur. Cette distinction n'est
#  pas decorative : plusieurs consignes ci-dessous S'INVERSENT sur un serveur,
#  et c'est signale a chaque fois par un bloc "PERIMETRE".
#
#  Il est idempotent : le relancer ne casse rien et ne duplique rien.
#
#  Usage :
#      bash restauration-linux.sh            # execute les etapes
#      bash restauration-linux.sh --dry-run  # affiche sans rien faire
#
# ============================================================================

set -euo pipefail

DEPOT_URL="https://github.com/ProlexAi/mini-jeux.git"
DEPOT_DIR="${DEPOT_DIR:-$HOME/mini-jeux}"
BRANCHE="${BRANCHE:-migration-linux}"
DRY_RUN=0

if [ "${1:-}" = "--dry-run" ]; then
    DRY_RUN=1
fi

# --------------------------------------------------------------------------
# Sorties. On prefixe tout : ce script sera lu dans un terminal encombre.
# --------------------------------------------------------------------------
info()  { printf '\033[1;34m[.]\033[0m %s\n' "$*"; }
ok()    { printf '\033[1;32m[+]\033[0m %s\n' "$*"; }
avert() { printf '\033[1;33m[!]\033[0m %s\n' "$*"; }
manuel(){ printf '\033[1;35m[>]\033[0m A FAIRE A LA MAIN : %s\n' "$*"; }

# Execute, ou affiche seulement si --dry-run.
lance() {
    if [ "$DRY_RUN" -eq 1 ]; then
        printf '    (dry-run) %s\n' "$*"
        return 0
    fi
    "$@"
}

# --------------------------------------------------------------------------
# 0. Verifications prealables
# --------------------------------------------------------------------------
info "Verification de l'environnement"

if [ "$(id -u)" -eq 0 ]; then
    avert "Ce script tourne en root. Il est prevu pour un compte utilisateur"
    avert "normal ; sudo est appele explicitement la ou il faut. Arret."
    exit 1
fi

if [ -r /etc/os-release ]; then
    # shellcheck disable=SC1091
    . /etc/os-release
    info "Distribution : ${PRETTY_NAME:-inconnue}"
    case "${ID:-}${ID_LIKE:-}" in
        *ubuntu*|*debian*) : ;;
        *) avert "Distribution non reconnue comme Ubuntu/Debian. Les commandes"
           avert "apt-get ci-dessous ne s'appliqueront probablement pas." ;;
    esac
else
    avert "/etc/os-release illisible : impossible d'identifier la distribution."
fi

# --------------------------------------------------------------------------
# 1. Paquets de base
#
#    Versions candidates MESUREES le 2026-09-05 sur les depots d'Ubuntu 26.04
#    (que Kubuntu partage) : python3 3.14.3, nodejs 22.22.1, git 2.53.0.
#    Le nombre affiche ci-dessous vient de la machine, pas de cette note : un
#    chiffre recopie dans un script perime des que sa source bouge.
#
#    L'option Lock::Timeout evite l'echec brut quand une autre installation
#    tient /var/lib/dpkg/lock-frontend. Un verrou n'est pas un paquet absent.
# --------------------------------------------------------------------------
info "Installation des paquets indispensables"
lance sudo apt-get -o DPkg::Lock::Timeout=120 update
lance sudo apt-get -o DPkg::Lock::Timeout=120 install -y python3 nodejs git gh

if [ "$DRY_RUN" -eq 0 ]; then
    info "Versions reellement installees :"
    python3 --version
    node --version
    git --version
fi
ok "Paquets de base en place"

# --------------------------------------------------------------------------
# 2. Authentification GitHub
#
#    Les identifiants Windows etaient proteges par DPAPI : ils ne sont PAS
#    exportables en clair. C'est une recreation, jamais une copie.
#
#    gh auth login est INTERACTIF (il ouvre un navigateur). Ce script ne le
#    lance donc pas a ta place : il verifie, et te dit quoi taper.
# --------------------------------------------------------------------------
info "Verification de l'authentification GitHub"
if gh auth status >/dev/null 2>&1; then
    ok "gh est deja authentifie"
else
    manuel "gh auth login    puis    gh auth setup-git"
    manuel "Choisir HTTPS et l'authentification par navigateur."
    avert "Sans cela, l'etape suivante echouera sur un depot prive."
fi

# --------------------------------------------------------------------------
# 3. Recuperation du depot
#
#    CLONE FRAIS, jamais une copie brute du dossier .git venu de Windows.
#    Motif mesure : les trois worktrees de C:\JeuRapide\.claude\worktrees\ se
#    referencent par chemins absolus Windows. Un clone frais ne les recree pas
#    du tout, donc rien a reparer. Une copie brute, elle, exigerait un
#    `git worktree prune`.
# --------------------------------------------------------------------------
info "Recuperation du depot dans $DEPOT_DIR"
if [ -d "$DEPOT_DIR/.git" ]; then
    ok "Depot deja present, on se contente de le mettre a jour"
    lance git -C "$DEPOT_DIR" fetch --all --prune
else
    lance git clone "$DEPOT_URL" "$DEPOT_DIR"
fi

if [ "$DRY_RUN" -eq 0 ]; then
    git -C "$DEPOT_DIR" checkout "$BRANCHE"
    info "Branche : $(git -C "$DEPOT_DIR" rev-parse --abbrev-ref HEAD)"
    info "Commit  : $(git -C "$DEPOT_DIR" rev-parse --short HEAD)"
fi
ok "Depot en place"

# --------------------------------------------------------------------------
# 4. CONTROLE : le projet fonctionne-t-il vraiment ?
#
#    C'est l'etape qui donne sa valeur au reste. Elle doit rendre 0.
# --------------------------------------------------------------------------
info "Controle des traductions (doit rendre 0)"
if [ "$DRY_RUN" -eq 0 ]; then
    if ( cd "$DEPOT_DIR" && node "Snake'on/verifie-traductions.js" ); then
        ok "Traductions completes"
    else
        avert "ECHEC du controle de traductions. Ne pas ignorer : ce controle"
        avert "passait au vert sur la machine d'origine le 2026-09-05."
    fi

    info "Controle des chemins (doit rendre 0)"
    if ( cd "$DEPOT_DIR/Snake'on/ia-assets" && python3 verifie-chemins.py ); then
        ok "Chemins portables"
    else
        avert "ECHEC du controle de chemins."
    fi
else
    printf '    (dry-run) node "Snake'"'"'on/verifie-traductions.js"\n'
    printf '    (dry-run) python3 verifie-chemins.py\n'
fi

# --------------------------------------------------------------------------
# 5. CONTROLE : le jeu se sert-il vraiment ?
#
#    On demarre le serveur, on interroge, on l'arrete. Le controle de la
#    MAUVAISE casse est le plus important : sous Linux il doit rendre 404.
#    S'il rendait 200, c'est que le systeme de fichiers est insensible a la
#    casse (montage exotique) et que le test ne prouve rien.
# --------------------------------------------------------------------------
info "Demarrage du serveur local et controle HTTP"
if [ "$DRY_RUN" -eq 0 ]; then
    PORT=8420
    ( cd "$DEPOT_DIR" && python3 -m http.server "$PORT" --directory "Snake'on" ) \
        >/tmp/snakeon-serveur.log 2>&1 &
    SRV_PID=$!
    # Attente active bornee : pas de sleep arbitraire.
    for _ in $(seq 1 40); do
        if curl -sf -o /dev/null "http://127.0.0.1:$PORT/index.html"; then
            break
        fi
        sleep 0.25
    done

    CODE_OK=$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/icons/icon-192.png")
    CODE_CASSE=$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/Icons/Icon-192.png")
    CODE_ABSENT=$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/nexiste-pas.html")

    info "bonne casse   -> HTTP $CODE_OK      (attendu 200)"
    info "mauvaise casse-> HTTP $CODE_CASSE   (attendu 404)"
    info "fichier absent-> HTTP $CODE_ABSENT  (attendu 404, temoin)"

    if [ "$CODE_OK" = "200" ] && [ "$CODE_CASSE" = "404" ] && [ "$CODE_ABSENT" = "404" ]; then
        ok "Le jeu est servi, et la casse est bien discriminante"
    else
        avert "Resultat inattendu. Si la mauvaise casse rend 200, le systeme de"
        avert "fichiers est insensible a la casse et ce controle ne prouve rien."
    fi

    kill "$SRV_PID" 2>/dev/null || true
    wait "$SRV_PID" 2>/dev/null || true
else
    printf '    (dry-run) demarrage http.server puis 3 requetes curl\n'
fi

# --------------------------------------------------------------------------
# 6. OPTIONNEL : pipeline d'assets IA
#
#    N'installe rien tout seul : ces paquets ne servent qu'a ia-assets/, qui
#    n'est PAS necessaire pour faire tourner le jeu (100% procedural, aucun
#    asset bitmap genere n'y est integre).
#
#    ATTENTION, le vrai chantier n'est pas ici : ComfyUI tournait sous
#    DirectML avec une RX 7900 GRE. Sous Linux il faut le RECONSTRUIRE en
#    ROCm -- roues PyTorch differentes, et la contrainte qui figeait ComfyUI
#    sur v0.7.0 disparait avec DirectML. Copier l'ancien dossier ne donnerait
#    qu'une installation morte. Voir la fiche F1 du rapport HTML.
# --------------------------------------------------------------------------
info "Pipeline d'assets IA (optionnel, rien n'est installe automatiquement)"
manuel "Si tu reprends ia-assets/ :  sudo apt-get install -y python3-pil"
manuel "Pour les scripts .ps1, pwsh n'est PAS dans les depots Ubuntu."
manuel "  Voir la fiche F2 du rapport : depot Microsoft, ou reecriture Python."
manuel "Pour ComfyUI : installation ROCm complete, fiche F1. Verification :"
manuel "  python3 -c \"import torch; print(torch.__version__, torch.cuda.is_available())\""

# --------------------------------------------------------------------------
# 7. Memoire Claude Code
#
#    L'identifiant de projet derive du CHEMIN. Le dossier cible n'existe donc
#    qu'apres le premier lancement de Claude Code dans le depot : ce script ne
#    peut pas le deviner, et ne tente pas de le creer.
# --------------------------------------------------------------------------
info "Memoire Claude Code du projet"
if [ -d "$HOME/.claude/projects" ]; then
    info "Identifiants de projet deja presents :"
    ls -1 "$HOME/.claude/projects" 2>/dev/null | sed 's/^/      /' || true
fi
manuel "1. lancer Claude Code une fois dans $DEPOT_DIR"
manuel "2. reperer l'identifiant cree :  ls ~/.claude/projects/"
manuel "3. y copier le dossier memory/ sauvegarde depuis la cle USB"

# --------------------------------------------------------------------------
# 8. Ce que ce script ne peut PAS faire
# --------------------------------------------------------------------------
printf '\n'
info "===================== RESTE A LA MAIN ====================="
manuel "localStorage du jeu : il devait etre exporte AVANT le formatage."
manuel "  Si ca n'a pas ete fait, la progression (niveau 10, 800 XP, meilleure"
manuel "  taille 28864) est perdue : rien ne la synchronise. Pour la remettre :"
manuel "  ouvrir le jeu, DevTools > Application > Local Storage, recoller la"
manuel "  valeur sous la cle neonSnakeUltimate_v1."
printf '\n'
manuel "Secrets : les recuperer depuis la cle USB majBios."
manuel "  PERIMETRE -- consigne valable pour CE POSTE DE DEVELOPPEMENT."
manuel "  Sur un serveur, la regle s'inverse : on ne regenere jamais une cle"
manuel "  qui chiffre des donnees existantes, on reprend la valeur sauvegardee."
manuel "  Ici, rien n'est chiffre en local : regenerer est sans consequence."
printf '\n'
manuel "Cle SSH hermes-vps : verifier si ~/.ssh/id_ed25519 avait ete sauvegarde."
manuel "  Aucune copie n'avait ete trouvee dans les coffres au 2026-09-05."
manuel "  Si elle est perdue : regenerer une paire et mettre a jour"
manuel "  authorized_keys sur le VPS (necessite un acces au VPS)."
printf '\n'
manuel "Skins abandonnes : recuperables si tu les veux un jour --"
manuel "  git checkout sauvegarde/stash-skins-speciaux -- \"Snake'on/index.html\""
info "==========================================================="

printf '\n'
ok "Fin. Relire les lignes [!] et [>] ci-dessus avant de considerer que c'est fait."
