# -*- coding: utf-8 -*-
"""
Module implémentant les différents terrains utilisés lors de la simulation
d'un écosytème.
"""

from abc import ABC, abstractmethod
import random as rnd
from dprint import dprint

class Terrain(ABC):
    """
    Créé un case de type Terrain et la rattache à l'écosystème passé en 
    paramètres

    Paramètres
    ----------
    ecosysteme: Ecosysteme
        L'instance d'Ecosysteme gérant la simulation à laquelle le terrain va
        se rattacher.
        
    coords: tuple
        Abscisse et ordonnée de la case dans la simulation
        
    Notes
    -----
    La classe Terrain étant abstraite ce sont ses classes filles qui doivent
    être instanciées.
    """
    
    def __init__(self, ecosysteme, coords):
        self._ecosysteme = ecosysteme
        self.__coords = coords
        self.impact_sante = self.Impact_sante_defaut
            
    @property
    def impact_sante(self):
        """
        impact_sante: float
            Chaque terrain modifie, en positif ou négatif, la santé de l'animal
            qui se trouve dessus suivant la règle suivante:
            'sante_animal += impact_sante''            
        """
        return self.__impact_sante
        
    @impact_sante.setter    
    def impact_sante(self, impact_sante):
        self.__impact_sante = impact_sante

    @property
    def coords(self):
        """      
        coords: tuple
            les coordonnées de la case dans la simulation en cours.

        Notes
        -----
        Cet attribut est en lecture seule, les coordonnées d'un terrain
        n'ont pas vocation à être modifiées en cours de simulation. Si
        besoin il faut instancier un nouveau terrain pour remplacer
        l'ancien.
        """
        return self.__coords
        
    @abstractmethod
    def action(self, animal):
        """
        Lorsqu'un animal se positionne sur un terrain ce dernier peut avoir
        une influence sur l'animal en question.
        
        Paramètres
        ----------
        animal: Animal
            l'animal qui viste la case courante
            
        Renvoie
        -------
        Rien
        """
        pass
    
    @abstractmethod
    def maj(self):
        """
        Permet de gérer l'évolution du type de terrain en fonction de l'état
        de la simulation
        
        Paramètres
        ----------
        Aucun
        
        Renvoie
        -------
        Rien
        """
        pass
    
    @abstractmethod
    def code_couleur(self):
        """
        Code couleur du terrain pour l'affichage en mode texte
        
        Paramètres
        ----------
        Aucun
        
        Renvoie
        -------
        code_couleur: string
            Le code couleur du terrain exprimé sous forme de séquence 
            d'échappement bash
            
        Notes
        -----
            Il revient à l'utilisateur de mettre fin au formatage à la
            fin de la chaîne de caractères qu'il construit en utilisant le code
            d'échappement ``\x1b[0m``.
        """
        pass

class Savane(Terrain):
    """
    Les cases ''Savane'' ont vocation à constituer la majorité du terrain de
    départ. Chaque animal qui visite une case ''Savane'' perdra un point de
    vie, sauf si cette case a été modifiée par un ''Marais'' environnant. 
    Voir règle spécifique dans la documentation de ''propage_danger'' de la
    classe ''Marais''.
    """
    Impact_sante_defaut = -1
    def action(self, animal):
        """

        """
        animal.sante += self.impact_sante

    def maj(self):
        """
        Voir documentation dans la super classe.
        Une case de type ''Savane'' devient ''Nourriture'' quand cette methode
        est appellée
        """
        
        x,y = self.coords
        dprint("La case "+str(self.coords)+" devient de la nourriture")
        self._ecosysteme.plateau[x, y, self._ecosysteme.Couche_terrain] = \
                            Nourriture(self._ecosysteme, self.coords)                   
    def code_couleur(self):
        return "\x1b[43;31m"
        
class Marais(Terrain):
    """
    Les ''Marais'' font perdre trois points de vie à chaque animal qui les
    visite. De plus ils influencent les cases voisines en y dégradant les
    conditions de vie.
    """
    Impact_sante_defaut = -3
    def action(self, animal):
        animal.sante += self.impact_sante
    
    def maj(self):
        """
        Voir documentation dans la super classe.
        Les cases ''Marais'' n'évoluent jamais.
        """
        pass
    
    def propage_danger(self, rayon_danger=1):
        """
        Propage le danger de la case courante dans un rayon de ''rayon_danger''
        en rajoutant la moitié du malus des marais sur les cases voisines.
        
        Arguments
        ---------
        rayon_danger: int, optionnel
            Rayon de propagation du malus. Valeur par défaut 1.
            
        Renvoie
        -------
        Rien.
        
        Notes
        -----
        Une case de ''Nourriture'' peut devenir une case dangereuse si elle est
        à proximité d'une case ''Marais''.
        Utiliser cette fonction sur un ecosystème dont la couche terrain n'est
        pas complètement initialisée est fortement déconseillé.
        Une case ''Marais'' ne rend pas un ''Marais'' voisin plus dangereux, de
        même une case d'un autre type entourée de plusieurs ''Marais'' ne 
        subira l'influence que d'un seul ''Marais''.
        """
        x, y = self.coords
        danger_x = (max(0, x-rayon_danger), 
                        min(self._ecosysteme.dims[0], x+rayon_danger+1))
        danger_y = (max(0, y-rayon_danger), 
                    min(self._ecosysteme.dims[1], y+rayon_danger+1))
                    
        cases_dangereuses = self._ecosysteme.plateau[danger_x[0]:danger_x[1],
                                danger_y[0]:danger_y[1],
                                self._ecosysteme.Couche_terrain]
        
        # flatten fait une copie, reshape(-1) une view
        # nditer semble casse gueule sur un array object
        # sinon double boucle
        for c in cases_dangereuses.reshape(-1):
            if c is not self and not c.impact_sante == c.Impact_sante_defaut\
                and type(c) is not Marais:
                c.marque_danger = True
                c.impact_sante += self.Impact_sante_defaut//2
        
    def code_couleur(self):
        return "\x1b[100;31m"
        
class Nourriture(Terrain):
    """
    Une case ''Nourriture'' permet à chaque animal qui la visite de
    retrouver trois points de santé, sauf si des ''Marais'' environnants ont
    dégradé cette case''
    """
    Impact_sante_defaut = +3
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__stock = rnd.randint(1,10)
        
    def action(self, animal):
        if self.__stock:
            self.__stock -= 1
            animal.sante += self.impact_sante
        else:
            self._ecosysteme.cases_besoin_maj.append(self.coords)
            dprint("une case nourriture vidée par " + str(animal))
        
    def maj(self):
        x,y = self.coords
        self._ecosysteme.plateau[x, y, self._ecosysteme.Couche_terrain] = \
                            Savane(self._ecosysteme, self.coords)
    def code_couleur(self):
        return "\x1b[102;31m"