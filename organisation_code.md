Le code pour un jeu d'échec à trois se divise en deux algorithmes complexes pour un total de trois classes (Mouvement, Bot et Visuelle)

## Partie Application

### classe Mouvements:

Le rôle de cette classe est la vérification de la validité du mouvement proposé par le joueur humain. Cette information sera renvoyée à la classe Affichage pour suivre le mouvement de la pièce sur l'échequier. La classe vérifie les déplacements possibles pour chaque type de pièce (pions, tours, fous etc.) et l'application des règles spécifiques au jeu d'échec à trois. Cette classe s'occupe également de la gestion des collisions et déterminer si le mouvement d'une pièce entraine une collision avec une autre pièce de l'échiquier et gérer cela en conséquence (ex: élimination d'une pièce adverse). De plus, Mouvements doit identifier les différentes mouvements spéciaux tels que les prises en passant ou les roques. Le plus important est néanmoins le retour des informations sur le mouvement. Il est essentiel que la classe Mouvement et Affichage soient liées pour permettre un bon déroulé du jeu.

La classe suit l'évolution du jeu et étudie la possible mise en échec ou échec et math à chaque tour.

**def verifie_mouvement(self, pos_a, pos_b):**  
  Vérifie si le mouvement de pos_a vers pos_b est légal sur le plateau stockée en mémoire.  
  Renvoie True si c'est le cas, False sinon.

**def mouvements(self, pos):**  
  Renvoie la liste des mouvements possible pour le pion se trouvant sur la case pos.

### classe Bot:

La classe bot est responsable de la mise en oeuvre d'un algorithme complexe pour déterminer les mouvements de l'ordinateur. Elle utilise un ensemble d'algorithmes de recherches pour évaluer les différentes options de mouvements. L'échequier est divisé en trois plateaux de deux joueurs et l'algorithme décide du meilleur mouvement parmi les trois possibles et l'utilise comme choix. La complexité du bot et par extension va être limité par le temps à notre disposition.

**def get_move(self):**  
  Calcule et renvoie un coup optimal sur le plateau actuel en fonction du réglage de difficulté du bot.

## Partie visuelle

### classe Affichage:

La classe Affichage gère l'interface utilisaateur et l'affichage des éléments du jeu (échequier, les différents pions et message lorsqu'en situation d'echec) mais également le déplacement des pions, leur élimination ou apparation lorsque le déplacement proposé par le joueur est validé par Mouvements ou joué par l'ordinateur.

**def start(self):**  
  Démarre le jeu.  
  Lance la fenetre, et démarre la boucle qui traitera les evenements.  
  Bloque jusqu'à la fermeture de la fenetre.  
  Ne renvoie rien.
