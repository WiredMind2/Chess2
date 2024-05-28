**Difficulté principale du projet: L'appropriation de la technologie du raytracing**

Un des défis rencontrés lors de l'élaboration du jeu est la reconnaissance des différentes cases lorsqu'un joueur indique la position du pion joué. Ce problème serait simple à résoudre si les cases étaient carrées, comme sur un plateau d'échecs classique, mais nous avons ici une multitude de polygones irréguliers. Pour que le code reconnaisse dans quelle case le joueur clique, nous avons utilisé la technologie du ray tracing, traditionnellement utilisée pour générer des images en simulant la propagation de la lumière dans un environnement virtuel. 

Le processus commence par le lancement de rayons depuis une caméra virtuelle à travers chaque pixel de l'image. Ces rayons interagissent avec les objets de la scène. Dans notre cas, le rayon part de la position où le joueur a cliqué et se dirige arbitrairement selon le vecteur y = 0. Le rayon est capable de reconnaître un polygone car chaque paire de sommets d'un polygone a été préalablement enregistrée. Ainsi, le rayon peut détecter lorsqu'il traverse un polygone.

Le théorème important que nous utilisons est le suivant, lorsque le rayon part depuis la position où le joueur a cliqué,
- Si le rayon traverse un nombre pair de fois un polygone, c'est que la caméra virtuelle est à l'extérieur, le clic n'est pas dans cette case
- Si le rayon traverse un nombre impair de fois un polygone, c'est que la caméra virtuelle est dans ce polygone et que par conséquent, le clic est inclut dans cette case. La case connue, le reste du code propose les options de déplacement possible et la faisabilité du coup.

---








































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







---

J'ai clarifié et simplifié certaines phrases pour une meilleure compréhension tout en conservant les détails techniques.























point de départ y=0
deux sommets


expliquer comment tu transposes cette technologie à notre problème.
pourquoi ? but final est de déterminer où est ce que je clic pour ainsi sélectionner une case. Ca aurait été trivial si tout était carré mais là, formes irrégulières

Le ray tracing, ou traçage de rayons, est une technique informatique pour générer des images en simulant la propagation de la lumière dans le monde réel. Le processus commence par le lancer de rayons depuis la caméra virtuelle à travers chaque pixel de l'image. Ces rayons interagissent avec les objets de la scène, subissant des réflexions, des réfractions et d'autres effets optiques. Les calculs récursifs sont souvent nécessaires pour suivre les chemins complexes de la lumière, comme les réflexions multiples ou la transmission à travers des matériaux transparents. Une fois tous les calculs effectués, la couleur finale de chaque pixel est déterminée en combinant les contributions de lumière de différentes sources. Malgré sa demande élevée en puissance de calcul, le ray tracing offre des rendus visuellement impressionnants avec des effets réalistes de lumière et de matériaux.

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

