# jeu.py
from table import Table
from joueur import Joueur
from stockage import Stockage

class Jeu:
    """
    Classe principale qui orchestre la partie de billard.
    Gère le tour par tour et les conditions de victoire.
    """

    def __init__(self, nom_joueur1: str, nom_joueur2: str):
        self.table = Table()
        self.joueurs = [Joueur(nom_joueur1), Joueur(nom_joueur2)]
        self.tour_actuel = 0       # index 0 ou 1
        self.nb_coups = 0
        self.gagnant = None
        self.stockage = Stockage()
        self._distribuer_billes()

    def _distribuer_billes(self):
        """
        Distribue les billes aux joueurs :
        joueur 1 → billes 1 à 7, joueur 2 → billes 9 à 15.
        La bille 8 (noire) est pour celui qui finit en dernier.
        """
        billes_numerotees = self.table.billes[1:]  # on exclut la blanche
        self.joueurs[0].billes_a_empocher = billes_numerotees[:7]
        self.joueurs[1].billes_a_empocher = billes_numerotees[7:14]

    def joueur_actuel(self) -> Joueur:
        """Retourne le joueur dont c'est le tour."""
        return self.joueurs[self.tour_actuel]

    def jouer_coup(self, angle: float, force: float):
        """
        Le joueur actuel joue son coup.

        Args:
            angle: angle du tir en radians
            force: force du tir (0.0 à 1.0)
        """
        joueur = self.joueur_actuel()
        bille_blanche = self.table.get_bille_blanche()
        joueur.jouer_coup(bille_blanche, angle, force)
        self.nb_coups += 1

    def mettre_a_jour(self):
        """
        Met à jour la physique à chaque frame.
        À appeler dans la boucle de jeu PyQt5.
        """
        self.table.deplacer_toutes_billes()
        self.table.detecter_collisions()

        # Quand tout s'arrête, on passe au joueur suivant
        if self.table.est_arretee():
            self._verifier_victoire()
            self._changer_tour()

    def _changer_tour(self):
        """Passe au joueur suivant."""
        self.tour_actuel = 1 - self.tour_actuel  # alterne entre 0 et 1

    def _verifier_victoire(self):
        """Vérifie si un joueur a gagné."""
        for joueur in self.joueurs:
            if joueur.a_gagne():
                self.gagnant = joueur

    def est_termine(self) -> bool:
        """Retourne True si la partie est finie."""
        return self.gagnant is not None

    def sauvegarder(self):
        """Sauvegarde l'état actuel de la partie."""
        self.stockage.sauvegarder_etat(self)