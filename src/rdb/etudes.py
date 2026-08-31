"""Les quatre études du dépôt, et les lectures d'entrepôt dont elles se servent."""

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
        # la règle d'exercice vit dans `postes`, à un seul endroit : la réécrire ici la ferait
        # diverger de la liste que les tests gardent
        exercice = postes.exercice_du_mois(date.year, date.month)
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


def identite_du_formulaire(co) -> pd.DataFrame:
    """La ligne 22 du relevé contre la somme des lignes qui la composent, banque par banque.

    Le formulaire P3 pose que le revenu net d'intérêt et hors intérêt, ligne 22, est la ligne 14
    plus la ligne 21 moins la ligne 15. C'est l'identité qui prouve quel code porte le revenu hors
    intérêt : trois codes du portail en portent le libellé, un seul referme l'égalité. Sans ce
    contrôle, échanger le code choisi contre l'un de ses homonymes ne casserait rien de visible et
    déplacerait la productivité de toutes les banques.
    """
    lignes = []
    for bid, nom in postes.GRANDES_BANQUES.items():
        quatorze = _cumul_annuel(co, bid, postes.REVENU_INTERET_NET)
        quinze = _cumul_annuel(co, bid, postes.PROVISIONS)
        vingt_et_un = _cumul_annuel(co, bid, postes.REVENU_HORS_INTERET)
        vingt_deux = _cumul_annuel(co, bid, postes.REVENU_NET_TOTAL)
        for e in sorted(set(quatorze) & set(vingt_et_un) & set(vingt_deux)):
            reconstitue = quatorze[e] + vingt_et_un[e] - quinze.get(e, 0.0)
            lignes.append({"institution": bid, "nom": nom, "exercice": e,
                           "ligne_22_publiee": vingt_deux[e], "ligne_22_reconstituee": reconstitue,
                           "ecart": reconstitue - vingt_deux[e]})
    return pd.DataFrame(lignes)


def codes_de_capitaux_propres_non_declares(co) -> list[str]:
    """Les codes de la branche « capitaux propres » que le dépôt ne retient ni n'écarte par écrit.

    Le relevé change au fil des années : un code apparaît, un autre s'éteint. Ce contrôle compare
    ce que l'entrepôt contient à ce que `postes` déclare, et rend la liste de ce qui manque à
    l'appel. Il a été écrit après avoir trouvé un code de cette branche, le 8635, qu'aucune liste
    ne lisait.
    """
    presents = [ligne[0] for ligne in co.execute(
        "SELECT DISTINCT poste FROM bilan WHERE lower(libelle) LIKE '%shareholder%equity%'"
        " ORDER BY poste").fetchall()]
    connus = set(postes.CAPITAUX_PROPRES) | set(postes.CAPITAUX_PROPRES_ECARTES)
    return [code for code in presents if code not in connus]


def composition_des_capitaux_propres(co) -> pd.DataFrame:
    """Combien de compositions de lignes différentes chaque exercice de bilan mélange.

    La moyenne d'exercice exige douze mois, jamais les mêmes douze lignes. Un poste qui n'est
    publié qu'une partie de l'année sort du dénominateur sans rien dire. Cette table rend la
    rupture visible plutôt que muette : un exercice à deux compositions mélange deux définitions
    des capitaux propres.
    """
    lignes = []
    marques = ", ".join("?" * len(postes.CAPITAUX_PROPRES))
    for bid, nom in postes.GRANDES_BANQUES.items():
        par_mois: dict[dt.date, set[str]] = {}
        for date, poste in co.execute(
                f"""SELECT fin_de_mois, poste FROM bilan
                    WHERE institution = ? AND poste IN ({marques})""",
                [bid, *postes.CAPITAUX_PROPRES]).fetchall():
            par_mois.setdefault(date, set()).add(poste)
        par_exercice: dict[int, list[frozenset[str]]] = {}
        for date, codes in par_mois.items():
            exercice = postes.exercice_du_mois(date.year, date.month)
            par_exercice.setdefault(exercice, []).append(frozenset(codes))
        for exercice, compositions in sorted(par_exercice.items()):
            if len(compositions) != 12:
                continue
            distinctes = set(compositions)
            lignes.append({
                "institution": bid, "nom": nom, "exercice": exercice,
                "mois": len(compositions), "compositions_distinctes": len(distinctes),
                "codes": " ".join(sorted(set().union(*distinctes)))})
    return pd.DataFrame(lignes)


def resume_des_identites(bilan: pd.DataFrame, decompo: pd.DataFrame,
                         formulaire: pd.DataFrame | None = None,
                         codes_non_declares: list[str] | None = None) -> dict:
    """Les nombres qui disent si les relevés se tiennent."""
    agregats = bilan["institution"].str.startswith("1000")
    resume = {
        "observations_de_bilan": int(len(bilan)),
        # les trois pseudo-institutions 1000000, 1000001 et 1000002 sont les totaux que le portail
        # calcule à partir des autres lignes : leur bilan n'est pas une observation indépendante
        "observations_de_bilan_d_institutions": int((~agregats).sum()),
        "observations_de_bilan_d_agregats": int(agregats.sum()),
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
    if formulaire is not None:
        resume["exercices_du_formulaire"] = int(len(formulaire))
        resume["pire_ecart_a_l_identite_du_formulaire_en_milliers"] = float(
            formulaire["ecart"].abs().max())
    if codes_non_declares is not None:
        resume["codes_de_capitaux_propres_non_declares"] = list(codes_non_declares)
    return resume


def pieges_de_la_descente(co) -> pd.DataFrame:
    """Ce que coûterait à la descente l'oubli des postes qu'on oublie.

    La descente du revenu brut au résultat net ne se referme que si l'on retranche aussi trois
    postes faciles à manquer : la part des actionnaires minoritaires, les activités abandonnées et
    les éléments extraordinaires. Cette table publie, exercice par exercice, l'écart qui resterait
    sans eux, pour que les chiffres du README se lisent sans refaire le calcul ni télécharger les
    relevés.
    """
    lignes = []
    for bid, nom in postes.GRANDES_BANQUES.items():
        for e in exercices(co, bid, nom):
            sans_rien = (e.revenu_brut - e.provisions - e.charges_hors_interet - e.impot
                         - e.resultat_net)
            sans_les_deux = sans_rien - e.minoritaires
            lignes.append({
                "institution": bid, "nom": nom, "exercice": e.exercice,
                "revenu_brut": e.revenu_brut,
                "activites_abandonnees": e.activites_abandonnees,
                "elements_extraordinaires": e.elements_extraordinaires,
                "minoritaires": e.minoritaires,
                "ecart_complet": ecart_a_la_cascade(e),
                "ecart_sans_les_deux_lignes_signees": sans_les_deux,
                "ecart_sans_les_deux_lignes_ni_les_minoritaires": sans_rien,
                "part_du_revenu_brut_sans_les_deux_lignes": abs(sans_les_deux) / e.revenu_brut,
                "part_du_revenu_brut_sans_les_trois_postes": abs(sans_rien) / e.revenu_brut})
    return pd.DataFrame(lignes)


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
