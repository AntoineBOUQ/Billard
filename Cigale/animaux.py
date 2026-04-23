# -*- coding: utf-8 -*-

import numpy as np
from numpy.random import randint
from dprint import dprint
from terrain import Marais

class Animal():
    """
    Classe décrivant les comportement par défaut des animaux. Peut-être 
    utilisée en l'état ou sous classée pour définir des comportements de
    déplacement différents.
    """
    def __init__(self, abscisse, ordonnee, ecosysteme, capacite=20):
        """
        Créé un animal aux coordonnées désirées.
        
        Paramètres
        ----------
        abscisse, ordonnée: int
            Les coordonnées auxquelles l'animal sera créé.
            
        ecosysteme: Ecosysteme
            L'instance de la classe Ecosysteme à laquelle l'animal va
            se rattacher.
            
        capacité: int
            niveau de santé maximal de l'animal. Vaut 10 par défaut.
            
        Notes
        -----
            Aucune vérification n'est fait à la création pour s'assurer
            que les coordonnées demandées sont disponibles dans l'ecosystème.
        """
        
        self.__sante = randint(capacite//2, capacite+1)
        self.__bebe = True
        self.__en_couple = False
        self._ecosysteme = ecosysteme
        self._max = capacite
        self.coords = abscisse, ordonnee

    @property
    def bebe(self):
        """
        bebe: bool
            Drapeau permettant de différencier les nouveaux nés qui existaient
            avant le tour de jeu courant. Un nouveau né n'est pas influencé 
            par le terrain sur laquelle il se trouve lors de sa naissance
            
        Notes
        -----
        Cet attribut est en lecture seule.
        """
        return self.__bebe
        
    @property
    def en_couple(self):
        """
        en_couple: bool
            Drapeau permettant de marquer qu'un individu a déjà tenté de se
            reproduire lors du tour courant et n'est donc pas disponible pour
            former un autre couple.
        """
        return self.__en_couple
        
    @en_couple.setter
    def en_couple(self, val):
        if val in (True, False):
          self.__en_couple = val
          
    @property
    def sante(self):
        """
        sante: float
            Le niveau de santé de l'animal. Si ce niveau arrive à 0 l'animal
            est marqué comme mort et sera retiré du plateau de jeu
        """
        return self.__sante
    
    @sante.setter
    def sante(self, value):
        if value <= self._max:
            self.__sante = value
        if value <= 0: #<= car certaines cases enlèvent plus de 1 en santé
            self._ecosysteme.animaux_morts.append(self)

    @property
    def coords(self):
        """
        coords: tuple
            Les coordonnées de l'animal sur le plateau de jeu
        
        Notes
        -----
        Lors de la création de l'animal aucune vérification n'est effectuée
        pour s'assurer que la case demandée est libre. Par contre au cours
        de son évolution lors des tours suivants s'il tente de se rendre sur
        une case déjà occupée l'exception ''ValuerError'' sera levée, l'animal
        restera sur la case où il est présent et l'action de cette case sera
        appliquée à nouveau. Suivant l'effet recherché il conviendra, ou non,
        d'ignorer cette exception.
        """
        return self.__coords

    @coords.setter
    def coords(self, nouv_coords):
        xmax, ymax = self._ecosysteme.dims
        x, y = nouv_coords
        x = min(x, xmax-1)
        x = max(x, 0)
        y = min(y, ymax-1)
        y = max(y, 0)
                            
        plateau = self._ecosysteme.plateau
        couche_animaux = self._ecosysteme.Couche_animaux
        couche_terrain = self._ecosysteme.Couche_terrain

        if not self.__bebe:
            # premier cas, l'animal a décidé de ne pas bouger
            if self.coords == nouv_coords:
            # on applique une nouvelle fois l'action éventuelle liée à la case
                plateau[x, y, couche_terrain].action(self)
                return

            # si la destination est libre on y va
            elif plateau[x ,y, couche_animaux] is None:
                plateau[x ,y, couche_animaux] = self

                # on  vide l'ancienne case
                plateau[self.coords[0], self.coords[1],
                                    couche_animaux] = None
                
                self.__coords = x,y
                # on applique les éventuelles actions que la case peut avoir sur
                # l'animal
                plateau[x, y, couche_terrain].action(self) 
            else: 
                # pas de bol, la case a été prise entre le tour de décision
                # et le tour de mouvement
                # on applique à nouveau l'action de la case courante            
                plateau[self.coords[0], self.coords[1],
                                    couche_terrain].action(self) 
                raise ValueError("La case (%i,%i) est occupée"%(x, y))

        else: #c'est un bebe
            plateau[x ,y, couche_animaux] = self
            # on met à jour l'information de coordonnées dans l'animal
            self.__coords = x,y
            self._ecosysteme.append(self)
            self.__bebe = False


    def reproduction(self, rayon_vision=1, taux_succes=0.4):
        """
        Va chercher un partenaire de reproduction éventuel autour de
        l'animal courant et créé un nouvel animal si la reproduction
        est possible.
        
        Paramètres
        ----------
        rayon_vision : int, optionnel
            Rayon de recherche d'un voisin autour de l'animal courant. 
            Vaut 1 par défaut.
        taux_succes : float
            Probabilité de succès d'une reproduction. Vaut 0.4 par défaut
            
        Renvoie
        -------
        Rien
        
        Notes
        -----
        Si la propagation des cases danger n'est pas implémentée il vaut mieux
        prendre une taux de succes de 0.3.
        La capacité du nouveau né sera égale à la partie entière de la moyenne
        de la santé des parents. Des parents en mauvaise santé feront donc des
        bébés plus faibles.
        """
        plateau = self._ecosysteme.plateau
        couche_animaux = self._ecosysteme.Couche_animaux
        couche_terrain = self._ecosysteme.Couche_terrain

        x, y = self.coords

        # on ne regarde pas "par dessus" les bords du plateau        
        vision_x = (max(0, x-rayon_vision), 
                        min(self._ecosysteme.dims[0], x+rayon_vision+1))
        vision_y = (max(0, y-rayon_vision), 
                    min(self._ecosysteme.dims[1], y+rayon_vision+1))
        plateau_visible = plateau[
                    vision_x[0]:vision_x[1],
                    vision_y[0]:vision_y[1],
                    couche_animaux]
                
        cases_vides = np.equal(plateau_visible, None)
        animaux_voisins = plateau_visible[np.logical_not(cases_vides)]
        
        for ins in animaux_voisins:
            if ins is not self and not self.en_couple and not ins.en_couple\
                        and not ins.bebe and type(ins) == type(self) and\
                        np.random.rand() < taux_succes:
                self.en_couple = True
                ins.en_couple = True
                # on va se limiter à positionner le bébé autour de l'animal
                # à l'origine du couple sinon c'est vraiment bien lourd à
                # gérer et ça n'apporte rien
                x_vide, y_vide = np.where(cases_vides)
                if x_vide.size > 0:
                    # le plus simple c'est de tricher et d'aller chercher
                    # dans couche_terrain les coordonnées de là où on veut
                    # attetrir sinon c'est assez pénible de reconstruire
                    # bebe_x et bebe_y en fonction de la forme qu'aura
                    # plateau_visible (coins, bords...)
                    choix_case = np.random.randint(0,x_vide.size)
                    case_cible = plateau[vision_x[0]:vision_x[1],
                                vision_y[0]:vision_y[1], couche_terrain]\
                                [x_vide[choix_case], y_vide[choix_case]]
                                        
                    bebe_x = case_cible.coords[0]
                    bebe_y = case_cible.coords[1]
                    bebe_capacite = (self.sante + ins.sante) // 2
                    dprint("Naissance", type(self), bebe_x, bebe_y,
                          "papa", self.coords, "maman", ins.coords)                  
                    self._ecosysteme.animaux_nes.append((type(self),
                                                          bebe_x, bebe_y,
                                                          bebe_capacite))
                
        
    def __str__(self):
        """
        Affiche l'état courant de l'animal.
        
        Paramètres
        ----------
        Aucun
        
        Renvoie
        -------
        s: str
            La chaîne de caractères qui sera affichée via ''print''
        """
        return "%c : position (%i, %i) etat %i/%i"%(
            self.car(), self.coords[0], self.coords[1],
            self.sante, self._max
            )
    
    def car(self):
        """
        Renvoie l'identifiant de l'espèce de l'animal.
        
        Paramètres
        ----------
        Aucun
        
        Renvoie
        -------
        c: str
            Le caractère représentant l'animal.
        """
        return 'A'    

    def decider(self):
        """
        Décide de la destination de l'animal en fonction de sa stratégie de
        déplacement.

        Paramètres
        ----------
        Aucun
        
        Renvoie
        -------
        Rien
        """
        
        xmax, ymax = self._ecosysteme.dims

        dx = randint(-2, 2+1)
        dy = randint(-2, 2+1)

        self._destination = self.coords[0] + dx, self.coords[1] + dy

    def bouger(self): 
        """
        Tente d'effectuer le mouvement choisi dans ''decider''.

        Paramètres
        ----------
        Aucun
        
        Renvoie
        -------
        Rien
        
        Notes
        -----
        Si la case choisie est déjà occupée l'animal ne bougera pas et
        l'exception levée lors de la tentative de mise à jour de ses 
        coordonnées sera ignorée.
        """
        try:
            self.coords = self._destination
        except ValueError:
            return False        
        return True
        
class Fourmi(Animal):
    def decider(self):
        self.en_couple = False
        xmax, ymax = self._ecosysteme.dims
        nx, ny = self.coords
        if self.sante>=4:
            if randint(0,2+1):
                nx += randint(-3, 3+1)
            else:
                ny += randint(-3, 3+1)
        else:
            nx -= xmax//10
            ny -= ymax//10
        self._destination = nx, ny

    def car(self):
        return 'F'

class Cigale(Animal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sante = self._max
        
    def decider(self):
        self.en_couple = False
        xmax, ymax = self._ecosysteme.dims
        nx, ny = self.coords
        action = randint(0,2+1)
        if action==1:
            dprint("Je danse.")
        elif action==2:
            dprint("Je chante.")
        elif self.sante>=4:
            if randint(0,2+1):
                nx += randint(-3, 3+1)
            else:
                ny += randint(-3, 3+1)
        else:
            nx -= xmax//20
            ny -= ymax//20
        
        self._destination = nx, ny


    def car(self):
        return 'C'

class Mogwai(Animal):
    """
    ''Animal'' inoffensif dans son état Gizmo le ''Mogwai'' devient un fléau
    qui détruit tout sur son passage quand il devient un Gremlins.
    """
    Rayon_marais = 1
    Gremlins = False
    def __init__(self, *args, **kwargs):
        """
        Les ''Mogwai'' sont pratiquement invulnérables, leur santé est
        de 1e6 à la naissance.
        """
        super().__init__(*args, **kwargs)
        self._max = 1e6
        self.sante = self._max
        
    def reprodution(self):
        """
        Les Mogwai ont un taux de succèes de 0.8 lors de leur reproduction.
        """
        super().bouger(taux_succes = 0.8)
        
    def bouger(self):
        """
        Dans sa phase Gizmo le ''Mogwai'' se déplace comme un ''Animal'', dans
        sa phase Gremlins il va détruire la case où il se trouve, ainsi que ses
        voisines dans un rayon de ''Rayon_marais'', en les transformant en
        ''Marais''
        """
        super().bouger()
        if not Mogwai.Gremlins:
            return
        dprint(self)
        plateau = self._ecosysteme.plateau
        couche_terrain = self._ecosysteme.Couche_terrain
        x, y= self.coords
        # on ne détruit pas "par dessus" les bords du plateau        
        marais_x = (max(0, x - Mogwai.Rayon_marais), 
                        min(self._ecosysteme.dims[0], x +
                            Mogwai.Rayon_marais + 1))

        marais_y = (max(0, y - Mogwai.Rayon_marais), 
                min(self._ecosysteme.dims[1], y +
                    Mogwai.Rayon_marais + 1))           

        terrain_hs = plateau[marais_x[0]:marais_x[1],
                            marais_y[0]:marais_y[1],
                            couche_terrain]     
        
        # reshape(-1) evite la copie de flatten, nditer pas évident
        # à utiliser sur array object, au pire ils font une double
        # boucle
        for case in terrain_hs.reshape(-1):
            i, j = case.coords
            plateau[i, j, couche_terrain] =\
                    Marais(self._ecosysteme, case.coords)
            plateau[i, j, couche_terrain].propage_danger()

    def car(self):
        return 'G'
        
