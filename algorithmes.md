Algorithmes non triviaux utilisés:

Implémentation d'un robot pouvant jouer aux echecs:

Nous avons adapté Stockfish, le moteur d'échec open-source le plus puissant au monde.
D'après Wikipédia:
Il a gagné tous les évenements principaux du TCEC (Top Chess Engine Championship) ainsi que le CCC (Computer Chess Championship de Chess.com) depuis 2020.
Son score ELO est estimé à environ 3634.

Utilise des réseaux de neurones. (deep learning etc)

Mais on a bossé quand même pcq il n'est absolument pas adapté aux échecs à trois joueurs.
Donc on interagit avec jusqu'à 9 instances de Stockfish en même temps, et on utilise une IA pour combiner les résultats qu'il nous renvoie et en déduire le meilleur coup à jouer.

___ Mtn qu'on a fini de flex: ___

Raytracing:
Un algorithme qui est devenu très populaire depuis la sortie des cartes graphiques RTX, il permet de compter le nombre d'intersections entre un rayon imaginaire et des ensembles de polygones. 
Nous utilisons cette algorithme pour autre chose par contre:
Lors d'un clic de la souris, on lance un laser depuis les coordonnees du clic qui se deplace vers la gauche jusqu'a l'infini. On compte combien de fois il traverse chaque arete de chaque case. Il existe un theoreme (nom a retrouver) qui dit que si le laser traverse un nombre pair de fois les aretes d'une forme fermee, alors l'origine du laser se trouve a l'exterieur de la forme. Sinon si c'est impair, alors l'origine est a l'interieur et donc on a clique a l'interieur de la case correspondante.

UCI:
Techniquement un protocole plus qu'un algo mais vasy c'est non trivial.
Universal Chess Interface, UCI, est le protocole permettant à notre IA d'interagir avec Stockfish. 
Nous devons donc lancer une ligne de commande virtuelle (avec Popen() de Python) qui nous permet d'avoir les deux programmes qui interagissent entre eux.
On fait ca trois fois par joueur 'bot' (donc jusqu'a 9 fois en tout).
Il y a tout une methode pour coder le plateau d'echec en FEN string, sauf que ca marche pas pour les plateaux a trois joueurs donc on coupe notre plateau en trois plateux a deux joueurs. On utilise une IA du futur qu'on a fait nous meme pour en deduire a partir des reponses de Stockfish le meilleur coup a jouer sur le plateau actuel.

Mapping de la carte:
En fonction des fonctions etc nous avons du representer le plateau sous quatre formes differentes dans le jeu, bien evidemment avec les methodes qu'il faut pour passer de l'une a l'autre a chaque fois.
D'abord il y a les FEN strings, voir plus haut. Ensuite on represente le plateau en memoire en decoupant la partie des rouges et en la mettant derriere les noirs pour pouvoir stocker tout le plateau dans une matrice de 8 par 12 cases.
Peut etre faire un schema pour mieux expliquer le decoupage?
Ensuite on a la representation que Stockfish nous renvoie, au format 'human-readable' (?) -> avec des lettres (a6, b4, c2) donc on a une fonction pour convertir ca d'abord au format plateau de trois joueurs puis au format index de la matrice.
Enfin on a la representation du plateau, donc on est capable de deduire les coordonnees de chaque case en fonction de son nom (a6) et vice-versa (et ce fut un cauchemar a faire celui la)

