# -*- coding: utf-8 -*-
import numpy as np
import random as rnd
import time
import matplotlib.pyplot as plt

from animaux import Fourmi, Cigale, Mogwai
from dprint import dprint
from terrain import Savane, Marais, Nourriture

"""
Ce module contient la définition de la classe principale servant à gérer le jeu
"""
        
class Ecosysteme(list):
    """
    Classe gérant le déroulement du jeu. 
    """
    Couche_animaux = 0
    Couche_terrain = 1
    def __init__(self, nb_ins,nbt,xmax,ymax):
        self.__xmax = xmax
        self.__ymax = ymax       
        self.__plateau = np.empty((xmax, ymax, 2), dtype=object)
        self.nbtour =  nbt  
        self.cases_besoin_maj = []
        self.animaux_morts = []
        self.animaux_nes = []
        
        # liste utilisée pour tracer les différentes populations
        # au cours des tours de jeu
        self.population = []
        
        # remplissage de la couche liée aux animaux
        # merci stackoverflow   
        # on génère toutes les combinaisons de coordonnées possibles     
        py, px = np.mgrid[0:xmax, 0:ymax]
        
        # on sauvegarde pour plus tard ça peut servir (cataclysme)
        self.__points = np.c_[py.ravel(), px.ravel()]
        
        # on choisit nb_ins entiers entre 0 et xmax*ymax
        idx_points_choisis = np.random.choice(xmax*ymax, nb_ins, replace=False)        
        
        # et on utilise ces entiers aléatoires pour aller chercher les
        # les combinaisons correspondantes        
        for pt in self.__points[idx_points_choisis]:
            choix = np.random.rand()           
            if choix < 0.4:
                Fourmi(pt[0], pt[1], self)
            elif choix < 0.8:
                Cigale(pt[0], pt[1], self)
            else:                
                Mogwai(pt[0], pt[1], self)
        # ça part dans les animaux
        #self.append(insecte)
       
        # remplissage de la couche liée aux cases
        # on aura majoritairement de la savane, puis arbitrairement
        # 10% de Maraiss et 20% de nourriture


        # test double boucle, au final c'est le moins pire
        cases_danger = []
        for i in range(xmax):
            for j in range(ymax):
                choix = np.random.rand()
                if choix > 0.3:            
                    case_type = Savane
                elif choix  > 0.1:
                    case_type = Nourriture
                else:
                    case_type = Marais
                    cases_danger.append((i,j))
                self.__plateau[i, j, Ecosysteme.Couche_terrain] = \
                                case_type(self, (i,j))
        
        for i,j in cases_danger:
            self.__plateau[i, j, Ecosysteme.Couche_terrain].propage_danger()
    
    @property
    def plateau(self):
        """
        plateau: ndarray
            Donne accès au tableau Numpy gérant la cohérence du plateau.
        """
        return self.__plateau
        
    @property
    def dims(self):
        """
        Renvoies les dimensions du plateau de jeu
        """
        return self.__plateau.shape[0:2]
        
    def __str__(self):
        """
        Affiche le plateau de jeu en mode texte suivant les codes couleur
        définis dans les sous classes de ''Terrain'' et les caractères définis
        dans les sous classes de ''Animal''.
        
        Paramètres
        ----------
        Aucun
        
        Renvoie
        -------
        s: string
            La chaîne de caractères qui sera affichée via ''print''
            
        Notes
        -----
        Le terminal utilisé pour l'affichage devra savoir gérer les codes
        d'échappement bash.
        """
        
        pos = {}
        for ins in self:
            pos[ins.coords]=ins.car()
        s = ""
        for i in range(self.__xmax):
            for j in range(self.__ymax):
                s+=self.plateau[i,j, Ecosysteme.Couche_terrain].code_couleur()
                if (i, j) in pos:
                    s += pos[(i,j)]
                else:
                    s += "."
            s += "\x1b[0m\n"
        return s
    
    def unTour(self):
        """
        Effectue toutes les actions liées à un tour de jeu.
        
        Paramètres
        ----------
        Aucun
        
        Renvoie
        -------
        Rien
        """
        
        # attention à utiliser le shuffle de random, pas celui de np.random
        # sinon on va avoir de gros soucis quand np va tenter de caster
        # l'instance d'ecosysteme en array !
        nb_fourmis = 0
        nb_cigales = 0
        nb_mogwai = 0
        
        rnd.shuffle(self)
        for ins in self:  # fonctionne car Ecosysteme descend de list
            ins.decider()
        for ins in self:
            ins.bouger()
            if type(ins) == Fourmi:
                nb_fourmis += 1
            elif type(ins) == Cigale:
                nb_cigales += 1
            else:
                nb_mogwai += 1
        # mort des animaux
        for ins in self.animaux_morts:
            dprint("mort de: "+str(ins))
            self.remove(ins)
            self.plateau[ins.coords[0], ins.coords[1],\
                                Ecosysteme.Couche_animaux] = None
            # un insecte qui meurt sur une case transforme cette case en
            # nourriture si c'est de la Savane
            terrain = self.plateau[ins.coords[0], ins.coords[1],\
                                Ecosysteme.Couche_terrain]
            if type(terrain) == Savane:
                self.cases_besoin_maj.append(ins.coords)
        self.animaux_morts = []

        for ins in self:
            # en faisant ça en dernier on n'a pas à traiter de cas particulier
            # pour savoir si on decider() ou bouger() sur un bébé
            ins.reproduction()

        # création des animaux nés
        for type_ins, x, y, capacite in self.animaux_nes:
            type_ins(x, y, self, capacite)
                            
        # c'est idiot de reparcourir les animaux pour dire qu'ils ne sont
        # plus en couple, on va faire ça dans décider plutôt
            
        self.animaux_nes = []
        dprint("Nombre d'animaux: ", len(self))

        self.population.append((nb_fourmis, nb_cigales, nb_mogwai))

        for x,y in self.cases_besoin_maj:
            terrain = self.plateau[x,y, Ecosysteme.Couche_terrain]
            # on sauvegarde le malus associé à cette case
            delta_sante = terrain.impact_sante - terrain.Impact_sante_defaut
            # on fait la transformation de case
            self.plateau[x,y, Ecosysteme.Couche_terrain].maj()
            # on remet en place le malus de la case précédente
            self.plateau[x,y, Ecosysteme.Couche_terrain].impact_sante +=\
                                delta_sante
            
        self.cases_besoin_maj = []

    def cataclysme(self):
        """
        Transforme un nombre aléatoire, mais conséquent, de cases de 
        ''Terrain'' en cases ''Marais''.
        Le nombre de cases transformées est compris entre la moitié et
        la totalité des cases du tableau.
        
        Paramètres
        ----------
        Aucun

        Renvoie
        -------
        Rien        
        """
        
        nb_cases = self.__xmax * self.__ymax
        nb_danger = np.random.randint(nb_cases//2, nb_cases+1)
        idx_points_choisis = np.random.choice(nb_cases, 
                                              nb_danger, replace=False)        
        # et on va chercher les nbins premières        
        for i,j in self.__points[idx_points_choisis]:
            self.__plateau[i, j, Ecosysteme.Couche_terrain] = \
                                    Marais(self, (i, j))
            self.__plateau[i, j, Ecosysteme.Couche_terrain].propage_danger()
            
    def simuler (self):
        """
        Contrôle l'évolution du jeu, affiche le résultat de chaque tour dans
        un terminal.
        
        Paramètres
        ----------
        Aucun

        Renvoie
        -------
        Rien  
        """
        
        for t in range(self.nbtour):
            print("### Tour %i ###"%(t))
            self.unTour()
            if t == int(self.nbtour*0.8):
                self.cataclysme()
            if t == int(self.nbtour*0.5):
                Mogwai.Gremlins = True
            print(self)
            time.sleep(0.5)
            
    def statistiques(self):
        """
        Présente l'évolution des différentes populations d'animaux en fonction
        du tour de jeu. Cette fonction doit être appellée en fin de simulation.
        
        Paramètres
        ----------
        Aucun

        Renvoie
        -------
        Rien  
        """
        plt.title("Evolution de la population d'animaux")
        plots = plt.plot(range(self.nbtour), self.population)
        plt.xlabel("Tour de jeu")
        plt.ylabel("Nombre d'individus")
        plt.legend(plots, ("Fourmis", "Cigales", "Mogwai / Gremlins"))
        plt.show()

if __name__ == "__main__":
    nbins = 120
    nbtour = 60
    ecosys = Ecosysteme(nbins,nbtour,40,80)
    print(ecosys)
    ecosys.simuler()
    ecosys.statistiques()
