"""Les cinq figures du dépôt. Chacune reçoit un tableau déjà calculé et n'invente aucun nombre."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from gvf.figures import cascade
from gvf.style import GRIS, OKABE_ITO, appliquer, enregistrer, formateur, fr

from .postes import NOMS_COURTS

DOSSIER = Path("results/figures")


def _fin(fig, nom: str, dossier: Path = DOSSIER) -> list[Path]:
    # pas de `tight_layout` : la feuille de style partagée active la mise en page sous contrainte
    chemins = enregistrer(fig, dossier, nom)
    plt.close(fig)
    return chemins


def descente(exercice, dossier: Path = DOSSIER) -> list[Path]:
    """Du revenu brut au résultat net, en pourcentage du revenu brut, pour un exercice.

    La cascade est dessinée en parts du revenu brut plutôt qu'en dollars : c'est ce qui rend deux
    banques de tailles différentes comparables sur le même graphique.
    """
    appliquer()
    brut = exercice.revenu_brut
    etiquettes = ["Revenu brut", "Provisions", "Frais", "Impôt", "Minoritaires\net divers"]
    divers = (exercice.activites_abandonnees + exercice.elements_extraordinaires
              - exercice.minoritaires)
    # la première barre part de zéro et vaut le revenu brut : sans elle, la cascade commence en
    # l'air et le lecteur doit deviner d'où la première soustraction est retranchée
    valeurs = [100.0, -100 * exercice.provisions / brut,
               -100 * exercice.charges_hors_interet / brut,
               -100 * exercice.impot / brut, 100 * divers / brut]
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    cumuls = cascade(ax, etiquettes, valeurs, depart=0.0, total="Résultat net", decimales=1)
    ax.set_xticks(range(len(etiquettes) + 1), etiquettes + ["Résultat net"], fontsize=9)
    ax.set_ylabel("part du revenu brut")
    ax.yaxis.set_major_formatter(formateur(decimales=0, suffixe=" %"))
    ax.set_title(f"{NOMS_COURTS.get(exercice.nom, exercice.nom)}, exercice {exercice.exercice} : "
                 f"{fr(cumuls[-1], 1)} % du revenu brut reste aux actionnaires")
    return _fin(fig, "descente", dossier)


def trois_facteurs(table, dossier: Path = DOSSIER) -> list[Path]:
    """Les trois facteurs de la décomposition, chacun dans son cadre, les six banques ensemble."""
    appliquer()
    fig, axes = plt.subplots(1, 3, figsize=(11.4, 4.4))
    cadres = [("marge", "Marge : le résultat net\nrapporté au revenu brut", 0, " %", 100),
              ("productivite", "Productivité : le revenu brut\nrapporté à l'actif", 1, " %", 100),
              ("levier", "Levier : l'actif rapporté\naux capitaux propres", 2, "", 1)]
    poignees = None
    for colonne, titre, i, suffixe, facteur in cadres:
        ax = axes[i]
        for j, (nom, g) in enumerate(table.groupby("nom", sort=False)):
            g = g.sort_values("exercice")
            ax.plot(g["exercice"], g[colonne], lw=1.5, color=OKABE_ITO[j % len(OKABE_ITO)],
                    label=NOMS_COURTS.get(nom, nom))
        ax.set_title(titre, fontsize=9.5)
        ax.set_xlabel("exercice")
        decimales = 1 if colonne != "levier" else 0
        ax.yaxis.set_major_formatter(formateur(decimales=decimales, suffixe=suffixe,
                                               facteur=facteur))
        poignees = ax.get_legend_handles_labels()
    # le creux de 2008 est nommé plutôt que laissé au lecteur : sans étiquette, il passe pour une
    # anomalie de calcul alors que c'est le plus gros événement de la série
    creux = table.loc[table["marge"].idxmin()]
    for ax, colonne in ((axes[0], "marge"), (axes[1], "productivite")):
        ax.annotate(f"{NOMS_COURTS.get(creux['nom'], creux['nom'])} {int(creux['exercice'])}",
                    (creux["exercice"], creux[colonne]), textcoords="offset points",
                    xytext=(8, 6), fontsize=7.4, color=GRIS)
    fig.legend(*poignees, fontsize=8, ncols=6, frameon=False, loc="lower center",
               bbox_to_anchor=(0.5, -0.06))
    return _fin(fig, "trois_facteurs", dossier)


def contributions(table, dossier: Path = DOSSIER) -> list[Path]:
    """Ce que chaque facteur a apporté au rendement entre deux exercices, banque par banque."""
    appliquer()
    t = table.sort_values("ecart")
    fig, ax = plt.subplots(figsize=(9.0, 4.8))
    y = np.arange(len(t))
    hauteur = 0.26
    series = [("points_marge", "Marge", 0), ("points_productivite", "Productivité", 1),
              ("points_levier", "Levier", 2)]
    for colonne, etiquette, i in series:
        ax.barh(y + (i - 1) * hauteur, 100 * t[colonne], height=hauteur,
                color=OKABE_ITO[i], label=etiquette)
    ax.plot(100 * t["ecart"], y, "D", ms=6, color=GRIS, label="Variation totale")
    ax.axvline(0, color=GRIS, lw=1.0)
    ax.set_yticks(y, [f"{NOMS_COURTS.get(n, n)}\n{fr(100 * d, 1)} % → {fr(100 * a, 1)} %"
                      for n, d, a in zip(t["nom"], t["rendement_depart"], t["rendement_arrivee"],
                                         strict=True)], fontsize=8)
    ax.set_xlabel("contribution au rendement des capitaux propres, en points de pourcentage")
    # des graduations entières : arrondir à l'unité des graduations que matplotlib pose à la
    # demie afficherait « 2 » là où le trait vaut 2,5
    limite = int(np.ceil(100 * max(t[c].abs().max() for c, _, _ in series)))
    ax.set_xticks(range(-limite, limite + 1, 2))
    ax.xaxis.set_major_formatter(formateur(decimales=0))
    ax.legend(fontsize=8, ncols=4, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.01))
    return _fin(fig, "contributions", dossier)


def exploitation(table, dossier: Path = DOSSIER) -> list[Path]:
    """Le coefficient d'exploitation et le rendement, dans le temps."""
    appliquer()
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.6))
    poignees = None
    for colonne, ax, titre, etiquette in (
            ("coefficient_exploitation", axes[0], "Les frais rapportés au revenu brut",
             "coefficient d'exploitation"),
            ("rendement_des_capitaux_propres", axes[1], "Le rendement des capitaux propres",
             "rendement")):
        for j, (nom, g) in enumerate(table.groupby("nom", sort=False)):
            g = g.sort_values("exercice")
            ax.plot(g["exercice"], g[colonne], lw=1.5, color=OKABE_ITO[j % len(OKABE_ITO)],
                    label=NOMS_COURTS.get(nom, nom))
        moyenne = table.groupby("exercice")[colonne].mean()
        ax.plot(moyenne.index, moyenne.to_numpy(), lw=2.6, color=GRIS, ls="--",
                label="Moyenne des six")
        ax.set_title(titre, fontsize=10)
        ax.set_xlabel("exercice")
        ax.set_ylabel(etiquette)
        ax.yaxis.set_major_formatter(formateur(decimales=0, suffixe=" %", facteur=100))
        poignees = ax.get_legend_handles_labels()
    # l'exercice 2008 est nommé plutôt que laissé au lecteur : un coefficient d'exploitation de
    # 194 % passe pour une erreur de calcul si rien ne dit d'où il vient
    pointe = table.loc[table["coefficient_exploitation"].idxmax()]
    axes[0].annotate(f"{NOMS_COURTS.get(pointe['nom'], pointe['nom'])} {int(pointe['exercice'])}",
                     (pointe["exercice"], pointe["coefficient_exploitation"]),
                     textcoords="offset points", xytext=(10, -2), fontsize=7.6, color=GRIS)
    fig.legend(*poignees, fontsize=8, ncols=4, frameon=False, loc="lower center",
               bbox_to_anchor=(0.5, -0.08))
    return _fin(fig, "exploitation", dossier)


def sorties(table, dossier: Path = DOSSIER) -> list[Path]:
    """Ce qui quitte les bénéfices non répartis autrement que par le résultat, exercice par
    exercice, et le creux de l'exercice sous restriction."""
    appliquer()
    fig, ax = plt.subplots(figsize=(9.4, 4.6))
    for j, (nom, g) in enumerate(table.groupby("nom", sort=False)):
        g = g.sort_values("exercice")
        ax.plot(g["exercice"], g["part_du_resultat"], lw=1.2, alpha=0.55,
                color=OKABE_ITO[j % len(OKABE_ITO)], label=NOMS_COURTS.get(nom, nom))
    # la moyenne ne porte que sur les banques en bénéfice : un exercice en perte n'a pas de part du
    # résultat net. Trois exercices sur vingt-neuf n'en comptent donc que cinq, et l'étiquette le
    # dit plutôt que de laisser croire à une population constante.
    moyenne = table.groupby("exercice")["part_du_resultat"].mean()
    ax.plot(moyenne.index, moyenne.to_numpy(), lw=2.8, color=GRIS,
            label="Moyenne des banques en bénéfice")
    ax.axhline(1.0, color=GRIS, lw=0.9, ls="--")
    # l'exercice 2021 d'une banque canadienne court de novembre 2020 à octobre 2021, donc
    # entièrement à l'intérieur de la restriction du BSIF, levée le 4 novembre 2021
    ax.axvspan(2019.6, 2021.4, color=OKABE_ITO[3], alpha=0.13)
    haut = ax.get_ylim()[1]
    ax.annotate("Restriction du BSIF sur\nles dividendes et les rachats",
                (2020.5, haut), textcoords="offset points", xytext=(0, -30),
                ha="center", fontsize=7.8, color=GRIS)
    ax.annotate("Première application\ndes normes internationales",
                (2012, haut), textcoords="offset points", xytext=(-4, -30),
                ha="right", fontsize=7.8, color=GRIS)
    ax.set_xlabel("exercice")
    ax.set_ylabel("part du résultat net qui sort\ndes bénéfices non répartis")
    ax.yaxis.set_major_formatter(formateur(decimales=0, suffixe=" %", facteur=100))
    ax.legend(fontsize=7.6, ncols=4, frameon=False, loc="lower center", bbox_to_anchor=(0.5, -0.42))
    return _fin(fig, "sorties", dossier)
