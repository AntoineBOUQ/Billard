from bille import Bille, BilleBlanche, BilleNumerotee


class Table:
    #___Paramètres géométriques de la table___
    BISEAU = 50.0               # longueur du biseau le long de chaque bord (aux coins)
    RAYON_TROU_COIN = 22.0      # rayon d'empochage des poches de coin
    RAYON_TROU_MILIEU = 22.0    # rayon d'empochage des poches du milieu

    #___Initialisation___
    def __init__(self, largeur: float = 800.0, hauteur: float = 500.0):
        self.largeur = largeur
        self.hauteur = hauteur
        self.billes = []        # liste de toutes les billes du jeu

        # Géométrie calculée à partir des dimensions (poches + bandes)
        self.trous = self._calculer_trous()
        self.bandes = self._calculer_bandes()

        # Couleurs RGB de chaque bille
        self.billes_couleur = [
            [255, 255, 255], [255, 255, 0], [0, 0, 255], [255, 0, 0],
            [127, 0, 255], [244, 102, 27], [0, 255, 0], [109, 7, 26], [0, 0, 0],
            [255, 255, 0], [0, 0, 255], [255, 0, 0],
            [127, 0, 255], [244, 102, 27], [0, 255, 0], [109, 7, 26]
        ]
        self._initialiser_billes()      # crée les 16 billes
        self.nb_bille_rentre = 0        # compteur de billes numérotées empochées

    #___Position des 6 poches (x, y, rayon d'empochage)___
    def _calculer_trous(self):
        W, H, b = self.largeur, self.hauteur, self.BISEAU
        rc, rm = self.RAYON_TROU_COIN, self.RAYON_TROU_MILIEU
        # Les poches de coin sont placées au milieu du biseau (et non plus dans l'angle)
        return [
            (b / 2,      b / 2,      rc),   # coin haut-gauche
            (W - b / 2,  b / 2,      rc),   # coin haut-droit
            (b / 2,      H - b / 2,  rc),   # coin bas-gauche
            (W - b / 2,  H - b / 2,  rc),   # coin bas-droit
            (W / 2,      0.0,        rm),   # milieu haut
            (W / 2,      H,          rm),   # milieu bas
        ]

    #___Liste des bandes (segments sur lesquels les billes rebondissent)___
    def _calculer_bandes(self):
        W, H, b = self.largeur, self.hauteur, self.BISEAU
        return [
            # Bandes droites (raccourcies pour laisser la place aux biseaux)
            ((b, 0), (W - b, 0)),          # bande haute
            ((b, H), (W - b, H)),          # bande basse
            ((0, b), (0, H - b)),          # bande gauche
            ((W, b), (W, H - b)),          # bande droite
            # Biseaux des 4 coins (les "petites bandes" en diagonale)
            ((b, 0), (0, b)),              # haut-gauche
            ((W - b, 0), (W, b)),          # haut-droit
            ((0, H - b), (b, H)),          # bas-gauche
            ((W, H - b), (W - b, H)),      # bas-droit
        ]

    #___Création des billes___
    def _initialiser_billes(self):
        # La blanche est placée à gauche, sur la ligne de service
        self.billes.append(BilleBlanche(200, 250))

        couleurs = [
            "jaune", "bleu", "rouge", "violet", "orange",
            "vert", "marron", "noir",
            "jaune_rayé", "bleu_rayé", "rouge_rayé", "violet_rayé",
            "orange_rayé", "vert_rayé", "marron_rayé"
        ]

        # Calcul du triangle de billes côté droit
        positions = self._calculer_positions_triangle(600, 250)
        for i, (x, y) in enumerate(positions):
            self.billes.append(BilleNumerotee(x, y, i + 1, couleurs[i]))

    #___Calcul des positions du triangle de départ___
    def _calculer_positions_triangle(self, x_depart: float, y_centre: float):
        positions = []
        espacement = 21         # distance entre centres de billes
        rangees = [1, 2, 3, 4, 5]   # 1 bille en rang 0, 2 en rang 1, etc.

        for rang, nb in enumerate(rangees):
            x = x_depart + rang * espacement
            # Centre verticalement la rangée
            y_debut = y_centre - (nb - 1) * espacement / 2
            for i in range(nb):
                positions.append((x, y_debut + i * espacement))

        return positions

    #___Mise à jour physique d'une frame___
    def deplacer_toutes_billes(self):
        """Déplace toutes les billes selon leur vitesse."""
        for bille in self.billes:
            if not bille.empochee:                  # on ignore les billes déjà sorties
                bille.deplacer()                    # mouvement et frottement
                self._verifier_trou(bille)          # 1. empochage (PRIORITAIRE)
                if not bille.empochee:
                    self._rebondir_sur_bandes(bille)  # 2. rebonds (bords + biseaux)

    #___Accesseur du compteur___
    def _nb_bille_rentre(self):
        return self.nb_bille_rentre

    #___Rebonds sur toutes les bandes (bords droits + biseaux)___
    def _rebondir_sur_bandes(self, bille: Bille):
        for (p1, p2) in self.bandes:
            self._rebond_segment(bille, p1, p2)

    #___Rebond d'une bille sur un segment de bande quelconque___
    def _rebond_segment(self, bille: Bille, p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        # Vecteur directeur du segment
        dx = x2 - x1
        dy = y2 - y1
        longueur2 = dx * dx + dy * dy
        if longueur2 == 0:
            return

        # Projection du centre de la bille sur le segment (t borné entre 0 et 1)
        t = ((bille.x - x1) * dx + (bille.y - y1) * dy) / longueur2
        t = max(0.0, min(1.0, t))

        # Point du segment le plus proche de la bille
        px = x1 + t * dx
        py = y1 + t * dy

        # Distance bille ↔ segment
        ecart_x = bille.x - px
        ecart_y = bille.y - py
        distance = (ecart_x ** 2 + ecart_y ** 2) ** 0.5

        # Collision si la bille touche la bande
        if 0 < distance < bille.rayon:
            # Normale unitaire (du point de contact vers le centre de la bille)
            nx = ecart_x / distance
            ny = ecart_y / distance

            # On replace la bille pour qu'elle ne traverse pas la bande
            chevauchement = bille.rayon - distance
            bille.x += nx * chevauchement
            bille.y += ny * chevauchement

            # Réflexion de la vitesse : v' = v - 2 (v·n) n
            produit = bille.vitesse_x * nx + bille.vitesse_y * ny
            if produit < 0:     # seulement si la bille fonce vers la bande
                bille.vitesse_x -= 2 * produit * nx
                bille.vitesse_y -= 2 * produit * ny

    #___Vérifier si une bille tombe dans une poche___
    def _verifier_trou(self, bille):
        for (tx, ty, rayon) in self.trous:
            # Distance euclidienne entre la bille et le trou
            distance = ((bille.x - tx) ** 2 + (bille.y - ty) ** 2) ** 0.5
            if distance < rayon:
                bille.empochee = True
                bille.vitesse_x = 0.0
                bille.vitesse_y = 0.0
                # Seules les billes numérotées comptent dans le compteur
                if not isinstance(bille, BilleBlanche):
                    self.nb_bille_rentre += 1
                return

    #___Détection de toutes les collisions entre billes___
    def detecter_collisions(self):
        for i in range(len(self.billes)):
            for j in range(i + 1, len(self.billes)):
                b1 = self.billes[i]
                b2 = self.billes[j]
                if not b1.empochee and not b2.empochee:
                    self._resoudre_collision(b1, b2)

    #___Résolution d'une collision entre deux billes___
    def _resoudre_collision(self, b1: Bille, b2: Bille):
        # Vecteur de b1 vers b2
        dx = b2.x - b1.x
        dy = b2.y - b1.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance >= b1.rayon + b2.rayon or distance == 0:
            return

        # Vecteur normal (de b1 vers b2, normalisé)
        nx = dx / distance
        ny = dy / distance

        # Vecteur tangentiel (perpendiculaire à la normale)
        tx = -ny
        ty = nx

        # Projection des vitesses sur les axes normal et tangentiel
        v1n = b1.vitesse_x * nx + b1.vitesse_y * ny
        v1t = b1.vitesse_x * tx + b1.vitesse_y * ty
        v2n = b2.vitesse_x * nx + b2.vitesse_y * ny
        v2t = b2.vitesse_x * tx + b2.vitesse_y * ty

        # Si les billes s'éloignent déjà, on ne fait rien
        if v1n - v2n <= 0:
            return

        # Échange des vitesses normales (collision élastique masses égales)
        nouvelle_v1n = v2n
        nouvelle_v2n = v1n

        # Coefficient de restitution (perte d'énergie au choc)
        restitution = 0.99
        nouvelle_v1n *= restitution
        nouvelle_v2n *= restitution

        # Reconstruction des vitesses cartésiennes
        b1.vitesse_x = nouvelle_v1n * nx + v1t * tx
        b1.vitesse_y = nouvelle_v1n * ny + v1t * ty
        b2.vitesse_x = nouvelle_v2n * nx + v2t * tx
        b2.vitesse_y = nouvelle_v2n * ny + v2t * ty

        # Séparation pour éviter le chevauchement résiduel
        overlap = (b1.rayon + b2.rayon - distance) / 2
        b1.x -= overlap * nx
        b1.y -= overlap * ny
        b2.x += overlap * nx
        b2.y += overlap * ny

    #___Vérification d'arrêt complet___
    def est_arretee(self) -> bool:
        return all(not b.est_en_mouvement()
                   for b in self.billes if not b.empochee)

    #___Accesseur de la bille blanche___
    def get_bille_blanche(self) -> BilleBlanche:
        return self.billes[0]