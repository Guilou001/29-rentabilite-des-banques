"""Quelle ligne du formulaire porte quel nombre.

Le portail du gouvernement ouvert publie des codes à quatre chiffres, pas des numéros de ligne. Le
BSIF met en ligne le formulaire vierge de chaque relevé, et ce formulaire porte les deux, le numéro
de ligne à gauche et le code à droite. La correspondance ci-dessous en est recopiée, depuis le
formulaire P3 de 2023 et le formulaire M4 de 2021.

Elle n'est pas prise sur parole : `tests/test_identites.py` la confronte aux identités du formulaire
lui-même. Un total doit égaler la somme de ses parties, et si ce n'est pas le cas, c'est qu'un code
est mal attribué. Cette précaution n'est pas théorique : trois codes du compte de résultat portent le
même libellé sur le portail, « revenus non productifs d'intérêt, revenu de négociation », alors que
l'identité prouve qu'un seul des trois est le revenu de négociation.
"""

from __future__ import annotations

# --- Compte de résultat (P3), en cumul depuis le début de l'exercice ----------------------------
REVENU_INTERET_NET = "8408"          # ligne 14
PROVISIONS = "8463"                  # ligne 15, charge pour dépréciation
REVENU_NET_APRES_PROVISIONS = "8464"  # ligne 16
REVENU_HORS_INTERET = "2084"         # ligne 21
REVENU_NET_TOTAL = "8535"            # ligne 22, revenu net d'intérêt et hors intérêt
CHARGES_HORS_INTERET = "1284"        # ligne 26
RESULTAT_AVANT_IMPOT = "1285"        # ligne 27
IMPOT_EXIGIBLE = "1286"              # ligne 28(a)
IMPOT_DIFFERE = "1287"               # ligne 28(b)
RESULTAT_AVANT_MINORITAIRES = "1288"  # ligne 29
# La part des actionnaires minoritaires des filiales porte DEUX codes selon l'époque. Le 1289 est
# celui de l'ancien référentiel comptable canadien, le 1197 celui des normes internationales,
# adoptées par les banques canadiennes à l'exercice 2012. Les deux ne coexistent jamais la même
# année, et n'en retenir qu'un laisse un trou de plusieurs centaines de millions dans les exercices
# antérieurs à 2012.
PART_MINORITAIRES = ["1197", "1289"]
# Les activités abandonnées, nettes d'impôt, signées. Sans cette ligne, la vente par la Banque
# Royale de sa banque de détail américaine en 2011 laisse un trou de 1,9 milliard.
ACTIVITES_ABANDONNEES = "8652"
ELEMENTS_EXTRAORDINAIRES = "1291"
RESULTAT_NET = "1292"                # résultat net attribuable aux détenteurs de capitaux propres

# --- Bilan (M4), à chaque fin de mois -----------------------------------------------------------
ACTIF_TOTAL = "1045"                 # section I, ligne 7
PASSIF_ET_CAPITAUX = "2230"          # section II, total du passif et des capitaux propres
ACTIONS_PRIVILEGIEES = "2355"        # section II, ligne 8(a)
ACTIONS_ORDINAIRES = "2357"          # ligne 8(b)
SURPLUS_APPORTE = "0503"             # ligne 8(c)
BENEFICES_NON_REPARTIS = "2225"      # ligne 8(d)
MINORITAIRES_BILAN = "1202"          # ligne 8(e)
CUMUL_AUTRES_ELEMENTS = "2604"       # ligne 8(f), cumul des autres éléments du résultat global

# Les capitaux propres attribuables aux détenteurs de la banque, c'est-à-dire tout sauf la part des
# actionnaires minoritaires des filiales. C'est le dénominateur qui va avec le poste 1292, lui aussi
# net des minoritaires : apparier un résultat net d'une chose avec des capitaux propres qui la
# contiennent gonflerait le dénominateur et rabaisserait le rendement.
CAPITAUX_PROPRES = [ACTIONS_PRIVILEGIEES, ACTIONS_ORDINAIRES, SURPLUS_APPORTE,
                    BENEFICES_NON_REPARTIS, CUMUL_AUTRES_ELEMENTS]

# Les six banques d'importance systémique nationale. Leur exercice se clôt le 31 octobre, fait publié
# dans chacun de leurs rapports annuels.
GRANDES_BANQUES = {
    "27997": "Banque Royale du Canada",
    "27999": "Banque Toronto-Dominion",
    "28000": "Banque de Nouvelle-Écosse",
    "27998": "Banque de Montréal",
    "27996": "Banque Canadienne Impériale de Commerce",
    "28002": "Banque Nationale du Canada",
}
NOMS_COURTS = {
    "Banque Royale du Canada": "Banque Royale",
    "Banque Toronto-Dominion": "Toronto-Dominion",
    "Banque de Nouvelle-Écosse": "Nouvelle-Écosse",
    "Banque de Montréal": "Banque de Montréal",
    "Banque Canadienne Impériale de Commerce": "Impériale de Commerce",
    "Banque Nationale du Canada": "Banque Nationale",
}

# Les mois de l'exercice d'une banque dont la clôture tombe le 31 octobre : de novembre de l'année
# précédente à octobre de l'année de l'exercice.
MOIS_DE_L_EXERCICE = [(-1, 11), (-1, 12)] + [(0, m) for m in range(1, 11)]
