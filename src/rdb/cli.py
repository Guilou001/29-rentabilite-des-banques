"""La ligne de commande : télécharger, construire l'entrepôt, décomposer, dessiner."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from . import donnees, etudes, figures

app = typer.Typer(add_completion=False, help=__doc__)

TABLES = Path("results/tables")
# Les bornes sont posées sur des ruptures visibles dans les données, non sur des dates rondes :
# 2007 est le dernier exercice avant la crise, 2019 le dernier avant la pandémie. La borne de sortie
# de crise n'est pas le creux du rendement : le rendement moyen des six est plus bas en 2008, à
# 9,70 %, qu'en 2009, à 11,08 %. Mais l'exercice 2008 de la Banque Canadienne Impériale de Commerce
# est en perte, à -14,98 %, et `contributions` refuse un rendement négatif. La borne est donc 2009.
PERIODES = [(1997, 2007), (2007, 2009), (2009, 2019), (2019, 2025), (1997, 2025)]


def _ecrire(table, nom: str) -> Path:
    TABLES.mkdir(parents=True, exist_ok=True)
    chemin = TABLES / f"{nom}.csv"
    table.to_csv(chemin, index=False)
    typer.echo(f"  {chemin}  {len(table)} lignes")
    return chemin


@app.command()
def fetch(force: bool = False) -> None:
    """Les deux relevés du BSIF, 979 Mo, depuis le portail du gouvernement ouvert."""
    for cle, chemin in donnees.tout_telecharger(force=force).items():
        typer.echo(f"  {cle}: {chemin} ({chemin.stat().st_size:,} octets)")


@app.command()
def entrepot() -> None:
    """L'entrepôt DuckDB et ses deux vues."""
    co = donnees.construire_entrepot()
    mesures = donnees.mesurer(co)
    for cle, valeur in mesures.items():
        typer.echo(f"  {cle:24} {valeur:>14,}")
    Path("results").mkdir(exist_ok=True)
    Path("results/entrepot.json").write_text(json.dumps(mesures, indent=2), encoding="utf-8")


@app.command()
def identites() -> None:
    """Les quatre identités que les relevés doivent vérifier, comptées plutôt qu'affirmées."""
    co = donnees.ouvrir()
    decompo = etudes.decomposition(co)
    bilan = etudes.identites_du_bilan(co)
    formulaire = etudes.identite_du_formulaire(co)
    non_declares = etudes.codes_de_capitaux_propres_non_declares(co)
    resume = etudes.resume_des_identites(bilan, decompo, formulaire, non_declares)
    for cle, valeur in resume.items():
        typer.echo(f"  {cle:48} {valeur}")
    Path("results").mkdir(exist_ok=True)
    Path("results/identites.json").write_text(json.dumps(resume, indent=2), encoding="utf-8")


@app.command()
def decomposer() -> None:
    """La décomposition de DuPont, exercice par exercice, et ses figures."""
    co = donnees.ouvrir()
    table = etudes.decomposition(co)
    _ecrire(table, "decomposition")
    dernier = table[table["exercice"] == table["exercice"].max()]
    typer.echo(dernier[["nom", "rendement_des_capitaux_propres", "marge", "productivite", "levier",
                        "coefficient_exploitation"]].to_string(index=False))
    _ecrire(etudes.composition_des_capitaux_propres(co), "composition")
    _ecrire(etudes.pieges_de_la_descente(co), "pieges")
    figures.trois_facteurs(table)
    figures.exploitation(table)
    plus_grande = max(etudes.exercices(co, "27997", "Banque Royale du Canada"),
                      key=lambda e: e.exercice)
    figures.descente(plus_grande)


@app.command()
def contributions() -> None:
    """Ce que chaque facteur a apporté au rendement, sur cinq périodes."""
    co = donnees.ouvrir()
    table = etudes.contributions_par_periode(co, PERIODES)
    _ecrire(table, "contributions")
    moyenne = table.groupby(["exercice_depart", "exercice_arrivee"])[
        ["rendement_depart", "rendement_arrivee", "ecart", "points_marge",
         "points_productivite", "points_levier"]].mean()
    typer.echo((100 * moyenne).round(2).to_string())
    longue = table[(table["exercice_depart"] == 1997) & (table["exercice_arrivee"] == 2025)]
    figures.contributions(longue)


@app.command()
def sorties() -> None:
    """Ce qui quitte les bénéfices non répartis autrement que par le résultat de l'exercice."""
    co = donnees.ouvrir()
    table = etudes.sorties_des_benefices_non_repartis(co)
    _ecrire(table, "sorties")
    moyenne = table.groupby("exercice")["part_du_resultat"].mean()
    typer.echo(moyenne.round(3).to_string())
    figures.sorties(table)


@app.command()
def tout() -> None:
    """Tout, dans l'ordre de la démonstration."""
    identites()
    decomposer()
    contributions()
    sorties()


if __name__ == "__main__":      # pragma: no cover
    app()
