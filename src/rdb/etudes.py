"""Les cinq études du dépôt, chacune rendant le tableau qu'elle produit."""

from __future__ import annotations

import datetime as dt

import pandas as pd
from gvf import osfi

from . import postes
from .dupont import Exercice, contributions, ecart_a_l_identite, ecart_a_la_cascade


def _cumul_annuel(co, institution: str, poste: str | list[str]) -> dict[int, float]:
    """Un poste du compte de résultat au quatrième trimestre, où le cumul est l'exercice entier.

    Plusieurs codes sont acceptés et additionnés, pour les grandeurs dont le code a changé avec le
    référentiel comptable : ils ne coexistent jamais la même année.
    """
    liste = [poste] if isinstance(poste, str) else poste
    marques = ", ".join("?" * len(liste))
    lignes = co.execute(f"""SELECT exercice, sum(valeur) FROM resultat
                            WHERE institution = ? AND poste IN ({marques}) AND trimestre = 4
                            GROUP BY exercice""", [institution, *liste]).fetchall()
    return dict(lignes)


def _moyenne_annuelle(co, institution: str, poste: str | list[str]) -> dict[int, float]:
    """Un poste du bilan, moyenné sur les douze mois de l'exercice clos le 31 octobre.

    La moyenne, et non la photographie du 31 octobre : le bilan d'une banque bouge de plusieurs pour
    cent d'un mois à l'autre, et un rendement calculé sur une seule date dirait en partie quelle
    date on a choisie. C'est aussi ce que font les banques elles-mêmes quand elles publient leur
    rendement des capitaux propres.
    """
    liste = [poste] if isinstance(poste, str) else poste
    marques = ", ".join("?" * len(liste))
    lignes = co.execute(f"""SELECT fin_de_mois, sum(valeur) FROM bilan
                            WHERE institution = ? AND poste IN ({marques})
                            GROUP BY fin_de_mois""", [institution, *liste]).fetchall()
    par_mois = dict(lignes)
    par_exercice: dict[int, list[float]] = {}
    for date, valeur in par_mois.items():
        # un exercice clos le 31 octobre couvre novembre et décembre de l'année précédente, puis
        # janvier à octobre de l'année qui lui donne son nom
        exercice = date.year + 1 if date.month >= 11 else date.year
        par_exercice.setdefault(exercice, []).append(valeur)
    return {e: sum(v) / len(v) for e, v in par_exercice.items() if len(v) == 12}


def exercices(co, institution: str, nom: str) -> list[Exercice]:
    """Tous les exercices d'une banque pour lesquels les deux relevés sont complets."""
    nii = _cumul_annuel(co, institution, postes.REVENU_INTERET_NET)
    hors = _cumul_annuel(co, institution, postes.REVENU_HORS_INTERET)
    prov = _cumul_annuel(co, institution, postes.PROVISIONS)
    charges = _cumul_annuel(co, institution, postes.CHARGES_HORS_INTERET)
    exigible = _cumul_annuel(co, institution, postes.IMPOT_EXIGIBLE)
    differe = _cumul_annuel(co, institution, postes.IMPOT_DIFFERE)
    minoritaires = _cumul_annuel(co, institution, postes.PART_MINORITAIRES)
    abandonnees = _cumul_annuel(co, institution, postes.ACTIVITES_ABANDONNEES)
    extraordinaires = _cumul_annuel(co, institution, postes.ELEMENTS_EXTRAORDINAIRES)
    net = _cumul_annuel(co, institution, postes.RESULTAT_NET)
    actif = _moyenne_annuelle(co, institution, postes.ACTIF_TOTAL)
    fonds = _moyenne_annuelle(co, institution, postes.CAPITAUX_PROPRES)

    sortie = []
    for e in sorted(set(nii) & set(hors) & set(net) & set(actif) & set(fonds)):
        brut = nii[e] + hors[e]
        if brut <= 0 or actif[e] <= 0 or fonds[e] <= 0:
            continue
        sortie.append(Exercice(
            institution=institution, nom=nom, exercice=e,
            revenu_interet_net=nii[e], revenu_hors_interet=hors[e],
            provisions=prov.get(e, 0.0), charges_hors_interet=charges.get(e, 0.0),
            impot=exigible.get(e, 0.0) + differe.get(e, 0.0),
            minoritaires=minoritaires.get(e, 0.0),
            activites_abandonnees=abandonnees.get(e, 0.0),
            elements_extraordinaires=extraordinaires.get(e, 0.0), resultat_net=net[e],
            actif_moyen=actif[e], capitaux_propres_moyens=fonds[e]))
    return sortie


def decomposition(co) -> pd.DataFrame:
    """La décomposition de DuPont, exercice par exercice, pour les six grandes banques."""
    lignes = []
    for bid, nom in postes.GRANDES_BANQUES.items():
        for e in exercices(co, bid, nom):
            ligne = e.en_ligne()
            ligne["ecart_a_l_identite"] = ecart_a_l_identite(e)
            ligne["ecart_a_la_cascade"] = ecart_a_la_cascade(e)
            lignes.append(ligne)
    return pd.DataFrame(lignes)


def identites_du_bilan(co) -> pd.DataFrame:
    """L'actif total contre le total du passif et des capitaux propres, sur toutes les lignes.

    Le bilan d'une banque doit se refermer : ce qu'elle possède égale ce qu'elle doit plus ce qui
    appartient à ses actionnaires. Le relevé publie les deux totaux séparément, donc l'égalité est
    vérifiable plutôt que supposée. C'est le contrôle de qualité le moins cher et le plus parlant
    sur des données que personne n'a rejouées.
    """
    lignes = co.execute("""
        WITH actif AS (SELECT institution, fin_de_mois, valeur AS a FROM bilan WHERE poste = ?),
             total AS (SELECT institution, fin_de_mois, valeur AS t FROM bilan WHERE poste = ?)
        SELECT actif.institution, actif.fin_de_mois, a, t
        FROM actif JOIN total USING (institution, fin_de_mois)""",
        [postes.ACTIF_TOTAL, postes.PASSIF_ET_CAPITAUX]).fetchall()
    table = pd.DataFrame(lignes, columns=["institution", "fin_de_mois", "actif", "passif_et_fonds"])
    table["ecart"] = table["actif"] - table["passif_et_fonds"]
    return table


def resume_des_identites(bilan: pd.DataFrame, decompo: pd.DataFrame) -> dict:
    """Les quatre nombres qui disent si les relevés se tiennent."""
    return {
        "observations_de_bilan": int(len(bilan)),
        # les relevés sont publiés en milliers de dollars : un écart d'une unité est l'arrondi de
        # publication, pas une erreur, et le compte des fermetures exactes se donne à part
        "bilans_exactement_fermes": int((bilan["ecart"] == 0).sum()),
        "pire_ecart_de_bilan_en_milliers": float(bilan["ecart"].abs().max()),
        "exercices": int(len(decompo)),
        "pire_ecart_a_l_identite": float(decompo["ecart_a_l_identite"].abs().max()),
        "pire_ecart_a_la_cascade": float(decompo["ecart_a_la_cascade"].abs().max()),
        "pire_ecart_a_la_cascade_relatif": float(
            (decompo["ecart_a_la_cascade"].abs() / decompo["revenu_brut"]).max()),
    }


def contributions_par_periode(co, bornes: list[tuple[int, int]]) -> pd.DataFrame:
    """Ce que chaque facteur a apporté au rendement, sur des périodes choisies.

    Les bornes sont des couples d'exercices. Elles sont posées sur des ruptures visibles dans les
    données plutôt que sur des dates rondes.
    """
    lignes = []
    for bid, nom in postes.GRANDES_BANQUES.items():
        par_exercice = {e.exercice: e for e in exercices(co, bid, nom)}
        for depart, arrivee in bornes:
            if depart not in par_exercice or arrivee not in par_exercice:
                continue
            try:
                ligne = contributions(par_exercice[depart], par_exercice[arrivee])
            except ValueError:
                continue
            ligne["institution"], ligne["nom"] = bid, nom
            lignes.append(ligne)
    return pd.DataFrame(lignes)


def sorties_des_benefices_non_repartis(co, banques: dict[str, str] | None = None) -> pd.DataFrame:
    """Ce qui quitte les bénéfices non répartis autrement que par le résultat de l'exercice.

    Le compte de résultat du BSIF ne porte **aucune ligne de dividendes versés**. Ce que la banque
    rend à ses actionnaires ne se lit donc pas directement. Mais les bénéfices non répartis, eux,
    sont au bilan à chaque fin de mois : ce qui y entre est le résultat de l'exercice, et ce qui en
    sort est tout le reste.

    Le résidu se lit avec précaution. Il contient les dividendes, mais aussi les rachats d'actions
    imputés aux bénéfices non répartis et les ajustements de première application d'une norme
    comptable. Ce n'est donc pas un taux de distribution, et le dépôt ne l'appelle pas ainsi.
    """
    lignes = []
    for bid, nom in (banques or postes.GRANDES_BANQUES).items():
        bnr = dict(co.execute("""SELECT fin_de_mois, valeur FROM bilan
                                 WHERE institution = ? AND poste = ?""",
                              [bid, postes.BENEFICES_NON_REPARTIS]).fetchall())
        net = _cumul_annuel(co, bid, postes.RESULTAT_NET)
        for exercice, resultat in sorted(net.items()):
            fin = bnr.get(dt.date(exercice, 10, 31))
            debut = bnr.get(dt.date(exercice - 1, 10, 31))
            if fin is None or debut is None or resultat <= 0:
                continue
            variation = fin - debut
            lignes.append({"institution": bid, "nom": nom, "exercice": exercice,
                           "benefices_non_repartis": fin, "variation": variation,
                           "resultat_net": resultat, "sortie": resultat - variation,
                           "part_du_resultat": (resultat - variation) / resultat})
    return pd.DataFrame(lignes)


def noms_courants(co) -> dict[str, str]:
    return osfi.noms_courants(co, "resultat")
