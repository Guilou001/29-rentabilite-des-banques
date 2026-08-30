"""La correspondance des postes : qu'aucun code ne serve deux fois, et que les listes tiennent."""

from __future__ import annotations

from rdb import postes


def test_aucun_poste_du_compte_de_resultat_ne_sert_a_deux_grandeurs():
    """Le même code dans deux grandeurs compterait le même dollar deux fois dans la cascade."""
    codes = [postes.REVENU_INTERET_NET, postes.REVENU_HORS_INTERET, postes.PROVISIONS,
             postes.CHARGES_HORS_INTERET, postes.IMPOT_EXIGIBLE, postes.IMPOT_DIFFERE,
             postes.RESULTAT_NET, postes.ACTIVITES_ABANDONNEES,
             postes.ELEMENTS_EXTRAORDINAIRES, *postes.PART_MINORITAIRES]
    assert len(set(codes)) == len(codes)


def test_les_deux_codes_de_minoritaires_sont_declares():
    """L'un vient de l'ancien référentiel canadien, l'autre des normes internationales."""
    assert len(postes.PART_MINORITAIRES) == 2
    assert len(set(postes.PART_MINORITAIRES)) == 2


def test_les_capitaux_propres_ne_contiennent_pas_de_doublon():
    assert len(set(postes.CAPITAUX_PROPRES)) == len(postes.CAPITAUX_PROPRES)


def test_les_capitaux_propres_ne_contiennent_ni_l_actif_ni_le_total_du_passif():
    """Une erreur de copie qui glisserait l'actif total dans la liste passerait inaperçue au calcul
    tout en divisant le levier par vingt."""
    interdits = {postes.ACTIF_TOTAL, postes.PASSIF_ET_CAPITAUX, postes.MINORITAIRES_BILAN}
    assert set(postes.CAPITAUX_PROPRES) & interdits == set()


def test_l_exercice_compte_douze_mois_et_commence_en_novembre():
    """Un exercice clos le 31 octobre couvre novembre et décembre de l'année précédente, puis
    janvier à octobre. Onze ou treize mois fausseraient toutes les moyennes de bilan."""
    assert len(postes.MOIS_DE_L_EXERCICE) == 12
    assert postes.MOIS_DE_L_EXERCICE[0] == (-1, 11)
    assert postes.MOIS_DE_L_EXERCICE[-1] == (0, 10)
    mois = [m for _, m in postes.MOIS_DE_L_EXERCICE]
    assert len(set(mois)) == 12


def test_les_six_grandes_banques_ont_toutes_un_nom_court():
    assert len(postes.GRANDES_BANQUES) == 6
    for nom in postes.GRANDES_BANQUES.values():
        assert nom in postes.NOMS_COURTS
        assert len(postes.NOMS_COURTS[nom]) <= len(nom)
