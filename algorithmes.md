**Difficulté principale du projet: L'appropriation de la technologie du raytracing**

Un des défis rencontrés lors de l'élaboration du jeu est la reconnaissance des différentes cases lorsqu'un joueur indique la position du pion joué. Ce problème serait simple à résoudre si les cases étaient carrées, comme sur un plateau d'échecs classique, mais nous avons ici une multitude de polygones irréguliers. Pour que le code reconnaisse dans quelle case le joueur clique, nous avons utilisé la technologie du ray tracing, traditionnellement utilisée pour générer des images en simulant la propagation de la lumière dans un environnement virtuel. 

Le processus commence par le lancement de rayons depuis une caméra virtuelle à travers chaque pixel de l'image. Ces rayons interagissent avec les objets de la scène. Dans notre cas, le rayon part de la position où le joueur a cliqué et se dirige arbitrairement selon le vecteur y = 0. Le rayon est capable de reconnaître un polygone car chaque paire de sommets d'un polygone a été préalablement enregistrée. Ainsi, le rayon peut détecter lorsqu'il traverse un polygone.

Le théorème important que nous utilisons est le suivant, lorsque le rayon part depuis la position où le joueur a cliqué,
- Si le rayon traverse un nombre pair de fois un polygone, c'est que la caméra virtuelle est à l'extérieur, le clic n'est pas dans cette case
- Si le rayon traverse un nombre impair de fois un polygone, c'est que la caméra virtuelle est dans ce polygone et que par conséquent, le clic est inclut dans cette case. La case connue, le reste du code propose les options de déplacement possible et la faisabilité du coup.

On peut ainsi déterminer dans quelle case le clic a été effectué et envoyer l'information pour faire avancer le jeu.

Un autre challenge a été le mapping de la carte.
Il faut savoir qu'afin que l'IA puisse définir le meilleur coup à jouer, nous avons dû adapter le plateau en le divisant en trois plateaux de deux jouers. L'IA issue de Stockfish (moteur d'échec open-source le plus puissant au monde) doit obligatoirement lire le plateau en FEN strings pour pouvoir fonctionner. Notre travail a donc été de d'abord diviser le plateau de trois joueurs en trois plateaux de deux joueurs puis de transposer ces tableaux en FEN String.
