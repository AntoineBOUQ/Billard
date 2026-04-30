# jeu.py
from table import Table
from joueur import Joueur
from stockage import Stockage
import random

class Jeu:
    def __init__(self, nom_joueur1: str, nom_joueur2: str):
        self.table = Table()
        self.joueurs = [Joueur(nom_joueur1), Joueur(nom_joueur2)]
        self.tour_actuel =random.randint(0,1)       # index 0 ou 1
        self.nb_coups = 0
        self.gagnant = None
        self.stockage = Stockage()
        self._distribuer_billes()

    def _distribuer_billes(self):
        billes_numerotees = self.table.billes[1:]  # on exclut la blanche
        self.joueurs[0].billes_a_empocher = billes_numerotees[:7]
        self.joueurs[1].billes_a_empocher = billes_numerotees[7:14]

    def joueur_actuel(self): #retourne le joueur dont c'est le tour
        return self.joueurs[self.tour_actuel]

    def jouer_coup(self, angle, force):
        joueur = self.joueur_actuel() # assigne le joueur sous forme de classe joueur
        bille_blanche = self.table.get_bille_blanche() #assigne à Bille blanche la première bille de la liste
        joueur.jouer_coup(bille_blanche, angle, force)
        self.nb_coups += 1


    def mettre_a_jour(self):
        self.table.deplacer_toutes_billes()
        self.table.detecter_collisions()

        # Quand tout s'arrête, on passe au joueur suivant
        if self.table.est_arretee():
            self._verifier_victoire()
            self._changer_tour()

    def nb_bille_rentre(self):
        return self.table._nb_bille_rentre()

    def _changer_tour(self):
        """Passe au joueur suivant."""
        self.tour_actuel = 1 - self.tour_actuel  # alterne entre 0 et 1


    def _verifier_victoire(self):
        """Vérifie si un joueur a gagné."""
        for joueur in self.joueurs:
            if joueur.a_gagne():
                self.gagnant = joueur

    def est_termine(self):
        """Retourne True si la partie est finie."""
        return self.gagnant is not None

    def sauvegarder(self):
        """Sauvegarde l'état actuel de la partie."""
        self.stockage.sauvegarder_etat(self)