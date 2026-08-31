"""Les deux relevés que ce dépôt lit, et pourquoi ceux-là.

La mécanique du téléchargement et de l'entrepôt vit dans `gvf.osfi`, à un seul endroit pour tout le
portefeuille. Ce module ne dit que le choix des relevés et le nom des vues.

Le **P3** est le compte de résultat consolidé de chaque banque, trimestriel, en **cumul depuis le
début de l'exercice**. Le montant du deuxième trimestre contient celui du premier. Comme ce dépôt
travaille par exercice entier, il lui suffit du quatrième trimestre, où le cumul est l'année : c'est
le seul endroit du portefeuille où le cumul annuel simplifie le travail au lieu de le compliquer.

Le **M4** est le bilan consolidé, mensuel. Il donne l'actif et les capitaux propres, dont le
rendement est le rapport. Il est mensuel, ce qui permet de prendre une moyenne d'année plutôt qu'une
photographie de fin d'exercice, et cela compte : un bilan de banque bouge de plusieurs pour cent d'un
mois à l'autre.

Licence : licence du gouvernement ouvert du Canada, usage et redistribution permis avec attribution.
Rien n'est redistribué ici : les deux fichiers font 979 mégaoctets et `data/` est ignoré.
"""

from __future__ import annotations

from pathlib import Path

from gvf import osfi

RACINE = Path("data/raw")
ENTREPOT = Path("data/osfi.duckdb")

RELEVES = [osfi.BANQUES["p3"], osfi.BANQUES["m4"]]
VUES = {"resultat": "p3", "bilan": "m4"}


def tout_telecharger(racine: Path = RACINE, force: bool = False) -> dict[str, Path]:
    return osfi.tout_telecharger(RELEVES, racine, force)


def construire_entrepot(racine: Path = RACINE, entrepot: Path = ENTREPOT):
    return osfi.construire_entrepot(RELEVES, VUES, racine, entrepot)


def ouvrir(entrepot: Path = ENTREPOT):
    return osfi.ouvrir(entrepot)


def mesurer(co, racine: Path = RACINE) -> dict[str, int]:
    mesures = osfi.mesurer(co, list(VUES))
    # `gvf.osfi` ne compte les institutions que dans la première vue. Les deux relevés n'en portent
    # pas le même nombre, et trois d'entre elles sont les totaux que le portail calcule lui-même :
    # les trois comptes se publient donc séparément plutôt que résumés en un seul.
    for vue in VUES:
        mesures[f"institutions_{vue}"] = co.execute(
            f"SELECT count(DISTINCT institution) FROM {vue}").fetchone()[0]
    mesures["agregats_du_portail"] = co.execute(
        "SELECT count(DISTINCT institution) FROM bilan WHERE institution LIKE '1000%'").fetchone()[0]
    mesures["exercices"] = co.execute("SELECT count(DISTINCT exercice) FROM resultat").fetchone()[0]
    mesures["premier_exercice"] = co.execute("SELECT min(exercice) FROM resultat").fetchone()[0]
    mesures["dernier_exercice"] = co.execute("SELECT max(exercice) FROM resultat").fetchone()[0]
    # la taille des deux fichiers source, mesurée sur le disque : le README l'annonce et elle doit
    # donc se retrouver dans `results/` comme le reste
    for releve in RELEVES:
        chemin = racine / releve.fichier
        if chemin.exists():
            mesures[f"octets_{releve.cle}"] = chemin.stat().st_size
    return mesures
