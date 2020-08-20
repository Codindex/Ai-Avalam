import json
import random
import copy

import concurrent.futures as cf # ajout de dernière minute

class Avalam():
    def __init__(self, state):
        self.__game = state["game"]
        self.__before = state["moves"]
        self.__players = state["players"]
        toi = state["you"]
        for n in range(2):
            if state["players"][n]==toi:
                self.__toi = n
        
        self.__mespions = {}
        self.__sespions = {}
        i=0
        for X in state["game"]:
            j=0
            for Y in X:
                if len(Y)>0:
                    if Y[-1] == self.__toi:
                        self.__mespions[(i,j)] = len(Y)
                    else:
                        self.__sespions[(i,j)] = len(Y)
                j+=1
            i+=1
        
        self.__moves = []
        camps = [self.__mespions,self.__sespions]
        for pions in camps:
            for pion in pions:
                i,j = pion
                __k=[(i-1,j-1),(i-1,j),(i-1,j+1),(i,j-1),(i,j+1),(i+1,j-1),(i+1,j),(i+1,j+1)]
                if i == 0:
                    __k=[(i,j-1),(i,j+1),(i+1,j-1),(i+1,j),(i+1,j+1)]
                if i == 8:
                    __k=[(i-1,j-1),(i-1,j),(i-1,j+1),(i,j-1),(i,j+1)]
                if j == 0:
                    __k=[(i-1,j),(i-1,j+1),(i,j+1),(i+1,j),(i+1,j+1)]
                if j == 8:
                    __k=[(i-1,j-1),(i-1,j),(i,j-1),(i+1,j-1),(i+1,j)]

                for n in __k:
                    height = len(state["game"][n[0]][n[1]])
                    if height>0:
                        if height + len(state["game"][i][j])<=5:
                            self.__moves.append({
                                "move": {
                                    "from": [i, j],
                                    "to": [n[0], n[1]]
                                }
                            })
        
        self.__goodmoves = []
        self.__badmoves = []
        for move in self.__moves:
            m=(move["move"]["to"][0],move["move"]["to"][1])
            if m in self.__sespions:
                self.__goodmoves.append(move)
            else:
                self.__badmoves.append(move)

        self.__perfectmoves = []
        self.__suremoves = []
        self.__verybadmoves = []
        self.__notbadmoves = []

        __Goodmoves=copy.deepcopy(self.__goodmoves)
        for goodmove in __Goodmoves:
            p=(goodmove["move"]["from"][0],goodmove["move"]["from"][1])
            From=state["game"][p[0]][p[1]]
            yourheight = len(From)

            m=(goodmove["move"]["to"][0],goodmove["move"]["to"][1])
            To=state["game"][m[0]][m[1]]
            height = len(To)

            if height + yourheight == 5: 
                if From[-1]==self.__toi:
                    self.__perfectmoves.append(goodmove)
                else:
                    self.__suremoves.append(goodmove)
                    self.__goodmoves.remove(goodmove) 
        
        __Badmoves = copy.deepcopy(self.__badmoves)
        for badmove in __Badmoves:
            p=(badmove["move"]["from"][0],badmove["move"]["from"][1])
            From=state["game"][p[0]][p[1]]
            yourheight = len(From)

            m=(badmove["move"]["to"][0],badmove["move"]["to"][1])
            To=state["game"][p[0]][p[1]]
            height = len(To)

            if height + yourheight == 5:
                if From[-1]==self.__toi:
                    self.__notbadmoves.append(badmove)
                else:
                    self.__verybadmoves.append(badmove)
                    self.__badmoves.remove(badmove)
    
    def givepions(self, pions="you"):
        if pions=="you":
            return self.__mespions
        if pions=="him":
            return self.__sespions 

    def _isgameover(self):
        return len(self.__moves)==0

    def _isbadposition(self, move={}):
        if self._isgameover():
            return len(self.__mespions)<=len(self.__sespions)
        
        if len(self.__perfectmoves) > 0:
            return False
        return True

    def _nextstate(self, move):
        G={}
        N=copy.deepcopy(self.__game)
        start=move["move"]["from"]
        __Tower=copy.deepcopy(N[start[0]][start[1]])
        N[start[0]][start[1]]=[]
        end=move["move"]["to"]
        N[end[0]][end[1]]+=__Tower
        G["game"]=N
        G["moves"]=copy.deepcopy(self.__before) # clé move recréée et ajout d'un "mouvement"
        G["moves"].append(move)                 # on peut ajouter n'importe quoi, c'est juste pour le bon fonctionnement de la classe
        # pour qu'elle sache le nombre de mouvements, s'il n'y a pas de clé "move", l'Ia se plante car elle lira cette clé "inexistante"
        G["players"]=self.__players
        G["you"]=self.__players[abs(self.__toi-1)] 
        return Avalam(G)

    def _nextblock(self, move): # en multithreading dans _blockmoves() # last modif
        nextstate = self._nextstate(move)
        end=move["move"]["to"]
        if nextstate.__game[end[0]][end[1]][-1]==self.__toi: # avant-dernière modification, j'avais oublié le [-1]
            i,j=end
            __k=[(i-1,j-1),(i-1,j),(i-1,j+1),(i,j-1),(i,j+1),(i+1,j-1),(i+1,j),(i+1,j+1)]
            if i == 0:
                __k=[(i,j-1),(i,j+1),(i+1,j-1),(i+1,j),(i+1,j+1)]
            if i == 8:
                __k=[(i-1,j-1),(i-1,j),(i-1,j+1),(i,j-1),(i,j+1)]
            if j == 0:
                __k=[(i-1,j),(i-1,j+1),(i,j+1),(i+1,j),(i+1,j+1)]
            if j == 8:
                __k=[(i-1,j-1),(i-1,j),(i,j-1),(i+1,j-1),(i+1,j)]
            e=len(__k)
            for pos in __k:
                if len(nextstate.__game[pos[0]][pos[1]])!=0:
                    if len(nextstate.__game[i][j]) + len(nextstate.__game[pos[0]][pos[1]]) <= 5:
                        break
                e-=1
            if e==0:
                return move
        return None
    
    def _clean(self, liste): # last modif
        X=0
        while X < len(liste):
        	elem = liste[X]
        	if elem != None:
        		X+=1
        	else:
        		del liste[X]
        return liste

    def _blockmoves(self): # last modif
        with cf.ThreadPoolExecutor(8) as executor :
	        movesfound=list(executor.map(self._nextblock, self.__goodmoves))
        movesclean = self._clean(movesfound)
        if len(movesclean) > 0:
            return movesclean
        return None
    
    def _ennemyview(self): # point de vue de l'adversaire, mais sans prévisualiser un coup
        G={}
        G["game"]=copy.deepcopy(self.__game)
        G["moves"]=copy.deepcopy(self.__before)
        G["players"]=self.__players
        G["you"]=self.__players[abs(self.__toi-1)]
        return Avalam(G)
    

    def _nextmoves(self, moves=[]):
        movesfound=[]
        for move in moves:
            nextstate = self._nextstate(move)
            if nextstate._isbadposition():
                movesfound.append(move)
        
        if len(movesfound)>0:
            return movesfound
        return None

    def _antiblock(self): # dernière modif
        choices=[]
        view = self._ennemyview()
        B = view._blockmoves()
        if B is not None:
            for m in B:
                i,j=m["move"]["from"]
                __k=[(i-1,j-1),(i-1,j),(i-1,j+1),(i,j-1),(i,j+1),(i+1,j-1),(i+1,j),(i+1,j+1)]
                if i == 0:
                    __k=[(i,j-1),(i,j+1),(i+1,j-1),(i+1,j),(i+1,j+1)]
                if i == 8:
                    __k=[(i-1,j-1),(i-1,j),(i-1,j+1),(i,j-1),(i,j+1)]
                if j == 0:
                    __k=[(i-1,j),(i-1,j+1),(i,j+1),(i+1,j),(i+1,j+1)]
                if j == 8:
                    __k=[(i-1,j-1),(i-1,j),(i,j-1),(i+1,j-1),(i+1,j)]
                
                for pos in __k:
                    if len(self.__game[pos[0]][pos[1]]) > 0:
                        if self.__game[pos[0]][pos[1]][-1]==self.__toi:
                            if len(self.__game[i][j]) + len(self.__game[pos[0]][pos[1]]) <= 5:
                                choices.append({
                                    "move":{
                                        "from": [pos[0],pos[1]],
                                        "to": [i,j]
                                    }
                                })
        
        if len(choices) > 0:
            return choices
        return None
    
    def _message(self, typemove): # pour aller chercher le message dans le fichier json
        try:
            with open("Messages_personnalisés.json") as message:
                M = json.loads(message.read())
                return M[typemove]
        except:
            pass

    def _findgoodmove(self):
        # bons mouvements
        if len(self.__perfectmoves) > 0:
            return (self.__perfectmoves, self._message("perfectmove"))

        if len(self.__before) < 10:
            __l = len(self.__before)
            return (self._nextmoves(self.__goodmoves), self._message("start{}".format(1+int(__l/2))))
        
        if self._blockmoves() is not None:
            return (self._blockmoves(), self._message("blockmove"))
        
        if self._antiblock() is not None:
            return (self._antiblock(),self._message("antiblock"))
        
        if self._nextmoves(self.__goodmoves) is not None:
            return (self._nextmoves(self.__goodmoves), self._message("goodmove"))

        if len(self.__suremoves) > 0:
            return (self.__suremoves, self._message("suremove"))
        
        if len(self.__goodmoves) > 0:
            return (self.__goodmoves, self._message("almostbadmove"))
            # Même s'il y a un perfectmove pour l'adversaire au coup suivant, c'est mieux que de prendre un de nos pions maintenant
        
        # mauvais mouvements
        if len(self.__notbadmoves) > 0:
            return (self.__notbadmoves, self._message("notbadmove"))

        if self._nextmoves(self.__badmoves) is not None:
            return (self._nextmoves(self.__badmoves), self._message("badmove"))

        return (self.__badmoves, self._message("lastmove"))

    
    def response(self):
        x = self._findgoodmove()
        __move = random.choice(x[0])
        __move['message'] = x[1]
        # print(isinstance(__move,dict)) # ajout d'une vérification si besoin
        return __move


import cherrypy
import sys
import socket

class Server():
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        cherrypy.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        cherrypy.response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        if cherrypy.request.method == "OPTIONS":
            return ''
        
        body = cherrypy.request.json
        print(body) # imprime dans le terminal ce qui est reçu
        moving = Avalam(body).response()
         
        return moving
    
    @cherrypy.expose
    def ping(self):
        return "pong... Vous voyez bien que ça marche, alors qu'est-ce qu'on attend pour jouer ? :)"

if __name__ == "__main__":
    # les lignes suivantes permettent de modifier le dictionnaire d'inscription depuis le terminal
    if len(sys.argv) > 1:
        port=int(sys.argv[1])
    else:
        port=50000
    
    if len(sys.argv) > 2:
        name=str(sys.argv[2])
    else:
        name="AvalaMaster"
    
    if len(sys.argv) > 3:
        matricules=[]
        matricules.append(str(sys.argv[3]))
    else:
        matricules=["18281"]
    if len(sys.argv) > 4:
        matricules.append(str(sys.argv[4]))

    Z = {
        "matricules": matricules,
        "port": port,
        "name": name
    }
    print(Z)
    S = json.dumps(Z, indent=4)
    R = S.encode()
    s = socket.socket()
    s.connect((socket.gethostname(), 3001))
    s.send(R)
    s.detach() # ajout inutile parce qu'on n'utilise plus ce socket ensuite, mais on ne sait jamais...

    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': port})
    cherrypy.quickstart(Server())

# dictionnaire envoyé par défaut
# {
# 	"matricules": ["18281"],
# 	"port": 50000,
# 	"name": "AvalaMaster"
# }