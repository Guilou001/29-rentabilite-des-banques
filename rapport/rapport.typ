#set document(title: "Les banques canadiennes gagnent mieux leur vie qu'en 1997 et rapportent moins à leurs actionnaires", author: "Guillaume Vaudescal")
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
    #text(size: 18pt, weight: "bold")[Les banques canadiennes gagnent mieux leur vie qu'en 1997 et rapportent moins à leurs actionnaires]
    #v(0.6em)
    #text(size: 10pt, fill: luma(70))[Guillaume Vaudescal · 2026-08-31 · #link("https://github.com/Guilou001/29-rentabilite-des-banques")[Guilou001/29-rentabilite-des-banques]]
  ]
]
#v(1.2em)
#line(length: 100%, stroke: 0.6pt + luma(190))
#v(0.8em)

Une banque qui garde près de vingt-huit cents de chaque dollar encaissé, contre dix-neuf il y a vingt-huit ans, devrait rapporter davantage. Les six grandes banques canadiennes rapportent pourtant trois points de moins qu'en 1997. Ce dépôt sépare les causes, sur les relevés déposés au régulateur.

*Résultat en une phrase.* Sur 174 exercices et six banques de 1997 à 2025, la marge a ajouté *+5,7 points* au rendement des capitaux propres. Deux choses lui en ont retiré *8,6* : chaque dollar de bilan produit moins de revenu qu'avant (*−4,5 points*), et les banques portent un quart de levier en moins (*−4,1 points*). Le rendement moyen passe donc de *15,95 % à 12,98 %*, et l'identité qui le décompose se referme à *2,8 × 10⁻¹⁷*.

_Summary in English. A DuPont decomposition of Canada's six domestic systemically important banks over 174 bank-years, built from OSFI's public P3 income statement and M4 balance sheet returns (1.9 million rows). Return on equity fell from 15.95 % to 12.98 % between fiscal 1997 and 2025. A logarithmic attribution splits the change: margin contributed +5.7 points, asset productivity −4.5 and leverage −4.1. The three-factor identity closes to machine precision, the revenue-to-net- income waterfall to one part in a million, and the balance sheet closes exactly on 19 238 of 19 241 month-ends. A by-product: OSFI's income statement carries no dividend line, so what banks return to shareholders is only visible from retained earnings, where the 2021 fiscal year stands out at 33.8 % of net income, the year fully covered by OSFI's restriction on dividends and buybacks._

== 1. La question posée

*En mots simples.* Deux banques rapportent 14 % à leurs actionnaires. La première y arrive parce qu'elle garde beaucoup de chaque dollar encaissé. La seconde parce qu'elle a emprunté vingt dollars pour chaque dollar de capitaux propres. Ce n'est pas la même chose : la première tient dans la durée, la seconde se retourne à la première mauvaise année.

La *décomposition de DuPont*, du nom de l'entreprise chimique qui l'a mise au point vers 1915 pour arbitrer entre ses divisions, sépare les deux. Elle écrit le rendement des capitaux propres comme un produit de trois rapports.

#quote(block: true)[rendement des capitaux propres = marge × productivité de l'actif × levier]

La *marge* est ce que la banque garde de chaque dollar encaissé. La *productivité de l'actif* est le revenu qu'engendre chaque dollar de bilan. Le *levier* est le nombre de dollars de bilan que porte chaque dollar de capitaux propres. L'égalité est vraie par construction, les dénominateurs s'annulant deux à deux, ce qui la rend vérifiable à la précision de la machine.

La question est alors précise : sur vingt-huit ans, lequel des trois a bougé, et dans quel sens ?

== 2. D'où vient le projet, et ce qu'il apporte

La décomposition de DuPont est enseignée partout et appliquée société par société, le plus souvent sur trois ou cinq ans de comptes publiés. Le BSIF publie autre chose : le relevé réglementaire que chaque banque lui dépose, trimestre par trimestre, depuis 1996. C'est la même information comptable, mais homogène entre les six banques et longue de trente ans, de 1996 à 2026, ce qu'aucun rapport annuel n'offre.

Trois apports.

- *Quatre identités vérifiées* plutôt qu'un résultat affirmé : celle de DuPont, celle qui descend

du revenu brut au résultat net, celle qui referme le bilan, celle du formulaire. La dernière désigne lequel des trois codes homonymes porte le revenu hors intérêt.

- *L'attribution logarithmique de la variation du rendement*, qui répartit l'écart entre les trois

facteurs sans laisser de résidu, sur cinq périodes et six banques.

- *Ce que le compte de résultat du BSIF ne dit pas* : il ne porte aucune ligne de dividendes

versés, et ce que les banques rendent à leurs actionnaires doit donc se lire au bilan.

== 3. Les données

#table(
  columns: 4,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: left + top,
  inset: 5pt,
    [*Relevé*],
    [*Ce qu'il porte*],
    [*Taille*],
    [*Ce qu'on y prend*],
    [P3],
    [compte de résultat consolidé, trimestriel],
    [230 496 088 o],
    [le revenu, les frais, l'impôt, le résultat net],
    [M4],
    [bilan consolidé, mensuel],
    [748 730 698 o],
    [l'actif total et les six lignes de capitaux propres],
)

Une fois chargés, ils font *1 900 048 lignes* et 31 exercices de 1996 à 2026. Le compte de résultat porte 110 déposants et le bilan 112 ; trois d'entre eux sont les agrégats que le portail calcule lui-même, « Total All Banks », « Total Domestic Banks » et « Total Foreign Bank Subsidiaries ». L'étude porte sur les six banques d'importance systémique nationale et sur les exercices complets, soit *174 exercices de 1997 à 2025*. Mesuré le 30 août 2026. Licence du gouvernement ouvert du Canada, usage et redistribution permis avec attribution ; rien n'est redistribué ici.

=== Quatre pièges dans les données, mesurés

Le premier est que *le compte de résultat est en cumul annuel*. C'est le seul endroit du portefeuille où ce cumul simplifie le travail : au quatrième trimestre, le cumul est l'exercice.

Le deuxième est que *la ligne 22 du formulaire n'est pas le revenu brut*. Elle est déjà nette des provisions pour créances douteuses. Le revenu brut est la somme des lignes 14 et 21, et prendre la 22 sous-estimerait la productivité de 6,5 % à 12,5 % selon la banque, au dernier exercice.

Le troisième est que *la part des actionnaires minoritaires porte deux codes*. Le premier vient de l'ancien référentiel comptable canadien, le second des normes internationales, adoptées par les banques canadiennes à l'exercice 2012. Les deux ne coexistent jamais la même année, et n'en lire qu'un laisse un trou de plusieurs centaines de millions avant 2012.

Le quatrième est que *deux lignes signées manquent à la descente si on les oublie*. Les activités abandonnées valent moins 1,8 milliard chez la Banque Royale en 2011, l'exercice où elle a vendu sa banque de détail américaine ; les éléments extraordinaires valent plus 309 millions chez la Toronto-Dominion en 2008. Sans ces deux lignes, la descente laisse un écart de 7,5 % du revenu brut ; sans elles ni la part des minoritaires, de 7,9 % ; avec les trois, de un millionième.

== 4. La méthode, pas à pas

+ *Charger les deux relevés* dans un entrepôt DuckDB, une base analytique qui lit les fichiers sur place plutôt que de les tenir en mémoire.
+ *Lire le compte de résultat au quatrième trimestre*, où le cumul est l'exercice entier.
+ *Moyenner le bilan sur les douze mois de l'exercice*, clos le 31 octobre pour les six banques. La moyenne, et non la photographie du 31 octobre : un bilan de banque bouge de plusieurs pour cent d'un mois à l'autre, et c'est aussi ainsi que les banques calculent leur propre rendement.
+ *Vérifier les quatre identités* avant d'interpréter quoi que ce soit.
+ *Décomposer*, puis attribuer la variation par les logarithmes, ce qui rend l'addition exacte alors que les trois facteurs se multiplient.

== 5. Les résultats

=== 5.1 Les quatre identités tiennent

#table(
  columns: 4,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: left + top,
  inset: 5pt,
    [*Identité*],
    [*Ce qu'elle vérifie*],
    [*Observations*],
    [*Pire écart*],
    [Marge × productivité × levier = rendement],
    [qu'aucun poste n'est compté deux fois],
    [174 exercices],
    [*2,8 × 10⁻¹⁷*],
    [Revenu brut moins charges = résultat net],
    [que la descente est complète],
    [174 exercices],
    [*8 000 \$* sur des milliards],
    [Ligne 14 plus ligne 21 moins ligne 15 = ligne 22],
    [quel code porte le revenu hors intérêt],
    [174 exercices],
    [*5 000 \$*],
    [Actif = passif plus capitaux propres],
    [que le bilan se referme],
    [19 241 fins de mois],
    [*1 000 \$*],
)

Comment lire ce tableau, en trois constats. Le premier est que la première ligne est un contrôle du code et non des données : l'identité de DuPont est vraie par construction, et un écart visible aurait signalé une erreur de programmation. Le deuxième est que les trois autres portent sur les données elles-mêmes, et qu'elles tiennent. Le bilan se referme exactement sur 19 238 des 19 241 fins de mois publiées, dont 1 101 sont les trois agrégats du portail et non des banques. Les trois observations qui restent ferment à mille dollars près, l'unité de publication du relevé. Le troisième est que la troisième ligne tranche entre trois codes homonymes. Le revenu hors intérêt referme le formulaire à 5 000 \$ près avec le code retenu. Il le manque de 8,5 milliards avec le premier de ses deux homonymes, de 30,5 milliards avec le second.

L'écart de 8 000 \$ sur la descente n'a été atteint qu'après avoir trouvé les quatre pièges de la section 3. Avant, il valait 1,9 milliard.

=== 5.2 La marge a gagné, la productivité et le levier ont plus que perdu

Moyenne des six banques ; les deux premières colonnes en pour cent, les quatre suivantes en points de pourcentage de rendement des capitaux propres.

#table(
  columns: 7,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: left + top,
  inset: 5pt,
    [*Période*],
    [*Rendement au départ*],
    [*À l'arrivée*],
    [*Variation*],
    [*dont marge*],
    [*dont productivité*],
    [*dont levier*],
    [1997 à 2007],
    [15,95 %],
    [18,62 %],
    [*+2,67*],
    [+5,37],
    [−2,52],
    [−0,19],
    [2007 à 2009],
    [18,62 %],
    [11,08 %],
    [*−7,54*],
    [−5,51],
    [−0,86],
    [−1,17],
    [2009 à 2019],
    [11,08 %],
    [13,95 %],
    [*+2,87*],
    [+5,92],
    [−0,60],
    [−2,45],
    [2019 à 2025],
    [13,95 %],
    [12,98 %],
    [*−0,97*],
    [−0,30],
    [−0,66],
    [−0,01],
    [*1997 à 2025*],
    [*15,95 %*],
    [*12,98 %*],
    [*−2,97*],
    [*+5,67*],
    [*−4,52*],
    [*−4,12*],
)

Comment lire ce tableau, en trois constats. Le premier est que sur vingt-huit ans la marge a ajouté 5,67 points de rendement, ce qui est considérable. Le rendement a pourtant baissé de 2,97 points : les deux autres facteurs en ont retiré 8,64 à eux deux. Le deuxième est que la crise de 2008 se lit dans la marge et non dans le levier, contrairement à ce qu'on attendrait. Entre 2007 et 2009, le levier n'explique que 1,17 point sur 7,54. Le désendettement des banques canadiennes est venu après la crise et non pendant, et la période suivante le montre, où le levier retire 2,45 points. Le troisième est que les contributions des quatre premières lignes ne s'additionnent pas à celles de la cinquième, alors que la colonne Variation, elle, se télescope exactement. L'attribution est exacte à l'intérieur d'une période, pas entre périodes, et le dépôt publie donc la période longue comme une ligne à part plutôt que comme une somme.

#figure(image("../results/figures/contributions.png", width: 100%), caption: [Ce que chaque facteur a apporté au rendement, de 1997 à 2025])

Comment lire cette figure : trois barres par banque, une par facteur, et un losange pour la variation totale. Une banque dont le losange est à droite de zéro rapporte plus qu'en 1997. Une seule y arrive.

=== 5.3 La Toronto-Dominion est la seule des six à rapporter plus qu'en 1997

#table(
  columns: 7,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: left + top,
  inset: 5pt,
    [*Banque*],
    [*1997*],
    [*2025*],
    [*Variation*],
    [*dont marge*],
    [*dont productivité*],
    [*dont levier*],
    [Toronto-Dominion],
    [15,80 %],
    [*16,76 %*],
    [*+0,96*],
    [+8,30],
    [−3,07],
    [−4,28],
    [Nationale du Canada],
    [12,98 %],
    [12,86 %],
    [−0,13],
    [+8,94],
    [−5,76],
    [−3,31],
    [Royale du Canada],
    [17,13 %],
    [15,25 %],
    [−1,87],
    [+8,48],
    [−4,92],
    [−5,44],
    [Impériale de Commerce],
    [15,95 %],
    [13,67 %],
    [−2,29],
    [+6,80],
    [−4,60],
    [−4,49],
    [de Montréal],
    [15,60 %],
    [10,09 %],
    [−5,50],
    [+3,31],
    [−4,58],
    [−4,22],
    [*de Nouvelle-Écosse*],
    [*18,26 %*],
    [*9,25 %*],
    [*−9,01*],
    [*−1,81*],
    [−4,20],
    [−3,01],
)

Comment lire ce tableau, en trois constats. Le premier est que la Banque de Nouvelle-Écosse est la seule dont la marge a baissé en vingt-huit ans. C'est aussi celle qui perd le plus : elle partait de la meilleure position des six et finit à la dernière place. Le deuxième est que la Banque Nationale a la plus forte progression de marge, +8,94 points, et finit pourtant à plat : sa productivité d'actif a reculé plus que celle de toutes les autres. Le troisième est que la contribution du levier est du même ordre pour les six, de −3,0 à −5,4 points. Les six relèvent du même régulateur et des mêmes exigences de fonds propres, mais rien ici ne mesure la part que ces exigences y prennent.

#figure(image("../results/figures/trois_facteurs.png", width: 100%), caption: [Les trois facteurs, exercice par exercice])

Comment lire cette figure : un cadre par facteur, une ligne par banque. Le creux nommé des deux premiers cadres est l'exercice 2008 de la Banque Canadienne Impériale de Commerce. Son revenu brut est tombé de 12,07 à 3,71 milliards et elle a perdu 2,06 milliards. Sa marge vaut cette année-là moins 55 % et son coefficient d'exploitation 194 %. Le cadre du milieu porte la même étiquette : sa productivité tombe de 3,63 % à 1,08 %. Le cadre de droite montre que le levier ne baisse pas en 2008 mais à partir de 2009.

=== 5.4 De chaque dollar encaissé à la Banque Royale, trente cents restent aux actionnaires

#figure(image("../results/figures/descente.png", width: 100%), caption: [Du revenu brut au résultat net, Banque Royale, exercice 2025])

Comment lire cette figure : la première barre est le revenu brut, ramené à 100. Les trois suivantes retranchent les provisions pour créances douteuses, les frais de fonctionnement et l'impôt. La cinquième réunit la part des actionnaires minoritaires, les activités abandonnées et les éléments extraordinaires, et vaut −0,0 pour cet exercice. La sixième est ce qui reste. Les frais pèsent huit fois plus que les provisions, ce qui explique pourquoi le premier chiffre qu'un analyste de banque regarde est le coefficient d'exploitation.

#table(
  columns: 6,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: left + top,
  inset: 5pt,
    [*Banque*],
    [*Rendement 2025*],
    [*Marge*],
    [*Productivité*],
    [*Levier*],
    [*Coefficient d'exploitation*],
    [Toronto-Dominion],
    [16,76 %],
    [33,1 %],
    [2,99 %],
    [16,9],
    [54,1 %],
    [Royale du Canada],
    [15,25 %],
    [30,6 %],
    [2,83 %],
    [17,6],
    [54,9 %],
    [Impériale de Commerce],
    [13,67 %],
    [28,9 %],
    [2,64 %],
    [17,9],
    [54,4 %],
    [Nationale du Canada],
    [12,86 %],
    [28,7 %],
    [2,57 %],
    [17,4],
    [54,4 %],
    [de Montréal],
    [10,09 %],
    [24,0 %],
    [2,49 %],
    [16,9],
    [58,2 %],
    [de Nouvelle-Écosse],
    [9,25 %],
    [20,6 %],
    [2,60 %],
    [17,2],
    [59,7 %],
)

Comment lire ce tableau, en trois constats. Le premier est que le levier ne sépare plus les six : il va de 16,9 à 17,9, un écart de six pour cent, alors qu'il allait de 21,6 à 24,7 en 1997. Le deuxième est que le classement suit la marge presque exactement, et le coefficient d'exploitation de près : les quatre banques dont les frais absorbent moins de 55 % du revenu sont les quatre premières. Le troisième est que l'écart entre la première et la dernière vaut 7,5 points de rendement, soit davantage que la baisse moyenne du secteur en vingt-huit ans.

#figure(image("../results/figures/exploitation.png", width: 100%), caption: [Le coefficient d'exploitation et le rendement, exercice par exercice])

Comment lire cette figure : à gauche les frais rapportés au revenu brut, à droite le rendement, avec la moyenne des six en trait épais. Le coefficient d'exploitation passe de 63,6 % en 1997 à 55,9 % en 2025, mais l'amélioration n'est pas continue. Il empire d'abord, jusqu'à 69,9 % en 2005, puis 87,3 % dans la crise de 2008. Il ne descend qu'à partir de 2009, et remonte encore à 62,5 % en 2023, plus haut que ses onze exercices précédents. La pointe nommée à 194 % est l'exercice 2008 de la Banque Canadienne Impériale de Commerce, dont les frais ont dépassé le revenu brut effondré.

=== 5.5 Le compte de résultat du BSIF ne porte aucune ligne de dividendes

Ce que les banques rendent à leurs actionnaires ne se lit donc pas directement. Mais les bénéfices non répartis sont au bilan à chaque fin de mois : ce qui y entre est le résultat de l'exercice, ce qui en sort est tout le reste.

#table(
  columns: 2,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: left + top,
  inset: 5pt,
    [*Exercice*],
    [*Part du résultat net qui sort des bénéfices non répartis*],
    [2019],
    [60,4 %],
    [2020],
    [62,7 %],
    [*2021*],
    [*33,8 %*],
    [2022],
    [49,6 %],
    [2025],
    [69,8 %],
    [2012],
    [*123,1 %*],
)

Comment lire ce tableau, en trois constats. Le premier est que l'exercice 2021, qui court de novembre 2020 à octobre 2021, est le plus bas depuis 2005, dont la moyenne ne porte que sur cinq banques. Il tombe entièrement à l'intérieur de la restriction du BSIF. Celui-ci a demandé aux institutions en mars 2020 de ne pas augmenter leurs dividendes ni racheter d'actions, et il a levé cette attente le 4 novembre 2021 (source citée en section 8). Le deuxième est que l'exercice 2012 dépasse cent pour cent. Cela ne veut pas dire que les banques ont distribué plus qu'elles n'ont gagné. C'est l'exercice de première application des normes comptables internationales, dont l'ajustement d'ouverture a été imputé aux bénéfices non répartis. Le troisième est que ce résidu *n'est pas un taux de distribution*, et que le dépôt ne l'appelle pas ainsi. Il mélange les dividendes, les rachats d'actions imputés aux bénéfices non répartis et les retraitements comptables. Rien dans les relevés publics ne permet de les séparer.

#figure(image("../results/figures/sorties.png", width: 100%), caption: [Ce qui quitte les bénéfices non répartis, exercice par exercice])

Comment lire cette figure : une ligne fine par banque, la moyenne des banques en bénéfice en trait épais, la bande colorée marquant les exercices couverts par la restriction du BSIF. Un exercice en perte n'a pas de part du résultat net, si bien que trois années sur vingt-neuf, 2002, 2005 et 2008, ne comptent que cinq banques. Les deux événements qui expliquent le creux de 2021 et le pic de 2012 sont nommés sur la figure, parce que sans eux ces deux points passeraient pour du bruit.

== 6. Reproduire

#raw("uv sync --locked --all-extras\nuv run pytest                 # 32 tests fermés, sans réseau ni gros fichiers\nuv run rdb fetch              # les deux relevés du BSIF, 979 Mo\nuv run rdb entrepot           # l'entrepôt DuckDB, 1 900 048 lignes\nuv run rdb tout               # les six tables et les cinq figures", block: true, lang: "bash")

Les tests tournent sur les formules et sur une banque fabriquée dont chaque rapport tombe rond. Les chiffres des tableaux et des figures viennent des fichiers de #raw("results/"), et chacun a le sien. Deux mesures font exception. Les écarts des deux codes homonymes du revenu hors intérêt et ce que l'omission du code 8635 gonflait en 2005 et 2006 sont écrits dans #raw("src/rdb/postes.py").

- #raw("entrepot.json") : ce que les deux relevés contiennent, jusqu'à la taille des fichiers source.
- #raw("identites.json") : les quatre écarts et les comptes d'observations.
- #raw("tables/decomposition.csv") : les trois facteurs, exercice par exercice.
- #raw("tables/contributions.csv") : l'attribution de la variation, avec son dénominateur.
- #raw("tables/pieges.csv") : ce que coûterait l'oubli des postes qu'on oublie.
- #raw("tables/sorties.csv") : ce qui quitte les bénéfices non répartis.
- #raw("tables/composition.csv") : les lignes de capitaux propres publiées chaque mois.

== 7. Limites, avec leur statut

#table(
  columns: 2,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: left + top,
  inset: 5pt,
    [*Limite*],
    [*Statut*],
    [Le résidu des bénéfices non répartis n'est pas un taux de distribution],
    [déclaré ; il mélange dividendes, rachats et retraitements, que rien dans les relevés publics ne sépare],
    [L'attribution logarithmique exige un rendement positif aux deux bornes],
    [déclaré ; l'exercice 2008 de la Banque Canadienne Impériale de Commerce est en perte et ne s'y prête pas, et la fonction refuse plutôt que de rendre un nombre],
    [Les contributions d'une période ne s'additionnent pas à celles d'une période plus longue],
    [déclaré ; l'attribution est exacte à l'intérieur d'une période, et la période longue est calculée à part],
    [Le bilan est moyenné sur douze mois, pas sur les jours],
    [reconnu ; les banques publient elles-mêmes une moyenne, sans dire laquelle, donc l'écart avec leur propre chiffre n'est pas mesurable],
    [Les capitaux propres retenus excluent la part des actionnaires minoritaires],
    [déclaré ; c'est ce qui les apparie au résultat net du relevé, lui aussi net de cette part],
    [Les changements de référentiel comptable coupent les séries en 2011 et 2012],
    [mesuré ; les deux codes de minoritaires sont additionnés, mais un retraitement d'ouverture reste un retraitement, et l'exercice 2012 le montre],
    [Les six banques seules, pas les banques étrangères ni les petites],
    [déclaré ; l'entrepôt en contient 110 au compte de résultat, et le code s'applique à n'importe laquelle, mais l'exercice ne se clôt pas toutes en octobre],
    [Le cumul des autres éléments du résultat global a changé de code fin 2006],
    [mesuré ; le code 8635, publié de janvier 2005 à octobre 2006, est une composante négative des capitaux propres, et l'omettre les gonflait de 0,7 à 13,6 % sur ces deux exercices ; corrigé le 31 août 2026, et un contrôle signale désormais tout code de cette branche que le dépôt ne nomme ni ne lit],
    [La moyenne de bilan exige douze mois, jamais les mêmes douze lignes],
    [mesuré ; 19 exercices sur 174 mélangent deux compositions, dont les six de 2007, et #raw("results/tables/composition.csv") les publie plutôt que de les taire],
    [Les parts de #raw("tables/contributions.csv") s'envolent quand le rendement ne bouge presque pas],
    [déclaré ; elles se divisent par la variation du logarithme du rendement, publiée dans le même fichier ; les colonnes #raw("points_") en points de rendement, seules citées ici, restent finies],
    [Le contrôle du bilan mêle les banques et les agrégats du portail],
    [mesuré ; sur 19 241 fins de mois, 1 101 appartiennent aux trois totaux que le portail calcule lui-même, et les deux comptes sont publiés séparément dans #raw("results/identites.json")],
    [Le rendement calculé ici n'est pas celui que les banques publient],
    [déclaré ; elles retranchent souvent les dividendes privilégiés et emploient les capitaux propres ordinaires, ce qui donne un nombre plus élevé],
)

== 8. Crédits, licence, citation

Relevés bancaires du portail du gouvernement ouvert du Canada, jeu « Banques » du Bureau du surintendant des institutions financières, sous licence du gouvernement ouvert, avec attribution. Formulaires vierges P3 (2023) et M4 (2021) du BSIF, dont la correspondance entre numéro de ligne et code publié est tirée.

Restriction sur les dividendes et les rachats d'actions : #link("https://www.osfi-bsif.gc.ca/en/news/osfi-announces-measures-support-resilience-financial-institutions")[mesures annoncées par le BSIF en mars 2020] et #link("https://www.osfi-bsif.gc.ca/en/news/statement-superintendent-lifting-expectations-dividends-share-repurchases-executive-compensation")[déclaration du surintendant levant ces attentes le 4 novembre 2021].

Code sous licence MIT, rapport sous licence CC BY 4.0. Figures et chargeur de données produits par #link("https://github.com/Guilou001/gv-fintools")[gv-fintools].

Voisinage dans le portefeuille : #link("https://github.com/Guilou001/28-etats-financiers-reformules")[28-etats-financiers-reformules] fait le même partage entre exploitation et financement sur les entreprises non financières du Canada, où le levier n'ajoute presque rien. Celui-ci le fait sur les banques, dont le levier est le métier. #link("https://github.com/Guilou001/30-risque-operationnel")[30-risque-operationnel] lit les mêmes relevés pour en tirer le capital réglementaire. Le rapport #raw("rapport/rapport.pdf") est engendré depuis ce README.
