# Cahier des charges

#### Groupe 97 *(Asinsa2)*: 
- Fromentel Antoine
- Labory Louis
- Chevalier Quentin
- Xia Xuanxiang
- Michaud William

## Idée de projet
Notre projet serait de créer un jeu d'échec à trois joueurs, avec les pièces "classiques" d'échec mais sur un plateau très particulier.

## Algorithmes
Nous aurons alors deux algorithmes complexes:
- Le premier permettrait de pouvoir calculer les mouvements de chaque pièce sur ce plateau non conventionnel.
- Le deuxième sera un robot capable de jouer de façon non aléatoire contre d'autres joueurs ou robots.
*Il est cependant à noter que dû au peu de temps que nous avons, ainsi que de la nature complexe de ce jeu, ce robot ne sera très probablement pas meilleur qu'un joueur humain.*

## Présentation du jeu d'échec à trois
Le jeu d'échec à trois est une variante crée par George R. Dekle Sr. en 1984. Le plateau utilisé est un plateau hexagonal composé de 96 cases polygonales. 

L'illustration ci-dessous présente le setup initial. Le placement des pièces est conforme au jeu d'échecs traditionnel à la différence près que la reine est placée à la gauche du roi. La règle de la "reine sur sa propre couleur" n'est donc plus applicable, d'autant plus qu'il y a une reine rouge. Les blancs jouent en premier, suivi des noirs puis des rouges.  Cette version des échecs conserve les règles traditionnelles qui ne sont pas affectées par la topologie du platea telles que le roque (déplacement spécial du roi et d'une des tours), la possibilité d'avancer le pion de deux cases pour son premier déplacement et le système de promotion. 

## But du jeu et stratégie
Le vainqueur est celui qui met en position d'échec et mat un des deux rois adverses. Il y aura ainsi un gagnant et deux perdants (même celui qui n'a pas été maté). Ceci permet d'avoir une partie réellement à trois joueurs, plus riches en stratégies tant un joueur qui en domine un autre, le troisième peut intervenir pour contre attaquer ou défendre le joueur en difficulté. Un point stratégique boulversé est l'échange récurrent de pièces de même valeur. En temps normal, cela ne porte rarement préjudice puisque les forces restent équilibrées. Au jeu d'échecs à trois, deux joueurs échangeant leurs places se mettent en position d'infériorité par rapport au troisième qui aura conservé plus de pièces. La notion de double menaces devient beaucoup plus prépondérante ici et permet aux joueurs de changer leurs modes de pensée pour prendre en compte le facteur "troisième joueur"

## Mouvement des différentes pièces
### Déplacement de la tour
Il faut bien retenir pour le mouvement de la tour que la tour doit toujours ressortir d'une case par le côté opposé d'où elle est entrée. Elle ne peut également pas franchir une case occupée par une pièce ou un pion.

### Déplacement du fou
Le fou, contrairement à la tour, traverse les cases en y rentrant par un sommet et en ressortant par le sommet opposé. Chaque case affranchie est de la même couleur que la précédente. Fait intéressant, le fou possède 4 directions différentes au lieu de deux en échec classique à l'exception des cases centrales (I5 - I9 - E9 - E4 - D4 et D5) où il a 5 options. 


