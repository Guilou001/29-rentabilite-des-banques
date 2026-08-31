"""Quelle ligne du formulaire porte quel nombre.

Le portail du gouvernement ouvert publie des codes à quatre chiffres, pas des numéros de ligne. Le
BSIF met en ligne le formulaire vierge de chaque relevé, et ce formulaire porte les deux, le numéro
de ligne à gauche et le code à droite. La correspondance ci-dessous en est recopiée, depuis le
formulaire P3 de 2023 et le formulaire M4 de 2021.

Elle n'est pas prise sur parole. L'identité du formulaire, ligne 14 plus ligne 21 moins ligne 15
égale ligne 22, est vérifiée sur les données réelles par `rdb identites` et sur un relevé fabriqué
par `tests/test_etudes.py`. Un total doit égaler la somme de ses parties, et si ce n'est pas le cas,
c'est qu'un code est mal attribué. Cette précaution n'est pas théorique : trois codes du compte de
résultat portent le même libellé sur le portail, « revenus non productifs d'intérêt, revenu de
négociation ». Mesuré sur les 174 exercices, l'identité tient à 5 000 $ près avec le code 2084.
Le pire écart monte à 8,5 milliards avec le 8534, à 30,5 milliards avec le 2046.
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
# Royale de sa banque de détail américaine en 2011 laisse un trou de 1,8 milliard. Avec la part des
# minoritaires oubliée en plus, le trou du même exercice monte à 1,9 milliard.
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
# Le même cumul portait un autre code avant que la ligne ne prenne son nom actuel. Le 8635 n'est
# publié que du 31 janvier 2005 au 31 octobre 2006, et le 2604 prend le relais le 31 janvier 2007.
# Le portail l'étiquette « shareholders' equity, total », étiquette fausse : la valeur est négative
# et cent fois trop petite pour un total. Ce que les données tranchent, c'est la continuité. Sans le
# 8635, les capitaux propres de la Banque Royale sautent de 18,12 à 20,38 milliards entre décembre
# 2004 et janvier 2005, le mois où le code apparaît ; avec lui, ils passent de 18,12 à 18,95. Même
# saut sur les cinq autres banques, et il disparaît de la même façon. Le code est donc une
# composante des capitaux propres, et l'omettre les gonfle de 0,7 à 13,6 % sur les exercices 2005
# et 2006.
CUMUL_AUTRES_ELEMENTS_ANCIEN = "8635"

# Les capitaux propres attribuables aux détenteurs de la banque, c'est-à-dire tout sauf la part des
# actionnaires minoritaires des filiales. C'est le dénominateur qui va avec le poste 1292, lui aussi
# net des minoritaires : apparier un résultat net d'une chose avec des capitaux propres qui la
# contiennent gonflerait le dénominateur et rabaisserait le rendement.
CAPITAUX_PROPRES = [ACTIONS_PRIVILEGIEES, ACTIONS_ORDINAIRES, SURPLUS_APPORTE,
                    BENEFICES_NON_REPARTIS, CUMUL_AUTRES_ELEMENTS,
                    CUMUL_AUTRES_ELEMENTS_ANCIEN]

# La branche « capitaux propres » du relevé porte d'autres codes, écartés chacun pour une raison
# nommée. La liste sert de garde-fou : `rdb identites` compare les codes que l'entrepôt contient
# dans cette branche à la somme des deux listes, et signale tout code qui n'apparaît ni dans l'une
# ni dans l'autre. Un code de plus au relevé cesse ainsi de passer inaperçu.
CAPITAUX_PROPRES_ECARTES = {
    "1202": "part des actionnaires minoritaires, normes internationales",
    "1201": "la même part, colonne des devises étrangères seulement",
    "0653": "actions privilégiées, colonne des devises étrangères seulement",
    "0654": "actions ordinaires, colonne des devises étrangères seulement",
    "0655": "surplus d'apport, colonne des devises étrangères seulement",
    "0657": "total du passif et des capitaux propres, devises étrangères",
    "0885": "total des capitaux propres, colonne des devises étrangères",
    "2230": "total du passif et des capitaux propres, qui n'est pas une composante",
}

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
# Le décalage d'année à appliquer à un bilan selon son mois. Il est déduit de la liste ci-dessus et
# non réécrit à la main : une règle d'exercice qui vivrait à deux endroits pourrait diverger, et le
# test qui garde la liste ne verrait rien.
_DECALAGE_PAR_MOIS = {mois: -decalage for decalage, mois in MOIS_DE_L_EXERCICE}


def exercice_du_mois(annee: int, mois: int) -> int:
    """L'exercice auquel appartient une fin de mois, pour une clôture au 31 octobre.

    Novembre et décembre appartiennent à l'exercice qui porte le nom de l'année suivante ; janvier
    à octobre à celui qui porte le nom de leur propre année.
    """
    return annee + _DECALAGE_PAR_MOIS[mois]
