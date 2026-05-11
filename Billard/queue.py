
import math
from bille import BilleBlanche


class Queue:
    """
    Représente la queue (canne) du joueur. Calcule la force et la direction du coup.
    """

    #___Initialisation___
    def __init__(self):
        self.longueur = 150.0       # longueur visuelle (pour un éventuel affichage)
        self.angle = 0.0            # angle de visée en radians
        self.force_max = 20.0       # vitesse maximale qu'on peut imprimer à la blanche

    #___Mémoriser la direction de visée___
    def viser(self, angle: float):
        self.angle = angle

    #___Appliquer le coup___
    def frapper(self, bille: BilleBlanche, force: float):
        # On borne la force entre 0 et 1 (sécurité)
        force = max(0.0, min(1.0, force))
        # La force entre 0 et 1 est convertie en vitesse réelle
        puissance = force * self.force_max

        # Décomposition en vitesses x et y selon l'angle de visée
        bille.vitesse_x = math.cos(self.angle) * puissance
        bille.vitesse_y = math.sin(self.angle) * puissance
