# joueur.py
from queue import Queue
from bille import BilleNumerotee

class Joueur:
    """
    Représente un joueur de billard.
    Gère le score, les billes à empocher et les coups joués.
    """

    def __init__(self, nom: str):
        """
        Args:
            nom: prénom ou pseudo du joueur
        """
        self.nom = nom
        self.score = 0
        self.queue = Queue()
        self.billes_a_empocher = []  # liste des billes assignées au joueur
        self.nb_coups = 0

    def jouer_coup(self, bille_blanche, angle: float, force: float):
        """
        Le joueur vise et frappe la bille blanche.

        Args:
            bille_blanche: la BilleBlanche de la table
            angle: angle visé en radians
            force: force du coup (0.0 à 1.0)
        """
        self.queue.viser(angle)
        self.queue.frapper(bille_blanche, force)
        self.nb_coups += 1

    def ajouter_point(self):
        """Incrémente le score du joueur d'un point."""
        self.score += 1

    def a_gagne(self) -> bool:
        """
        Vérifie si le joueur a empoché toutes ses billes.

        Returns:
            True si toutes ses billes sont empochées
        """
        return all(b.empochee for b in self.billes_a_empocher)

    def __str__(self):
        return f"Joueur {self.nom} — score: {self.score}, coups: {self.nb_coups}"