"""La chaîne complète, sur une banque fabriquée dont la réponse se calcule à la main."""

from __future__ import annotations

import datetime as dt

import duckdb
import pytest

from rdb import etudes, postes

BANQUE = "99999"
# des flux trimestriels constants : un quart de l'exercice à chaque trimestre
FLUX = {postes.REVENU_INTERET_NET: 150.0, postes.REVENU_HORS_INTERET: 100.0,
        postes.PROVISIONS: 12.5, postes.CHARGES_HORS_INTERET: 137.5,
        postes.IMPOT_EXIGIBLE: 25.0, postes.RESULTAT_NET: 75.0}
ACTIF = 10_000.0
FONDS_PAR_LIGNE = 100.0            # cinq lignes de capitaux propres, donc 500 au total


@pytest.fixture
def entrepot(tmp_path):
    """Trois exercices d'une banque dont l'exercice se clôt le 31 octobre."""
    co = duckdb.connect(str(tmp_path / "essai.duckdb"))
    co.execute("""CREATE TABLE resultat (institution VARCHAR, nom VARCHAR, groupe VARCHAR,
                  exercice INTEGER, trimestre INTEGER, poste VARCHAR, libelle VARCHAR,
                  valeur DOUBLE)""")
    co.execute("""CREATE TABLE bilan (institution VARCHAR, nom VARCHAR, groupe VARCHAR,
                  fin_de_mois DATE, poste VARCHAR, libelle VARCHAR, valeur DOUBLE)""")
    for exercice in (2023, 2024, 2025):
        for trimestre in (1, 2, 3, 4):
            for poste, flux in FLUX.items():
                co.execute("INSERT INTO resultat VALUES (?, 'Banque d''essai', 'Domestic Banks',"
                           " ?, ?, ?, '', ?)",
                           [BANQUE, exercice, trimestre, poste, flux * trimestre])
        # les douze mois de l'exercice : novembre et décembre de l'année précédente, puis janvier
        # à octobre de l'année de l'exercice
        for decalage, mois in postes.MOIS_DE_L_EXERCICE:
            date = dt.date(exercice + decalage, mois, 28)
            co.execute("INSERT INTO bilan VALUES (?, 'Banque d''essai', 'Domestic Banks',"
                       " ?, ?, '', ?)", [BANQUE, date, postes.ACTIF_TOTAL, ACTIF])
            co.execute("INSERT INTO bilan VALUES (?, 'Banque d''essai', 'Domestic Banks',"
                       " ?, ?, '', ?)", [BANQUE, date, postes.PASSIF_ET_CAPITAUX, ACTIF])
            for ligne in postes.CAPITAUX_PROPRES:
                co.execute("INSERT INTO bilan VALUES (?, 'Banque d''essai', 'Domestic Banks',"
                           " ?, ?, '', ?)", [BANQUE, date, ligne, FONDS_PAR_LIGNE])
    return co


def test_le_cumul_annuel_est_lu_au_quatrieme_trimestre(entrepot):
    """Le relevé cumule depuis le début de l'exercice : au quatrième trimestre, le cumul EST
    l'exercice. C'est le seul endroit où le cumul annuel simplifie le travail."""
    e = etudes.exercices(entrepot, BANQUE, "Banque d'essai")
    assert [x.exercice for x in e] == [2023, 2024, 2025]
    assert e[0].revenu_brut == pytest.approx(1_000.0)
    assert e[0].resultat_net == pytest.approx(300.0)


def test_les_capitaux_propres_additionnent_les_cinq_lignes_du_bilan(entrepot):
    e = etudes.exercices(entrepot, BANQUE, "Banque d'essai")[0]
    assert e.capitaux_propres_moyens == pytest.approx(500.0)
    assert e.actif_moyen == pytest.approx(ACTIF)
    assert e.levier == pytest.approx(20.0)


def test_la_part_des_minoritaires_est_hors_des_capitaux_propres_retenus():
    """Le résultat net du relevé est net des minoritaires ; le dénominateur doit l'être aussi.
    Apparier l'un avec des capitaux propres qui contiennent les minoritaires rabaisserait le
    rendement de toutes les banques qui ont des filiales."""
    assert postes.MINORITAIRES_BILAN not in postes.CAPITAUX_PROPRES


def test_un_exercice_incomplet_au_bilan_est_ecarte(entrepot):
    """Onze mois ne font pas une moyenne d'exercice. Prendre la moyenne de ce qui est là ferait
    dépendre le résultat des mois manquants."""
    entrepot.execute("DELETE FROM bilan WHERE fin_de_mois = ?", [dt.date(2025, 10, 28)])
    exercices = [x.exercice for x in etudes.exercices(entrepot, BANQUE, "Banque d'essai")]
    assert 2025 not in exercices
    assert 2024 in exercices


def test_l_identite_du_bilan_se_verifie_ligne_a_ligne(entrepot):
    table = etudes.identites_du_bilan(entrepot)
    assert len(table) == 36
    assert (table["ecart"] == 0).all()


def test_un_bilan_qui_ne_ferme_pas_est_repere(entrepot):
    entrepot.execute("UPDATE bilan SET valeur = valeur + 7 WHERE poste = ? AND fin_de_mois = ?",
                     [postes.ACTIF_TOTAL, dt.date(2025, 10, 28)])
    table = etudes.identites_du_bilan(entrepot)
    assert (table["ecart"] != 0).sum() == 1
    assert table["ecart"].abs().max() == pytest.approx(7.0)


def test_les_deux_codes_de_minoritaires_sont_additionnes(entrepot):
    """L'ancien référentiel comptable canadien et les normes internationales emploient deux codes
    différents, jamais la même année. N'en lire qu'un laisse un trou avant 2012."""
    ancien, recent = postes.PART_MINORITAIRES
    entrepot.execute("INSERT INTO resultat VALUES (?, 'x', 'y', 2025, 4, ?, '', 40.0)",
                     [BANQUE, ancien])
    entrepot.execute("INSERT INTO resultat VALUES (?, 'x', 'y', 2024, 4, ?, '', 40.0)",
                     [BANQUE, recent])
    par_exercice = {x.exercice: x for x in etudes.exercices(entrepot, BANQUE, "Banque d'essai")}
    assert par_exercice[2025].minoritaires == pytest.approx(40.0)
    assert par_exercice[2024].minoritaires == pytest.approx(40.0)
    assert par_exercice[2023].minoritaires == pytest.approx(0.0)


def test_les_sorties_des_benefices_non_repartis_se_calculent(entrepot):
    """La variation des bénéfices non répartis moins le résultat de l'exercice : ce qui manque est
    sorti autrement, par dividende, par rachat d'actions ou par retraitement comptable."""
    for exercice, valeur in ((2023, 1_000.0), (2024, 1_100.0), (2025, 1_150.0)):
        entrepot.execute("INSERT INTO bilan VALUES (?, 'x', 'y', ?, ?, '', ?)",
                         [BANQUE, dt.date(exercice, 10, 31), postes.BENEFICES_NON_REPARTIS, valeur])
    table = etudes.sorties_des_benefices_non_repartis(entrepot, {BANQUE: "Banque d'essai"})
    ligne = table[table["exercice"] == 2024].iloc[0]
    assert ligne["variation"] == pytest.approx(100.0)
    assert ligne["resultat_net"] == pytest.approx(300.0)
    assert ligne["sortie"] == pytest.approx(200.0)
    assert ligne["part_du_resultat"] == pytest.approx(2.0 / 3.0)
