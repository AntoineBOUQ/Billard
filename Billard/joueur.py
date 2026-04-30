# joueur.py
from queue import Queue
from bille import BilleNumerotee

class Joueur:
    def __init__(self, nom: str):
        self.nom = nom
        self.score = 0
        self.queue = Queue()
        self.billes_a_empocher = []  # liste des billes assignées au joueur
        self.nb_coups = 0

    def jouer_coup(self, bille_blanche, angle: float, force: float):
        self.queue.viser(angle) #la queue vise d'un angle 'angle'
        self.queue.frapper(bille_blanche, force)
        self.nb_coups += 1 #nb de coup associer au joueur

    def ajouter_point(self):
        """Incrémente le score du joueur d'un point."""
        self.score += 1

    def a_gagne(self) -> bool:
        return all(b.empochee for b in self.billes_a_empocher)

    def __str__(self):
        return f"Joueur {self.nom} — score: {self.score}, coups: {self.nb_coups}"