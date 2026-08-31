"""La chaîne complète, sur une banque fabriquée dont la réponse se calcule à la main."""

from __future__ import annotations

import datetime as dt

import duckdb
import pytest

from rdb import etudes, postes

BANQUE = "99999"
# des flux trimestriels constants : un quart de l'exercice à chaque trimestre. La ligne 22 du
# formulaire vaut la ligne 14 plus la ligne 21 moins la ligne 15, soit 237,5 par trimestre : c'est
# l'identité que le relevé doit vérifier, et elle est posée ici à la main.
FLUX = {postes.REVENU_INTERET_NET: 150.0, postes.REVENU_HORS_INTERET: 100.0,
        postes.PROVISIONS: 12.5, postes.REVENU_NET_TOTAL: 237.5,
        postes.CHARGES_HORS_INTERET: 137.5,
        postes.IMPOT_EXIGIBLE: 25.0, postes.RESULTAT_NET: 75.0}
# Deux codes du portail portent le même libellé que le revenu hors intérêt sans en être. Ils sont
# posés dans le relevé d'essai avec des valeurs qui ne referment pas l'identité, pour qu'un test
# puisse montrer que le dépôt lit le bon des trois.
HOMONYMES = {"8534": 60.0, "2046": 800.0}
ACTIF = 12_000.0
FONDS_PAR_LIGNE = 100.0            # six lignes de capitaux propres, donc 600 au total


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
            for poste, flux in {**FLUX, **HOMONYMES}.items():
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
                           " ?, ?, ?, ?)",
                           [BANQUE, date, ligne,
                            "liabilities, shareholders' equity, ligne d'essai", FONDS_PAR_LIGNE])
    return co


def test_le_cumul_annuel_est_lu_au_quatrieme_trimestre(entrepot):
    """Le relevé cumule depuis le début de l'exercice : au quatrième trimestre, le cumul EST
    l'exercice. C'est le seul endroit où le cumul annuel simplifie le travail."""
    e = etudes.exercices(entrepot, BANQUE, "Banque d'essai")
    assert [x.exercice for x in e] == [2023, 2024, 2025]
    assert e[0].revenu_brut == pytest.approx(1_000.0)
    assert e[0].resultat_net == pytest.approx(300.0)


def test_les_capitaux_propres_additionnent_les_six_lignes_du_bilan(entrepot):
    e = etudes.exercices(entrepot, BANQUE, "Banque d'essai")[0]
    assert e.capitaux_propres_moyens == pytest.approx(600.0)
    assert e.actif_moyen == pytest.approx(ACTIF)
    assert e.levier == pytest.approx(20.0)


def test_le_revenu_brut_ne_lit_pas_la_ligne_vingt_deux_du_releve(entrepot):
    """Piège du relevé : la ligne 22 est déjà nette des provisions. Le revenu brut est la somme des
    lignes 14 et 21, et prendre la 22 sous-estimerait la productivité de la banque.

    La ligne 22 est réellement dans le relevé d'essai, et le test la relit depuis l'entrepôt plutôt
    que de la recalculer : c'est ce qui distingue ce contrôle d'une soustraction posée à la main.
    """
    ligne_vingt_deux = entrepot.execute(
        "SELECT valeur FROM resultat WHERE institution = ? AND poste = ? AND exercice = 2023"
        " AND trimestre = 4", [BANQUE, postes.REVENU_NET_TOTAL]).fetchone()[0]
    assert ligne_vingt_deux == pytest.approx(950.0)
    e = etudes.exercices(entrepot, BANQUE, "Banque d'essai")[0]
    assert e.revenu_brut == pytest.approx(1_000.0)
    assert e.revenu_brut - e.provisions == pytest.approx(ligne_vingt_deux)


def test_l_identite_du_formulaire_designe_le_code_du_revenu_hors_interet(entrepot, monkeypatch):
    """Trois codes du portail portent le même libellé. L'identité du formulaire en désigne un.

    Ligne 14 plus ligne 21 moins ligne 15 égale ligne 22 : l'égalité se referme avec le code
    retenu et se casse avec chacun des deux homonymes. Sans ce contrôle, échanger le code ne
    casserait rien de visible et déplacerait la productivité de toutes les banques.
    """
    monkeypatch.setattr(postes, "GRANDES_BANQUES", {BANQUE: "Banque d'essai"})
    table = etudes.identite_du_formulaire(entrepot)
    assert len(table) == 3
    assert table["ecart"].abs().max() == pytest.approx(0.0)
    for homonyme in HOMONYMES:
        monkeypatch.setattr(postes, "REVENU_HORS_INTERET", homonyme)
        faux = etudes.identite_du_formulaire(entrepot)
        assert faux["ecart"].abs().max() > 1.0


def test_un_code_de_capitaux_propres_inconnu_est_signale(entrepot):
    """Le relevé change au fil des années. Un code de la branche que ni la liste retenue ni la
    liste écartée ne nomme doit être signalé, et non lu ou ignoré en silence."""
    assert etudes.codes_de_capitaux_propres_non_declares(entrepot) == []
    entrepot.execute("INSERT INTO bilan VALUES (?, 'x', 'y', ?, ?, ?, ?)",
                     [BANQUE, dt.date(2025, 10, 28), "9999",
                      "liabilities, shareholders' equity, ligne inconnue", 5.0])
    assert etudes.codes_de_capitaux_propres_non_declares(entrepot) == ["9999"]


def test_un_exercice_qui_melange_deux_compositions_est_publie(entrepot, monkeypatch):
    """Douze mois ne font pas douze fois les mêmes lignes. Un poste publié une partie de l'année
    seulement sort du dénominateur sans rien dire, et la table de composition le rend visible."""
    monkeypatch.setattr(postes, "GRANDES_BANQUES", {BANQUE: "Banque d'essai"})
    table = etudes.composition_des_capitaux_propres(entrepot)
    assert set(table["compositions_distinctes"]) == {1}
    entrepot.execute("DELETE FROM bilan WHERE poste = ? AND fin_de_mois = ?",
                     [postes.CUMUL_AUTRES_ELEMENTS, dt.date(2025, 10, 28)])
    apres = etudes.composition_des_capitaux_propres(entrepot)
    melange = apres[apres["exercice"] == 2025].iloc[0]
    assert melange["mois"] == 12
    assert melange["compositions_distinctes"] == 2


def test_un_bilan_de_novembre_tombe_dans_l_exercice_suivant(entrepot, monkeypatch):
    """La règle d'exercice s'applique à la moyenne de bilan, pas seulement à une constante. Un
    bilan du 30 novembre 2024 appartient à l'exercice 2025, clos le 31 octobre 2025."""
    assert postes.exercice_du_mois(2024, 11) == 2025
    assert postes.exercice_du_mois(2024, 12) == 2025
    assert postes.exercice_du_mois(2025, 10) == 2025
    monkeypatch.setattr(postes, "GRANDES_BANQUES", {BANQUE: "Banque d'essai"})
    # les douze mois de l'exercice 2025 sont posés dans la fixture : en retirer un de novembre 2024
    # doit faire disparaître l'exercice 2025, et lui seul
    entrepot.execute("DELETE FROM bilan WHERE fin_de_mois = ?", [dt.date(2024, 11, 28)])
    restants = [x.exercice for x in etudes.exercices(entrepot, BANQUE, "Banque d'essai")]
    assert restants == [2023, 2024]


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
