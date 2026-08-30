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


def mesurer(co) -> dict[str, int]:
    mesures = osfi.mesurer(co, list(VUES))
    mesures["exercices"] = co.execute("SELECT count(DISTINCT exercice) FROM resultat").fetchone()[0]
    mesures["premier_exercice"] = co.execute("SELECT min(exercice) FROM resultat").fetchone()[0]
    mesures["dernier_exercice"] = co.execute("SELECT max(exercice) FROM resultat").fetchone()[0]
    return mesures
