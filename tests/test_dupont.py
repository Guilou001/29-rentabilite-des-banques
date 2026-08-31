"""La décomposition, éprouvée sur des nombres choisis pour que le résultat se calcule de tête."""

from __future__ import annotations

import math

import pytest

from rdb.dupont import Exercice, contributions, ecart_a_l_identite, ecart_a_la_cascade


def banque(**remplacements) -> Exercice:
    """Une banque d'essai dont chaque rapport tombe rond.

    Revenu brut 1 000, provisions 50, frais 550, impôt 100, minoritaires 10 : il reste 290. Actif
    40 000, capitaux propres 2 000, donc un levier de 20 et une productivité de 2,5 %.
    """
    valeurs = {"institution": "99999", "nom": "Banque d'essai", "exercice": 2025,
               "revenu_interet_net": 600.0, "revenu_hors_interet": 400.0, "provisions": 50.0,
               "charges_hors_interet": 550.0, "impot": 100.0, "minoritaires": 10.0,
               "activites_abandonnees": 0.0, "elements_extraordinaires": 0.0,
               "resultat_net": 290.0, "actif_moyen": 40_000.0,
               "capitaux_propres_moyens": 2_000.0}
    valeurs.update(remplacements)
    return Exercice(**valeurs)


def test_les_rapports_se_calculent_a_la_main():
    b = banque()
    assert b.revenu_brut == pytest.approx(1_000.0)
    assert b.marge == pytest.approx(0.29)
    assert b.productivite == pytest.approx(0.025)
    assert b.levier == pytest.approx(20.0)
    assert b.rendement_des_capitaux_propres == pytest.approx(0.145)
    assert b.rendement_de_l_actif == pytest.approx(0.00725)
    assert b.coefficient_exploitation == pytest.approx(0.55)
    assert b.taux_de_provisionnement == pytest.approx(0.05)
    assert b.part_interet == pytest.approx(0.60)


def test_l_identite_de_dupont_tient_exactement():
    """Le produit des trois facteurs est le rendement, par construction et non par approximation."""
    for actif in (10_000.0, 40_000.0, 900_000.0):
        for fonds in (500.0, 2_000.0, 60_000.0):
            b = banque(actif_moyen=actif, capitaux_propres_moyens=fonds)
            assert ecart_a_l_identite(b) == pytest.approx(0.0, abs=1e-15)


def test_la_cascade_se_referme():
    assert ecart_a_la_cascade(banque()) == pytest.approx(0.0)


def test_les_activites_abandonnees_entrent_dans_la_cascade():
    """Sans ce terme, la vente d'une filiale laisse un trou. Le signe compte : une cession en perte
    retranche du résultat net, une cession en gain lui ajoute."""
    b = banque(activites_abandonnees=-40.0, resultat_net=250.0)
    assert ecart_a_la_cascade(b) == pytest.approx(0.0)
    faux = banque(activites_abandonnees=0.0, resultat_net=250.0)
    assert ecart_a_la_cascade(faux) == pytest.approx(40.0)


def test_les_elements_extraordinaires_entrent_aussi():
    b = banque(elements_extraordinaires=25.0, resultat_net=315.0)
    assert ecart_a_la_cascade(b) == pytest.approx(0.0)


def test_les_contributions_s_additionnent_a_la_variation_totale():
    """La décomposition logarithmique répartit exactement l'écart, sans résidu."""
    depart = banque(exercice=2000, capitaux_propres_moyens=1_500.0)
    arrivee = banque(exercice=2025, capitaux_propres_moyens=2_500.0)
    c = contributions(depart, arrivee)
    somme = c["points_marge"] + c["points_productivite"] + c["points_levier"]
    assert somme == pytest.approx(c["ecart"], abs=1e-15)
    assert c["part_marge"] + c["part_productivite"] + c["part_levier"] == pytest.approx(1.0)


def test_les_parts_s_envolent_quand_le_rendement_ne_bouge_pas_et_les_points_tiennent():
    """Deux facteurs qui se compensent laissent un rendement presque inchangé. Les parts, qui se
    divisent par la variation du logarithme de ce rendement, partent alors à l'infini.

    Les points, eux, valent la variation du logarithme de chaque facteur multipliée par la moyenne
    logarithmique des deux rendements, quantité finie quand l'écart tend vers zéro. Le test le
    vérifie contre cette formule, calculée à part, et non contre la sortie du code.
    """
    depart = banque()
    arrivee = banque(resultat_net=580.0, capitaux_propres_moyens=4_000.0 * (1 + 1e-9))
    c = contributions(depart, arrivee)
    assert abs(c["variation_logarithmique"]) < 1e-8
    assert abs(c["part_marge"]) > 100.0
    r0, r1 = depart.rendement_des_capitaux_propres, arrivee.rendement_des_capitaux_propres
    moyenne_logarithmique = (r1 - r0) / math.log(r1 / r0)
    for facteur, cle in (("marge", "points_marge"), ("levier", "points_levier")):
        attendu = math.log(getattr(arrivee, facteur) / getattr(depart, facteur))
        assert c[cle] == pytest.approx(attendu * moyenne_logarithmique, rel=1e-9)


def test_un_facteur_seul_a_bouger_porte_toute_la_contribution():
    """Si seul le levier change, la part du levier doit valoir un et les deux autres zéro."""
    depart = banque(capitaux_propres_moyens=2_000.0)
    arrivee = banque(capitaux_propres_moyens=1_600.0)
    c = contributions(depart, arrivee)
    assert c["part_levier"] == pytest.approx(1.0)
    assert c["part_marge"] == pytest.approx(0.0)
    assert c["part_productivite"] == pytest.approx(0.0)
    assert c["ecart"] > 0


def test_la_somme_des_logarithmes_est_le_logarithme_du_rendement():
    """C'est la propriété qui rend la décomposition exacte : le logarithme d'un produit est la somme
    des logarithmes de ses facteurs."""
    b = banque()
    somme = math.log(b.marge) + math.log(b.productivite) + math.log(b.levier)
    assert somme == pytest.approx(math.log(b.rendement_des_capitaux_propres))


def test_un_exercice_en_perte_est_refuse_plutot_que_maquille():
    """Le logarithme d'un rendement négatif n'existe pas. La fonction le dit plutôt que de rendre un
    nombre qui n'aurait pas de sens."""
    perte = banque(resultat_net=-100.0)
    with pytest.raises(ValueError):
        contributions(perte, banque())
    with pytest.raises(ValueError):
        contributions(banque(), perte)
