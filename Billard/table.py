# table.py
from bille import Bille, BilleBlanche, BilleNumerotee

class Table:
    """
    Représente le tapis de billard.
    Gère les billes, les collisions et les trous.
    """

    # Positions des 6 trous (coins + milieu des grands côtés)
    TROUS = [
        (0, 0), (400, 0), (800, 0),
        (0, 500), (400, 500), (800, 500)
    ]
    RAYON_TROU = 20.0

    def __init__(self, largeur: float = 800.0, hauteur: float = 500.0):
        """
        Args:
            largeur: largeur de la table en pixels
            hauteur: hauteur de la table en pixels
        """
        self.largeur = largeur
        self.hauteur = hauteur
        self.billes = []
        self._initialiser_billes()

    def _initialiser_billes(self):
        """Place la bille blanche et les 15 billes numérotées."""
        # Bille blanche
        self.billes.append(BilleBlanche(200, 250))

        # Couleurs des billes 1 à 15
        couleurs = [
            "jaune", "bleu", "rouge", "violet", "orange",
            "vert", "marron", "noir",
            "jaune_rayé", "bleu_rayé", "rouge_rayé", "violet_rayé",
            "orange_rayé", "vert_rayé", "marron_rayé"
        ]

        # Disposition en triangle côté droit
        positions = self._calculer_positions_triangle(600, 250)
        for i, (x, y) in enumerate(positions):
            self.billes.append(
                BilleNumerotee(x, y, i + 1, couleurs[i])
            )

    def _calculer_positions_triangle(self, x_depart: float, y_centre: float):
        """
        Calcule les positions en triangle pour les 15 billes.

        Args:
            x_depart: position x du sommet du triangle
            y_centre: position y du centre
        Returns:
            liste de tuples (x, y)
        """
        positions = []
        espacement = 22  # légèrement plus grand que le diamètre
        rangees = [1, 2, 3, 4, 5]  # 1+2+3+4+5 = 15 billes

        for rang, nb in enumerate(rangees):
            x = x_depart + rang * espacement
            y_debut = y_centre - (nb - 1) * espacement / 2
            for i in range(nb):
                positions.append((x, y_debut + i * espacement))

        return positions

    def deplacer_toutes_billes(self):
        """Déplace toutes les billes selon leur vitesse."""
        for bille in self.billes:
            if not bille.empochee:
                bille.deplacer()
                self._rebondir_bords(bille)
                self._verifier_trou(bille)

    def _rebondir_bords(self, bille: Bille):
        """
        Fait rebondir une bille sur les bords de la table.

        Args:
            bille: la bille à vérifier
        """
        if bille.x - bille.rayon <= 0:
            bille.x = bille.rayon
            bille.vitesse_x *= -1
        elif bille.x + bille.rayon >= self.largeur:
            bille.x = self.largeur - bille.rayon
            bille.vitesse_x *= -1

        if bille.y - bille.rayon <= 0:
            bille.y = bille.rayon
            bille.vitesse_y *= -1
        elif bille.y + bille.rayon >= self.hauteur:
            bille.y = self.hauteur - bille.rayon
            bille.vitesse_y *= -1

    def _verifier_trou(self, bille: Bille):
        """
        Vérifie si une bille est tombée dans un trou.

        Args:
            bille: la bille à vérifier
        """
        for (tx, ty) in self.TROUS:
            distance = ((bille.x - tx) ** 2 + (bille.y - ty) ** 2) ** 0.5
            if distance < self.RAYON_TROU:
                bille.empochee = True
                bille.vitesse_x = 0.0
                bille.vitesse_y = 0.0

    def detecter_collisions(self):
        """Détecte et gère les collisions entre toutes les billes."""
        for i in range(len(self.billes)):
            for j in range(i + 1, len(self.billes)):
                b1 = self.billes[i]
                b2 = self.billes[j]
                if not b1.empochee and not b2.empochee:
                    self._resoudre_collision(b1, b2)

    def _resoudre_collision(self, b1: Bille, b2: Bille):
        """
        Résout la collision entre deux billes (échange de vitesses simplifié).

        Args:
            b1, b2: les deux billes en collision
        """
        dx = b2.x - b1.x
        dy = b2.y - b1.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance < b1.rayon + b2.rayon and distance > 0:
            # Échange des vitesses (collision élastique simplifiée)
            b1.vitesse_x, b2.vitesse_x = b2.vitesse_x, b1.vitesse_x
            b1.vitesse_y, b2.vitesse_y = b2.vitesse_y, b1.vitesse_y

            # Séparation pour éviter le chevauchement
            overlap = (b1.rayon + b2.rayon - distance) / 2
            b1.x -= overlap * dx / distance
            b1.y -= overlap * dy / distance
            b2.x += overlap * dx / distance
            b2.y += overlap * dy / distance

    def est_arretee(self) -> bool:
        """
        Vérifie si toutes les billes sont immobiles.

        Returns:
            True si aucune bille ne bouge
        """
        return all(not b.est_en_mouvement() for b in self.billes
                   if not b.empochee)

    def get_bille_blanche(self) -> BilleBlanche:
        """Retourne la bille blanche."""
        return self.billes[0]