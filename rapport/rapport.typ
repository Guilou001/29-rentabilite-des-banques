#set document(title: "Pourquoi les bénéfices des banques changent-ils ?", author: "Guillaume Vaudescal")
#set page(
  paper: "a4",
  margin: (x: 2.2cm, y: 2.4cm),
  numbering: "1 / 1",
  footer: context [
    #set text(size: 8pt, fill: luma(90))
    #grid(columns: (1fr, auto), align: (left, right),
      [rentabilite-des-banques], [#counter(page).display("1 / 1", both: true)])
  ],
)
#set text(font: ("Helvetica", "Arial", "DejaVu Sans"), size: 10pt, lang: "fr")
#set par(justify: true, leading: 0.68em, spacing: 1.1em)
#set heading(numbering: none)
#show heading.where(level: 2): it => block(above: 1.6em, below: 0.8em, text(size: 13pt, it))
#show heading.where(level: 3): it => block(above: 1.2em, below: 0.6em, text(size: 11pt, it))
#show raw.where(block: true): it => block(
  fill: luma(246), inset: 8pt, radius: 3pt, width: 100%, text(size: 8.5pt, it))
#show raw.where(block: false): it => text(size: 9pt, fill: rgb("#1a3f66"), it)
#show quote.where(block: true): it => block(
  inset: (left: 10pt), stroke: (left: 1.5pt + luma(180)),
  text(style: "italic", fill: luma(45), it.body))
// la table NE DOIT PAS être enfermée dans un par() : Typst 0.15 la supprime alors
// entièrement, sans erreur. Le réglage se pose donc dans la portée du bloc.
#show table: it => block(above: 1.1em, below: 1.1em,
  [#set par(justify: false); #text(size: 8.8pt, it)])
#show figure: it => block(above: 1.4em, below: 1.4em, it)
#show figure.caption: it => text(size: 8.5pt, fill: luma(70), it)
#show link: it => text(fill: rgb("#0072B2"), it)

#align(center)[
  #block(width: 100%)[
    #text(size: 18pt, weight: "bold")[Pourquoi les bénéfices des banques changent-ils ?]
    #v(0.6em)
    #text(size: 10pt, fill: luma(70))[Guillaume Vaudescal · 2026-09-08 · #link("https://github.com/Guilou001/29-rentabilite-des-banques")[Guilou001/29-rentabilite-des-banques]]
  ]
]
#v(1.2em)
#line(length: 100%, stroke: 0.6pt + luma(190))
#v(0.8em)

Une banque peut gagner davantage en gardant une plus grande part de ses revenus, en tirant plus de revenus de ses actifs ou en s'endettant davantage. Ces trois changements n'ont pas le même sens.

Ce projet sépare leurs effets dans les comptes des six grandes banques canadiennes, de 1997 à 2025. Il étudie le bénéfice rapporté aux capitaux propres, c'est-à-dire les fonds comptables des actionnaires. Ce rendement comptable ne mesure ni le dividende versé ni la hausse de l'action.

*En moyenne, les banques gardent une plus grande part de leurs revenus. Pourtant, leur rendement comptable passe de 15,95 % à 12,98 %.*

== Comprendre ce qui fait bouger le total

#figure(image("../results/figures/contributions.png", width: 100%), caption: [Contributions de la marge, de la productivité des actifs et du levier dans les six banques])

Une barre vers la droite ajoute au rendement, une barre vers la gauche en retire. Le losange donne le changement total de chaque banque. Les contributions se compensent en partie.

#table(
  columns: 2,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: left + top,
  inset: 5pt,
    [*Changement entre 1997 et 2025*],
    [*Contribution moyenne au rendement*],
    [Plus de bénéfice conservé par dollar de revenu],
    [+5,67 points de pourcentage],
    [Moins de revenu par dollar d'actif],
    [−4,52 points de pourcentage],
    [Moins d'actif par dollar de capitaux propres],
    [−4,12 points de pourcentage],
    [Ensemble des trois effets],
    [−2,97 points de pourcentage],
)

Chaque banque pèse autant dans cette moyenne. Ce n'est pas le rendement d'un portefeuille d'actions. Les petits écarts d'addition viennent des arrondis. #link("results/tables/contributions.csv")[Contributions par banque].

== Passer des relevés au résultat

Le programme rassemble les comptes publics du BSIF, le régulateur financier fédéral canadien, dans une base DuckDB interrogeable en SQL. Il construit 174 exercices bancaires.

La décomposition de DuPont exprime le rendement comme le produit des trois facteurs du tableau. Le code vérifie cette égalité, le passage des revenus au bénéfice et la cohérence du bilan.

Le détail montre aussi les pièges de lecture des relevés, dont les postes déjà nets de provisions et les changements de classement comptable.

== Ce que la comparaison ne dit pas

La contribution d'un facteur est une décomposition comptable. Elle ne prouve pas qu'une décision précise de la direction a causé le changement.

Les normes comptables et la composition des activités ont changé en vingt-huit ans. Le dénominateur utilisé ici diffère aussi de certaines mesures de rendement publiées par les banques.

L'étude porte sur six établissements canadiens. Elle ne permet pas de prévoir leur rentabilité future.

== Refaire les calculs

#raw("uv sync --locked --all-extras\nuv run pytest\nuv run rdb fetch\nuv run rdb entrepot\nuv run rdb tout", block: true, lang: "bash")

Les commandes de téléchargement accèdent aux sources externes. Les tableaux et figures publiés restent consultables sans lancer les calculs.

== Pour aller plus loin

#link("docs/ETUDE_DETAILLEE.md")[Méthodes, résultats complets et références] · #link("rapport/rapport.pdf")[Présentation en PDF] · #link("CITATION.cff")[Citer le projet] · #link("LICENSE")[Licence].

== English summary

Public filings explain changes in the accounting return on equity of Canada's six major banks from 1997 to 2025. Higher margins are offset by lower asset productivity and leverage. These are accounting contributions, not stock returns or causal effects.
