"""D'où vient le rendement des capitaux propres, décomposé en facteurs qui se multiplient.

**Le problème, en mots simples.** Deux banques rapportent 14 % à leurs actionnaires. La première y
arrive parce qu'elle garde beaucoup de chaque dollar encaissé. La seconde parce qu'elle a emprunté
vingt dollars pour chaque dollar de capitaux propres. Ce n'est pas la même chose : la première tient
dans la durée, la seconde se retourne à la première mauvaise année.

**La décomposition de DuPont**, du nom de l'entreprise chimique qui l'a mise au point dans les années
1910 pour arbitrer entre ses divisions, sépare les deux. Elle écrit le rendement des capitaux propres
comme un produit de trois rapports :

    résultat net     résultat net     revenu brut       actif
    ------------  =  ------------  ×  -----------  ×  ------------
    capitaux propres  revenu brut        actif       capitaux propres

Le premier facteur est la **marge**, ce que la banque garde de chaque dollar encaissé. Le deuxième
est la **productivité de l'actif**, combien de revenu chaque dollar de bilan engendre. Le troisième
est le **levier**, combien de dollars de bilan chaque dollar de capitaux propres porte.

L'égalité est vraie par construction et non par estimation : les dénominateurs s'annulent deux à
deux. C'est ce qui la rend vérifiable à la précision de la machine, et c'est le test qui garde ce
module honnête.

**La marge se déplie à son tour**, et c'est là que se lit le métier bancaire. De chaque dollar de
revenu brut, la banque perd une part en provisions pour créances douteuses, une part en frais de
fonctionnement, une part en impôt. Ce qui reste est la marge. La deuxième de ces parts porte un nom
que tout analyste de banque emploie : le **coefficient d'exploitation**, les frais rapportés au
revenu, et c'est le premier chiffre qu'on regarde pour juger la tenue d'une banque.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Exercice:
    """Un exercice d'une banque : les grandeurs brutes, avant tout rapport."""

    institution: str
    nom: str
    exercice: int
    revenu_interet_net: float
    revenu_hors_interet: float
    provisions: float
    charges_hors_interet: float
    impot: float
    minoritaires: float
    activites_abandonnees: float
    elements_extraordinaires: float
    resultat_net: float
    actif_moyen: float
    capitaux_propres_moyens: float

    @property
    def revenu_brut(self) -> float:
        """Le revenu avant toute charge : intérêt net plus revenus hors intérêt.

        Attention au piège du relevé : la ligne 22 du formulaire, qu'on serait tenté de prendre
        pour le revenu total, est déjà nette des provisions. Le revenu brut est donc la somme des
        lignes 14 et 21, et non la ligne 22.
        """
        return self.revenu_interet_net + self.revenu_hors_interet

    @property
    def marge(self) -> float:
        return self.resultat_net / self.revenu_brut

    @property
    def productivite(self) -> float:
        return self.revenu_brut / self.actif_moyen

    @property
    def levier(self) -> float:
        return self.actif_moyen / self.capitaux_propres_moyens

    @property
    def rendement_des_capitaux_propres(self) -> float:
        """Le rendement calculé directement, sans passer par les trois facteurs."""
        return self.resultat_net / self.capitaux_propres_moyens

    @property
    def rendement_de_l_actif(self) -> float:
        return self.resultat_net / self.actif_moyen

    @property
    def coefficient_exploitation(self) -> float:
        """Les frais de fonctionnement rapportés au revenu brut.

        C'est le chiffre par lequel un analyste commence. Plus il est bas, plus la banque garde de
        ce qu'elle encaisse. Une grande banque canadienne tourne autour de 55 %.
        """
        return self.charges_hors_interet / self.revenu_brut

    @property
    def taux_de_provisionnement(self) -> float:
        return self.provisions / self.revenu_brut

    @property
    def taux_d_imposition(self) -> float:
        return self.impot / self.revenu_brut

    @property
    def part_des_minoritaires(self) -> float:
        return self.minoritaires / self.revenu_brut

    @property
    def part_interet(self) -> float:
        """La part du revenu qui vient de prêter, par opposition à celle qui vient de servir."""
        return self.revenu_interet_net / self.revenu_brut

    def en_ligne(self) -> dict:
        return {
            "institution": self.institution, "nom": self.nom, "exercice": self.exercice,
            "revenu_brut": self.revenu_brut, "resultat_net": self.resultat_net,
            "actif_moyen": self.actif_moyen,
            "capitaux_propres_moyens": self.capitaux_propres_moyens,
            "marge": self.marge, "productivite": self.productivite, "levier": self.levier,
            "rendement_des_capitaux_propres": self.rendement_des_capitaux_propres,
            "rendement_de_l_actif": self.rendement_de_l_actif,
            "coefficient_exploitation": self.coefficient_exploitation,
            "taux_de_provisionnement": self.taux_de_provisionnement,
            "taux_d_imposition": self.taux_d_imposition,
            "part_interet": self.part_interet,
        }


def ecart_a_l_identite(e: Exercice) -> float:
    """De combien le produit des trois facteurs s'écarte du rendement calculé directement.

    L'identité doit tenir exactement, aux erreurs d'arrondi de la machine près. Un écart visible
    signifie qu'un poste a été compté deux fois ou oublié, jamais que la décomposition est
    « approchée ».
    """
    return e.marge * e.productivite * e.levier - e.rendement_des_capitaux_propres


def ecart_a_la_cascade(e: Exercice) -> float:
    """De combien la descente du revenu brut au résultat net ne se referme pas.

    Revenu brut, moins provisions, moins frais, moins impôt, moins part des actionnaires
    minoritaires, plus les activités abandonnées, plus les éléments extraordinaires : le reste doit
    être le résultat net que le relevé publie sur une autre ligne.

    Les deux derniers termes sont signés et loin d'être anecdotiques. Les activités abandonnées
    valent moins 1,8 milliard chez la Banque Royale en 2011, l'exercice où elle a vendu sa banque de
    détail américaine. Les éléments extraordinaires valent plus 309 millions chez la Toronto-Dominion
    en 2008, et une ligne du même ordre chaque année de 2007 à 2011.
    """
    reconstitue = (e.revenu_brut - e.provisions - e.charges_hors_interet - e.impot
                   - e.minoritaires + e.activites_abandonnees + e.elements_extraordinaires)
    return reconstitue - e.resultat_net


def contributions(depart: Exercice, arrivee: Exercice) -> dict:
    """Ce que chaque facteur a apporté à la variation du rendement entre deux exercices.

    **Pourquoi ce n'est pas une simple soustraction.** Les trois facteurs se multiplient, donc leurs
    variations ne s'additionnent pas : une marge qui monte de 10 % et un levier qui baisse de 10 %
    ne s'annulent pas tout à fait. Passer par le logarithme rend l'addition exacte, parce que le
    logarithme d'un produit est la somme des logarithmes.

    On calcule donc la variation du logarithme de chaque facteur, on la rapporte à la variation du
    logarithme du rendement, et on obtient des parts qui font exactement cent pour cent. La
    contribution en points de rendement s'obtient en répartissant l'écart réel selon ces parts.

    La méthode a une limite qui est déclarée : elle exige que les deux rendements soient de même
    signe et non nuls. Une banque qui perd de l'argent une année ne s'y prête pas, et la fonction
    le dit plutôt que de rendre un nombre.

    Deuxième limite, sur les parts et non sur les points. Les parts se divisent par la variation
    du logarithme du rendement, publiée sous le nom `variation_logarithmique`. Quand cette
    variation approche zéro, les parts s'envolent : la Banque Nationale, dont le rendement bouge de
    treize centièmes de point en vingt-huit ans, en porte trois au-delà de mille pour cent. Les
    points, eux, ne bougent pas. Ils valent la variation du logarithme de chaque facteur multipliée
    par la moyenne logarithmique des deux rendements, quantité qui reste finie quand l'écart tend
    vers zéro.
    """
    import math

    r0 = depart.rendement_des_capitaux_propres
    r1 = arrivee.rendement_des_capitaux_propres
    if r0 <= 0 or r1 <= 0:
        raise ValueError("la décomposition logarithmique demande deux rendements strictement "
                         "positifs ; un exercice en perte ne s'y prête pas")
    ecart = r1 - r0
    variations = {
        "marge": math.log(arrivee.marge / depart.marge),
        "productivite": math.log(arrivee.productivite / depart.productivite),
        "levier": math.log(arrivee.levier / depart.levier),
    }
    total = sum(variations.values())
    parts = ({cle: v / total for cle, v in variations.items()} if abs(total) > 1e-15
             else dict.fromkeys(variations, 0.0))
    # le dénominateur des parts est publié avec elles. Quand les deux rendements sont presque
    # égaux, il tend vers zéro et les parts partent à l'infini sans que les points en souffrent :
    # le produit part × écart vaut la variation du logarithme du facteur multipliée par la moyenne
    # logarithmique des rendements. Le lecteur du fichier a besoin de voir ce dénominateur.
    resultat = {"exercice_depart": depart.exercice, "exercice_arrivee": arrivee.exercice,
                "rendement_depart": r0, "rendement_arrivee": r1, "ecart": ecart,
                "variation_logarithmique": total}
    for cle, part in parts.items():
        resultat[f"part_{cle}"] = part
        resultat[f"points_{cle}"] = part * ecart
    return resultat
