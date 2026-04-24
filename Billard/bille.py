# bille.py

class Bille:
    """
    Classe mère représentant une bille de billard.
    Contient les attributs et comportements communs à toutes les billes.
    """

    def __init__(self, x: float, y: float, rayon: float = 10.0):
        """
        Initialise une bille avec sa position et son rayon.

        Args:
            x: position horizontale (en pixels)
            y: position verticale (en pixels)
            rayon: rayon de la bille (par défaut 10.0)
        """
        self.x = x
        self.y = y
        self.rayon = rayon
        self.vitesse_x = 0.0
        self.vitesse_y = 0.0
        self.empochee = False

    def deplacer(self):
        """
        Met à jour la position selon la vitesse actuelle
        et applique un frottement pour ralentir progressivement.
        """
        self.x += self.vitesse_x
        self.y += self.vitesse_y

        frottement = 0.98
        self.vitesse_x *= frottement
        self.vitesse_y *= frottement

        if abs(self.vitesse_x) < 0.01:
            self.vitesse_x = 0.0
        if abs(self.vitesse_y) < 0.01:
            self.vitesse_y = 0.0

    def est_en_mouvement(self) -> bool:
        """
        Indique si la bille est encore en mouvement.

        Returns:
            True si la bille bouge encore
        """
        return self.vitesse_x != 0.0 or self.vitesse_y != 0.0

    def __str__(self) -> str:
        return f"Bille à ({self.x:.1f}, {self.y:.1f})"


class BilleBlanche(Bille):
    """
    La bille blanche, seule bille que le joueur peut frapper.
    Hérite de Bille.
    """

    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.est_jouable = True

    def reinitialiser(self, x: float, y: float):
        """
        Replace la bille blanche si elle a été empochée par erreur.

        Args:
            x: nouvelle position x
            y: nouvelle position y
        """
        self.x = x
        self.y = y
        self.vitesse_x = 0.0
        self.vitesse_y = 0.0
        self.empochee = False

    def __str__(self):
        return f"Bille blanche à ({self.x:.1f}, {self.y:.1f})"


class BilleNumerotee(Bille):
    """
    Une bille numérotée (1 à 15).
    Hérite de Bille et ajoute un numéro et une couleur.
    """

    def __init__(self, x: float, y: float, numero: int, couleur: str):
        """
        Args:
            numero: numéro de la bille (1 à 15)
            couleur: couleur de la bille (ex: "rouge", "jaune")
        """
        super().__init__(x, y)
        self.numero = numero
        self.couleur = couleur

    def __str__(self):
        return f"Bille n°{self.numero} ({self.couleur}) à ({self.x:.1f}, {self.y:.1f})"

