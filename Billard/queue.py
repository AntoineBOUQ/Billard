# queue.py
import math
from bille import BilleBlanche

class Queue:
    """
    Représente la queue (canne) du joueur.
    Calcule la force et la direction du coup.
    """

    def __init__(self):
        self.longueur = 150.0   # en pixels
        self.masse = 0.5        # en kg (pour calculs physiques futurs)
        self.angle = 0.0        # angle en radians
        self.force_max = 20.0   # force maximale d'un coup

    def viser(self, angle: float):
        """
        Oriente la queue selon un angle.

        Args:
            angle: angle en radians
        """
        self.angle = angle

    def frapper(self, bille: BilleBlanche, force: float):
        """
        Frappe la bille blanche avec une force donnée.
        Convertit la force et l'angle en vitesse x/y.

        Args:
            bille: la bille blanche à frapper
            force: intensité du coup (entre 0.0 et 1.0)
        """
        # On limite la force entre 0 et 1
        force = max(0.0, min(1.0, force))
        puissance = force * self.force_max

        # Décomposition en vitesses x et y selon l'angle
        bille.vitesse_x = math.cos(self.angle) * puissance
        bille.vitesse_y = math.sin(self.angle) * puissance

    def __str__(self):
        angle_degres = math.degrees(self.angle)
        return f"Queue — angle: {angle_degres:.1f}°, force max: {self.force_max}"