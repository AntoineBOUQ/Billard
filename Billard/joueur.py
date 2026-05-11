
from queue import Queue


class Joueur:

    #___Initialisation___
    def __init__(self, nom: str):
        self.nom = nom                  # nom affiché à l'écran
        self.score = 0                  # nombre de billes empochées
        self.queue = Queue()            # chaque joueur a sa queue
        self.billes_a_empocher = []     # liste des billes assignées (pleines ou rayées)
        self.nb_coups = 0               # nombre de coups joués par ce joueur

    #___Le joueur joue un coup___
    def jouer_coup(self, bille_blanche, angle: float, force: float):
        self.queue.viser(angle)                 # la queue mémorise l'angle
        self.queue.frapper(bille_blanche, force)# la queue frappe la blanche
        self.nb_coups += 1                      # incrémentation du compteur

    #___Incrémente le score___
    def ajouter_point(self):
        self.score += 1

    #___Vérifie si le joueur a empoché toutes ses billes___
    def a_gagne(self) -> bool:
        # Renvoie True si toutes les billes assignées au joueur sont empochées
        return all(b.empochee for b in self.billes_a_empocher)
