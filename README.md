# Ai-Avalam-Player

Le projet informatique de l'Ecam de 2020.
Mon IA du projet pour le jeu Avalam, comment elle fonctionne, et quelles bibliothèques sont utilisées.

## Stratégie

Parlons tout d'abord de son fonctionnement...
Mon Ia contient 2 classes, `Avalam(state)` pour le choix du mouvement, et `Server()` pour le serveur qui assure la réception de l'état de jeu et l'envoi du mouvement choisi.

## Classe de l'Ia (Avalam(state))
Bibliothèques utilisées (modules de python):
- `json`
- `random`
- `copy`
- `concurrent.futures` (multithreading)

On va diviser son fonctionnement en plusieures parties, de la réception de l'`état de jeu` à l'envoi de la réponse

### État de jeu

Voici un état de jeu que l'Ia est en mesure de recevoir:

```json
{
	"game": [
		[ [],  [],  [], [0], [1],  [],  [],  [],  []],
		[ [],  [],  [], [1], [0], [1], [0], [1],  []],
		[ [],  [], [1], [0], [1], [0], [1], [0], [1]],
		[ [],  [], [0], [1], [0], [1], [0], [1], [0]],
		[ [], [0], [1], [0],  [], [0], [1], [0],  []],
		[[0], [1], [0], [1], [0], [1], [0],  [],  []],
		[[1], [0], [1], [0], [1], [0], [1],  [],  []],
		[ [], [1], [0], [1], [0], [1],  [],  [],  []],
		[ [],  [],  [],  [], [1], [0],  [],  [],  []]
	],
	"moves": [],
	"players": ["joueur 0", "joueur 1"],
	"you": "joueur 1"
}
```

C'est un état de jeu de début de partie dans cet exemple.
L'IA reçoit l'état du jeu et enregistre les données utiles, à savoir :
- la `grille de jeu` qui contient la position de toutes les tours, elle est enregistrée dans la variable `self.__game` rattachée à la classe ;
- les mouvements effectués dans `self.__before` (plus précisément, elle récupère le nombre de mouvements précédemment effectués : elle n'analyse pas les mouvements précédents, ce n'est pas nécessaire pour le choix du prochain mouvement); n'est vraiment utilisé qu'en début de partie, mais j'y reviendrai ;
- les noms des joueurs et le nom de notre joueur, pour pouvoir attribuer les tours à chaque camp (enregistre "la position de notre nom dans la liste des joueurs" dans `self.__toi`).

### Classement des tours et recherche des mouvements possibles
(Dans la partie `__init__` de la classe `Avalam()`)

Grâce à ce dernier point, l'Ia est en mesure de classer les différentes tours dans chaque camp en analysant la `grille de jeu`.
Dans notre cas, elle va stocker les tours du joueur 1 dans la liste `self.__mespions` , et les tours adverses dans `self.__sespions` en regardant simplement le dernier chiffre de chaque liste.
Ensuite, elle recherche tous les mouvements possibles pour chaque pions dans la grille, sachant que déplacer un pion sur une case vide est interdit, mais il faut aussi que la hauteur de la tour formée après le mouvement ne dépasse pas 5 pions.
Le mouvement est un `dictionnaire` python qui ressemble à celui-ci :

```json
{
    "move": {
        "from": [4, 5],
        "to": [5, 6]
    }
}
```

On va ensuite pouvoir classer les mouvements par ordre d'importance.

### Classement des mouvements par ordre d'importance
(`__init__`)

J'entends par là que certains mouvements sont à privilégier si on veut avoir un maximum de points à la fin de la partie. En effet, c'est celui qui "possède" le plus de tours qui gagne ! La hauteur des tour n'a pas d'importance, sauf s'il y a égalité : dans ce cas c'est celui qui a le plus de tours à 5 étages qui gagne.
Donc il est préférable d'"avaler" les tours adverses (d'où le nom `Avalam`) pour lui faire perdre des points !
On effectue donc un 1er classement des mouvements possibles :
- Les mouvements qui permettent la capture des tours adverses sont placées dans la liste `self.__goodmoves`;
- Par contre, les mouvements qui avalent nos propres pions sont placées dans `self.__badmoves`.

### Classement avancé
(toujours dans `__init__`)

Maintenant que nous avons un 1er classement, on peut chercher quels sont les "meilleures" et les "pires" des bons et mauvais mouvements. Dans ce jeu-ci :
- les `meilleurs mouvements` consistent à former une tour de 5 pions (qui ne peut donc plus être bougée, ni capturée) avec un pions de notre camp à son sommet : cela nous garanti un point sûr à la fin de la partie !;
- À l'inverse, le même mouvement avec un pion adverse au sommet est un mouvement à ne pas faire... les `pires mouvements`.

Pour les `goodmoves`:
- les `meilleurs mouvements` sont placés dans `self.__perfectmoves`;
- les `pires mouvements` dans `self.__suremoves` en prenant soin de les supprimer des `goodmoves` (voir pourquoi plus loin dans le `choix du mouvement`).

Même principe pour les `badmoves`, respectivement dans `self.__notbadmoves` et `self.__verybadmoves`. À noter toutefois que cette dernière liste ne sera jamais utilisée dans le choix d'un mouvement : d'une part, parce que ce sont les pires mouvements possibles, mais aussi parce que c'est les mouvements contraires aux `perfectmoves`. Or s'il n'y en a pas, alors il n'y a aucun `verybadmoves` non plus. Mais c'est juste une sécurité au cas où les autres mouvements ne seraient pas pris en compte.

### Choix du mouvement
(`_isbadposition()`, `_nextstate()`, `_nextblock()`, `_clean()`, `_blockmoves()`, `_ennemyview()`, `_antiblock()`, `_nextmoves()`, et `_findgoodmove()`)

C'est là que cela devient intéressant...
On choisi le mouvement par rapport aux mouvements disponibles suivant l'ordre d'importance :
`perfectmoves > goodmoves > suremoves > notbadmoves > badmoves > verybadmoves`
Bien évidemment c'est l'ordre inverse du point de vue de l'adversaire !
Il est important de jouer les `perfectmoves` en 1er, car l'adversaire peut faire le mouvement inverse qui l'avantagerait (`perfectmoves` ><`verybadmoves`==`perfectmoves` de l'adversaire)

#### Prévisualisation

S'il n'y a pas de `perfectmove`, il y a une étape qui s'ajoute pour prendre certains mouvements parmis les `goodmoves` : en effet, l'Ia va choisir lesquels de ces mouvements ne favorisent pas l'adversaire en lui offrant un `perfectmove` au tour suivant.
Pour cela, et pour chaque mouvement de la liste des `goodmoves` (qui n'ont pas étés placés dans `suremoves`), l'Ia va recréer l'état de jeu après le mouvement (`_nextstate()`) et l'analyser en 3 temps :

- D'abord avec `_blockmoves()`, cette fonction est elle-même divisée en 2 fonctions :
    - `_nextblock()` qui va regarder si le mouvement crée une tour imprenable à notre camp même si elle ne fait pas 5 pions de haut (aussi bon qu'un `perfectmove`) et les place dans une liste; utilise le `multitheading` avec `concurrent.futures`;
    - `_clean()` qui enlève tous les `None` de la liste formée.

- Ensuite, si `_blockmoves()` ne donne pas de mouvements, on va chercher si l'adversaire peut faire des `blockmoves` de son coté, et si on peut le bloquer avant qu'il ne le fasse, grâce à `_antiblock()`, qui utilise `_ennemyview()` et `_nextmoves()` (tiret suivant) en regardant du point de vue de l'adversaire; s'il existe des mouvements permettant de bloquer un ou des `blockmoves`, et qu'ils sont compris dans la liste des `goodmoves`, ils sont rassemblés dans une liste;

- Si cela n'a toujours rien donné, elle utilise simplement `_nextmoves()` (qui utilise `_isbadposition()`) pour voir s'il y a des `perfectmoves` qui apparaissent aux yeux de l'adversaire au prochain mouvement ! S'il n'y en a aucun, elle place le mouvement correspondant dans une liste et passe au suivant (comme les 2 fonctions précédentes).

La liste ainsi formée par l'une des 3 fonctions ci-dessus est donc envoyée à l'étape suivante (message bonus).

On réutilise la méthode de `_nextmoves()` pour les badmoves si on arrive à eux (même s'il est rare que l'on arrive à devoir analyser ces mouvements, mais c'est toujours mieux que d'en prendre un au "hasard")
Ces méthodes ne s'appliquent qu'aux `goodmoves` et `badmoves`, car les autres mouvements bloquent la tour formée, donc il est inutile de savoir si cette tour permet ou non un `perfectmove`....

### Choix du mouvement (résultats)

Au final, si l'on devait inclure les mouvements analysés dans l'ordre d'importance, cela donnerait ceci:

perfectmoves > `blockmoves` > `nextmoves` > suremoves > `goodmoves` restants > notbadmoves > `nextbadmoves` > badmoves restants > verybadmoves

Comme vous avez pu le remarquer, il n'est pas nécessaire d'analyser le jeu jusqu'à son dénouement avec une sorte de boucle dans la programmation, car cela prendrait trop de temps (surtout en début de partie), or il faut répondre dans les 10 secondes sous peine de recevoir une pénalité. Il vaut mieux se concentrer sur la capture des tours adverses, et sur l'état du jeu suivant le mouvement si celui-ci concerne une tour qui peut encore bouger ou être capturée par la suite.

### Message bonus
(`_findgoodmove()` et `response()`)

C'est la partie facultative :
Avec la sélection des meilleurs mouvements possibles, je rajoute un message en fonction des mouvements s'ils sont bons ou pas. Mais on peut toujours les changer s'il on veut, il suffit de changer la valeur correspondante au type de mouvement dans le fichier `json` séparé `Messages_personnalisés`, car c'est là qu'ils sont stockés. Libre à vous de mettre ce que vous voulez si ça vous chante :), mais ne modifiez pas les clés associées ! (Ni de le déplacer hors du dossier où vous avez cloné ce dépot)

Par exemple, les clés "début" sont des messages envoyés sur les 5 1ers mouvements d'un match (c'est seulement ici qu'est vraiment utilisé la variable `self.__before` énoncée au début dans le paragraphe `État de jeu`, c'est une fonctionnalité optionnelle que j'ai rajoutée en dernier)

La liste des mouvements et le message personnalisé sont mis dans un `tuple` dans `_findgoodmove()`, `response()` sert juste à choisir aléatoirement un mouvement dans la liste (avec le module `random`), et à rajouter le message dans le dictionnaire choisi (oui c'est pratique d'avoir construit les mouvements dans un dictionnaire python dès le départ)

Voilà donc ce qui est renvoyé à la ligne `moving = Avalam(body).response()` dans la classe du serveur Cherrypy.

```json
{
    "move": {
        "from": [4, 5],
        "to": [5, 6]
    },
    "message":"Le message choisi"
}
```

## Classe du serveur (Server())
Bibliothèque utilisée : `cherrypy` (avec json si on compte les décorateurs)
Attention, il n'est pas forcément inclu avec le programme python. Si ce n'est pas déjà fait, il faut télécharger la librairie `cherrypy` pour pouvoir l'utiliser (vous pouvez utiliser le programme `pip` dans le terminal si vous l'avez)

La classe du serveur est grandement basée sur celle présentée par le prof sur son dépot GitHub, contenant entre-autres l'énoncé du projet Ia de cette année et le serveur permettant le lancement du jeu de cette année (Avalam) et des années précédentes.

Quoi qu'il en soit, les choses importantes à retenir sont que :
- Il reçoit l'état de jeu : `body = cherrypy.request.json`;
- Il le fait analyser par la classe Avalam() : `moving = Avalam(body).response()`;
- Et il renvoie la réponse de ladite classe au superviseur de partie.

Grâce aux décorateurs (`@cherrypy.tools.json_in` et `@cherrypy.tools.json_out`), les données reçues en json sont transformées en dictionnaire python, et les données renvoyées sont encodées en format json.
La route `ping` sert juste à vérifier que le serveur répond si on l'appelle.

## Lancement du programme et envoi du dictionnaire d'inscription
Bibliothèques utilisées :
- socket
- sys

Tout ce que vous avez à faire pour lancer le programme, c'est de taper `python AvalaMaster.py` dans un terminal. Tâchez toutefois de lancer le superviseur de partie avant.
Pourquoi ? Parce qu'à la fin du code, j'ai programmé l'envoi automatique du `dictionnaire d'inscription` au superviseur, en plus du lancement de notre serveur.
Ce dictionnaire ressemble à celui-ci (le port et les matricules sont des nombres, pas des strings) :

```json
{
    "matricules": ["matricule 1", "matricule 2"],
    "port": "port",
    "name": "name"
}
```

Cependant, si vous voulez mettre un autre port, nom d'Ia ou d'autres matricules, il suffit de les rajouter dans le terminal quand vous lancer le programme : `python AvalaMaster.py port name matricule1 matricule2` dans cet ordre.
Le programme envoie donc automatiquement ce dictionnaire au superviseur, sur le port 3001, après s'être connecté au socket bien entendu !

Et voilà ! Il vous suffit ensuite d'utiliser la page internet du superviseur de partie pour combattre les autres Ia. Que le meilleur gagne !

Ah oui j'oubliais ! Si le prof lit ceci, sachez que mon matricule est bien dans les valeurs par défaut du dictionnaire, en plus du port 50000 et du nom `AvalaMaster`. Voilà, amusez-vous bien !