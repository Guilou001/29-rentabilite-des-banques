# Pourquoi les bénéfices des banques changent-ils ?

Une banque peut gagner davantage en gardant une plus grande part de ses revenus, en tirant plus de revenus de ses actifs ou en s'endettant davantage. Ces trois changements n'ont pas le même sens.

Ce projet sépare leurs effets dans les comptes des six grandes banques canadiennes, de 1997 à 2025. Il étudie le bénéfice rapporté aux capitaux propres, c'est-à-dire les fonds comptables des actionnaires. Ce rendement comptable ne mesure ni le dividende versé ni la hausse de l'action.

**En moyenne, les banques gardent une plus grande part de leurs revenus. Pourtant, leur rendement comptable passe de 15,95 % à 12,98 %.**

## Comprendre ce qui fait bouger le total

![Contributions de la marge, de la productivité des actifs et du levier dans les six banques](results/figures/contributions.png)

Une barre vers la droite ajoute au rendement, une barre vers la gauche en retire. Le losange donne le changement total de chaque banque. Les contributions se compensent en partie.

| Changement entre 1997 et 2025 | Contribution moyenne au rendement |
|---|---:|
| Plus de bénéfice conservé par dollar de revenu | +5,67 points de pourcentage |
| Moins de revenu par dollar d'actif | −4,52 points de pourcentage |
| Moins d'actif par dollar de capitaux propres | −4,12 points de pourcentage |
| Ensemble des trois effets | −2,97 points de pourcentage |

Chaque banque pèse autant dans cette moyenne. Ce n'est pas le rendement d'un portefeuille d'actions. Les petits écarts d'addition viennent des arrondis. [Contributions par banque](results/tables/contributions.csv).

## Passer des relevés au résultat

Le programme rassemble les comptes publics du BSIF, le régulateur financier fédéral canadien, dans une base DuckDB interrogeable en SQL. Il construit 174 exercices bancaires.

La décomposition de DuPont exprime le rendement comme le produit des trois facteurs du tableau. Le code vérifie cette égalité, le passage des revenus au bénéfice et la cohérence du bilan.

Le détail montre aussi les pièges de lecture des relevés, dont les postes déjà nets de provisions et les changements de classement comptable.

## Ce que la comparaison ne dit pas

La contribution d'un facteur est une décomposition comptable. Elle ne prouve pas qu'une décision précise de la direction a causé le changement.

Les normes comptables et la composition des activités ont changé en vingt-huit ans. Le dénominateur utilisé ici diffère aussi de certaines mesures de rendement publiées par les banques.

L'étude porte sur six établissements canadiens. Elle ne permet pas de prévoir leur rentabilité future.

## Refaire les calculs

```bash
uv sync --locked --all-extras
uv run pytest
uv run rdb fetch
uv run rdb entrepot
uv run rdb tout
```

Les commandes de téléchargement accèdent aux sources externes. Les tableaux et figures publiés restent consultables sans lancer les calculs.

## Pour aller plus loin

[Méthodes, résultats complets et références](docs/ETUDE_DETAILLEE.md) · [Présentation en PDF](rapport/rapport.pdf) · [Citer le projet](CITATION.cff) · [Licence](LICENSE).

## English summary

Public filings explain changes in the accounting return on equity of Canada's six major banks from 1997 to 2025. Higher margins are offset by lower asset productivity and leverage. These are accounting contributions, not stock returns or causal effects.
