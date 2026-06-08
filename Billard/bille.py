class Bille:
    """
    Classe mère représentant une bille de billard.
    """

    #___Initialisation___
    def __init__(self, x: float, y: float, rayon: float = 12.0):
        self.x = x                  # position horizontale (coordonnées logiques 0..800)
        self.y = y                  # position verticale (coordonnées logiques 0..500)
        self.rayon = rayon          # rayon en pixels logiques
        self.vitesse_x = 0.0        # composante horizontale de la vitesse
        self.vitesse_y = 0.0        # composante verticale de la vitesse
        self.empochee = False       # passe à True quand la bille tombe dans un trou

    #___Déplacement d'une frame avec frottement (conservé pour compatibilité)___
    def deplacer(self):
        # Avance d'un pas complet puis applique le frottement
        self.avancer(1.0)
        self.appliquer_frottement()

    #___Avance (éventuellement fractionnée) SANS frottement — pour les sous-pas___
    def avancer(self, fraction=1.0):
        self.x += self.vitesse_x * fraction
        self.y += self.vitesse_y * fraction

    #___Applique le frottement (une seule fois par frame)___
    def appliquer_frottement(self):
        # À chaque image, on perd 2% de la vitesse
        frottement = 0.98
        self.vitesse_x *= frottement
        self.vitesse_y *= frottement
        # Quand la vitesse devient très faible, on l'arrête
        # (sinon le frottement multiplicatif n'atteindrait jamais 0)
        if abs(self.vitesse_x) < 0.01:
            self.vitesse_x = 0.0
        if abs(self.vitesse_y) < 0.01:
            self.vitesse_y = 0.0

    #___Vérification de mouvement___
    def est_en_mouvement(self) -> bool:
        # Renvoie True si la bille a encore une vitesse non nulle
        return self.vitesse_x != 0.0 or self.vitesse_y != 0.0


class BilleBlanche(Bille):
    """Classe fille de Bille, représente la bille blanche."""

    #___Initialisation___
    def __init__(self, x: float, y: float):
        super().__init__(x, y)      # on appelle l'init de la classe mère
        self.est_jouable = True     # propre à la blanche

    #___Remise en jeu après un scratch___
    def reinitialiser(self, x: float, y: float):
        # Replace la blanche à la position donnée, vitesse nulle, plus empochée
        self.x = x
        self.y = y
        self.vitesse_x = 0.0
        self.vitesse_y = 0.0
        self.empochee = False



class BilleNumerotee(Bille):
    """
    Classe fille de Bille, représente une bille numérotée (1 à 15).
    """

    #___Initialisation___
    def __init__(self, x: float, y: float, numero: int, couleur: str):
        super().__init__(x, y)
        self.numero = numero        # numéro 1..15
        self.couleur = couleur      # nom textuel de la couleur