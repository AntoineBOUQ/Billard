
from bille import Bille, BilleBlanche, BilleNumerotee


class Table:
    # Position des 6 trous (en coordonnées logiques)
    TROUS = [(0, 0), (400, 0), (800, 0),
             (0, 500), (400, 500), (800, 500)]
    # Rayon d'attraction d'un trou : si une bille passe dans ce rayon, elle tombe
    RAYON_TROU = 20.0

    #___Initialisation___
    def __init__(self, largeur: float = 800.0, hauteur: float = 500.0):
        self.largeur = largeur
        self.hauteur = hauteur
        self.billes = []        # liste de toutes les billes du jeu

        # Couleurs RGB de chaque bille
        self.billes_couleur = [
            [255, 255, 255], [255, 255, 0], [0, 0, 255], [255, 0, 0],
            [127, 0, 255], [244, 102, 27], [0, 255, 0], [109, 7, 26], [0, 0, 0],
            [255, 255, 0], [0, 0, 255], [255, 0, 0],
            [127, 0, 255], [244, 102, 27], [0, 255, 0], [109, 7, 26]
        ]
        self._initialiser_billes()      # crée les 16 billes
        self.nb_bille_rentre = 0        # compteur de billes numérotées empochées

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
                self._rebondir_bords(bille)         # rebond sur les bords
                self._verifier_trou(bille)          # vérifie si elle tombe

    #___Accesseur du compteur___
    def _nb_bille_rentre(self):
        return self.nb_bille_rentre

    #___Rebonds sur les bords de la table___
    def _rebondir_bords(self, bille: Bille):
        # Bord gauche
        if bille.x - bille.rayon <= 0:
            bille.x = bille.rayon       # on recolle la bille au bord
            bille.vitesse_x *= -1       # on inverse la vitesse horizontale
        # Bord droit
        elif bille.x + bille.rayon >= self.largeur:
            bille.x = self.largeur - bille.rayon
            bille.vitesse_x *= -1

        # Bord haut
        if bille.y - bille.rayon <= 0:
            bille.y = bille.rayon
            bille.vitesse_y *= -1
        # Bord bas
        elif bille.y + bille.rayon >= self.hauteur:
            bille.y = self.hauteur - bille.rayon
            bille.vitesse_y *= -1

    #___Vérifier si une bille tombe dans un trou___
    def _verifier_trou(self, bille):
        for (tx, ty) in self.TROUS:
            # Distance euclidienne entre la bille et le trou
            distance = ((bille.x - tx) ** 2 + (bille.y - ty) ** 2) ** 0.5
            if distance < self.RAYON_TROU:
                bille.empochee = True
                bille.vitesse_x = 0.0
                bille.vitesse_y = 0.0
                # Seules les billes numérotées comptent dans le compteur
                # (la blanche, si elle tombe, sera repositionnée plus tard)
                if not isinstance(bille, BilleBlanche):
                    self.nb_bille_rentre += 1
                return

    #___Détection de toutes les collisions entre billes___
    def detecter_collisions(self):
        # Double boucle pour tester toutes les paires (i,j) avec i<j
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

        # Pas de collision (les billes ne se touchent pas)
        if distance >= b1.rayon + b2.rayon or distance == 0:
            return

        # Vecteur normal (de b1 vers b2, normalisé = longueur 1)
        nx = dx / distance
        ny = dy / distance

        # Vecteur tangentiel (perpendiculaire à la normale)
        tx = -ny
        ty = nx

        # Projection des vitesses sur les axes normal et tangentiel
        v1n = b1.vitesse_x * nx + b1.vitesse_y * ny     # vitesse de b1 selon la normale
        v1t = b1.vitesse_x * tx + b1.vitesse_y * ty     # vitesse de b1 selon la tangente
        v2n = b2.vitesse_x * nx + b2.vitesse_y * ny
        v2t = b2.vitesse_x * tx + b2.vitesse_y * ty

        # Si les billes s'éloignent déjà, on ne fait rien
        # (évite les collisions multiples qui bloqueraient les billes)
        if v1n - v2n <= 0:
            return

        # Échange des vitesses normales (collision élastique masses égales)
        # Les vitesses tangentielles restent inchangées
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
        # Renvoie True si plus aucune bille (non empochée) ne bouge
        return all(not b.est_en_mouvement()
                   for b in self.billes if not b.empochee)

    #___Accesseur de la bille blanche___
    def get_bille_blanche(self) -> BilleBlanche:
        return self.billes[0]       # la blanche est toujours à l'index 0