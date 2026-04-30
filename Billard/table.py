# table.py
from bille import Bille, BilleBlanche, BilleNumerotee

class Table:

    TROUS = [
        (0, 0), (4000, 0), (8000, 0),
        (0, 5000), (4000, 5000), (8000, 5000)
    ]
    RAYON_TROU = 200.0

    def __init__(self, largeur: float = 8000.0, hauteur: float = 5000.0):
        self.largeur = largeur
        self.hauteur = hauteur
        self.billes = []
        self._initialiser_billes()
        self.nb_bille_rentre=0



    def _initialiser_billes(self):
        """Place la bille blanche et les 15 billes numérotées."""
        # Bille blanche
        self.billes.append(BilleBlanche(2000, 2500))

        couleurs = [
            "jaune", "bleu", "rouge", "violet", "orange",
            "vert", "marron", "noir",
            "jaune_rayé", "bleu_rayé", "rouge_rayé", "violet_rayé",
            "orange_rayé", "vert_rayé", "marron_rayé"
        ]

        # Disposition en triangle côté droit
        positions = self._calculer_positions_triangle(6000, 2500)
        for i, (x, y) in enumerate(positions):
            self.billes.append(
                BilleNumerotee(x, y, i + 1, couleurs[i])
            )

    def _calculer_positions_triangle(self, x_depart: float, y_centre: float):
        positions = []
        espacement = 21
        rangees = [1, 2, 3, 4, 5]

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

    def _nb_bille_rentre(self):
        return self.nb_bille_rentre


    def _rebondir_bords(self, bille: Bille):
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

        for (tx, ty) in self.TROUS:
            distance = ((bille.x - tx) ** 2 + (bille.y - ty) ** 2) ** 0.5
            if distance < self.RAYON_TROU:
                self.nb_bille_rentre += 1
                bille.empochee = True
                bille.vitesse_x = 0.0
                bille.vitesse_y = 0.0




    def detecter_collisions(self):
        for i in range(len(self.billes)):
            for j in range(i + 1, len(self.billes)):
                b1 = self.billes[i]
                b2 = self.billes[j]
                if not b1.empochee and not b2.empochee:
                    self._resoudre_collision(b1, b2)

    def _resoudre_collision(self, b1: Bille, b2: Bille):
        dx = b2.x - b1.x
        dy = b2.y - b1.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance < b1.rayon + b2.rayon and distance > 0:
            # Échange des vitesses
            b1.vitesse_x, b2.vitesse_x = b2.vitesse_x, b1.vitesse_x
            b1.vitesse_y, b2.vitesse_y = b2.vitesse_y, b1.vitesse_y

            # Séparation pour éviter le chevauchement
            overlap = (b1.rayon + b2.rayon - distance) / 2
            b1.x -= overlap * dx / distance
            b1.y -= overlap * dy / distance
            b2.x += overlap * dx / distance
            b2.y += overlap * dy / distance

    def est_arretee(self) -> bool:
        return all(not b.est_en_mouvement() for b in self.billes
                   if not b.empochee)

    def get_bille_blanche(self) -> BilleBlanche:
        """Retourne la bille blanche."""
        return self.billes[0]