
import math
from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QPolygonF
from PyQt6.QtCore import Qt, QPointF, pyqtSignal


class TableBillard(QWidget):
    # Dimensions logiques de la table (référentiel utilisé par Table)
    LARGEUR_LOGIQUE = 800
    HAUTEUR_LOGIQUE = 500

    # Signal émis quand le joueur clique sur la table pour tirer.
    # Il transporte l'angle de visée en radians.
    angle_choisi = pyqtSignal(float)

    #___Initialisation___
    def __init__(self, parent=None, table=None):
        super().__init__(parent)
        self.setWindowTitle("Table de billard")
        self.table = table          # référence vers le modèle (peut être None au début)
        # Le widget peut s'étirer dans son parent
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(400, 250)

        # Permet à mouseMoveEvent d'être appelé sans bouton enfoncé
        self.setMouseTracking(True)

        # Position du curseur en coordonnées logiques (None = souris hors widget)
        self.curseur_x = None
        self.curseur_y = None

        # Angle de la flèche de visée (radians)
        self.angle_visee = 0.0

        # Permet de couper la visée pendant l'animation des billes
        self.visee_active = True

    #___Calcul de la mise à l'échelle (logique → pixels)___
    def _calculer_transformation(self):
        """
        Renvoie (échelle, dx, dy) : facteur de zoom et décalage pour centrer
        la table 800x500 dans le widget tout en gardant le ratio.
        """
        w = self.width()
        h = self.height()
        echelle = min(w / self.LARGEUR_LOGIQUE, h / self.HAUTEUR_LOGIQUE)
        largeur_table = self.LARGEUR_LOGIQUE * echelle
        hauteur_table = self.HAUTEUR_LOGIQUE * echelle
        dx = (w - largeur_table) / 2
        dy = (h - hauteur_table) / 2
        return echelle, dx, dy

    #___Conversion inverse (pixels → logique)___
    def _widget_vers_logique(self, x_widget, y_widget):
        # Sert à savoir où se trouve la souris en coordonnées de la table
        echelle, dx, dy = self._calculer_transformation()
        if echelle == 0:
            return 0, 0
        x_logique = (x_widget - dx) / echelle
        y_logique = (y_widget - dy) / echelle
        return x_logique, y_logique

    # ───── Événements souris ─────

    #___Mouvement de la souris___
    def mouseMoveEvent(self, event):
        if not self.visee_active or self.table is None:
            return
        # Conversion pixels → logique
        x_log, y_log = self._widget_vers_logique(
            event.position().x(), event.position().y()
        )
        self.curseur_x = x_log
        self.curseur_y = y_log

        # Calcul de l'angle entre la blanche et le curseur
        blanche = self.table.get_bille_blanche()
        dx = x_log - blanche.x
        dy = y_log - blanche.y
        # atan2 gère correctement les 4 quadrants
        self.angle_visee = math.atan2(dy, dx)

        # Redessine pour mettre à jour la flèche
        self.update()

    #___La souris quitte la zone du widget___
    def leaveEvent(self, event):
        self.curseur_x = None
        self.curseur_y = None
        self.update()

    #___Clic souris___
    def mousePressEvent(self, event):
        if not self.visee_active or self.table is None:
            return
        # On ne réagit qu'au clic gauche
        if event.button() != Qt.MouseButton.LeftButton:
            return
        # Émission du signal : l'interface va déclencher le coup
        self.angle_choisi.emit(self.angle_visee)

    # ───── Dessin ─────

    #___Méthode appelée par Qt à chaque redessin___
    def paintEvent(self, event):
        peintre = QPainter(self)
        peintre.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Fond noir (visible si le ratio du widget ne correspond pas à 8:5)
        peintre.fillRect(self.rect(), QColor(40, 40, 40))

        # Application de la transformation : à partir d'ici on dessine
        # en coordonnées logiques 0..800 / 0..500
        echelle, dx, dy = self._calculer_transformation()
        peintre.translate(dx, dy)
        peintre.scale(echelle, echelle)

        # Tapis vert
        peintre.setBrush(QBrush(QColor(0, 100, 0)))
        peintre.setPen(Qt.PenStyle.NoPen)
        peintre.drawRect(0, 0, self.LARGEUR_LOGIQUE, self.HAUTEUR_LOGIQUE)

        # Trous (6 cercles noirs aux coins et au milieu des longs côtés)
        peintre.setBrush(QBrush(Qt.GlobalColor.black))
        rayon_trou = 18
        positions_trous = [
            (0, 0), (self.LARGEUR_LOGIQUE // 2, 0), (self.LARGEUR_LOGIQUE, 0),
            (0, self.HAUTEUR_LOGIQUE),
            (self.LARGEUR_LOGIQUE // 2, self.HAUTEUR_LOGIQUE),
            (self.LARGEUR_LOGIQUE, self.HAUTEUR_LOGIQUE),
        ]
        for x, y in positions_trous:
            peintre.drawEllipse(x - rayon_trou, y - rayon_trou,
                                rayon_trou * 2, rayon_trou * 2)

        # Ligne de service et cercle de service (côté blanche)
        peintre.setPen(QPen(QColor(255, 255, 255, 80), 1))
        peintre.setBrush(Qt.BrushStyle.NoBrush)
        x_service = self.LARGEUR_LOGIQUE // 4
        peintre.drawLine(x_service, 0, x_service, self.HAUTEUR_LOGIQUE)
        rayon_cercle = 60
        peintre.drawEllipse(x_service - rayon_cercle,
                            self.HAUTEUR_LOGIQUE // 2 - rayon_cercle,
                            rayon_cercle * 2, rayon_cercle * 2)

        # Billes : on les dessine seulement si la table est branchée
        if self.table is not None and hasattr(self.table, "billes"):
            for i, bille in enumerate(self.table.billes):
                if bille.empochee:      # bille tombée → on ne la dessine pas
                    continue
                couleur = self.table.billes_couleur[i]
                if i <= 8:               # 0 = blanche, 1..8 = pleines
                    self._dessiner_boule_pleine(peintre, bille.x, bille.y, couleur)
                else:                    # 9..15 = rayées
                    self._dessiner_boule_rayee(peintre, bille.x, bille.y, couleur)

            # Flèche de visée — seulement si la blanche est en jeu et la souris présente
            blanche = self.table.get_bille_blanche()
            if (self.visee_active and not blanche.empochee
                    and self.curseur_x is not None):
                self._dessiner_fleche_visee(peintre, blanche)

    #___Dessin d'une bille pleine___
    def _dessiner_boule_pleine(self, peintre, x, y, couleur):
        rayon = 12
        r, g, b = couleur
        peintre.setBrush(QBrush(QColor(r, g, b)))
        peintre.setPen(QPen(Qt.GlobalColor.black, 1))
        peintre.drawEllipse(int(x - rayon), int(y - rayon),
                            rayon * 2, rayon * 2)

    #___Dessin d'une bille rayée___
    def _dessiner_boule_rayee(self, peintre, x, y, couleur):
        rayon = 12
        r, g, b = couleur
        # Disque blanc en arrière-plan
        peintre.setBrush(QBrush(Qt.GlobalColor.white))
        peintre.setPen(QPen(Qt.GlobalColor.black, 1))
        peintre.drawEllipse(int(x - rayon), int(y - rayon),
                            rayon * 2, rayon * 2)
        # Bande colorée au milieu (effet "rayé")
        peintre.setBrush(QBrush(QColor(r, g, b)))
        peintre.setPen(Qt.PenStyle.NoPen)
        peintre.drawRect(int(x - rayon), int(y - rayon // 2),
                         rayon * 2, rayon)

    #___Dessin de la flèche de visée___
    def _dessiner_fleche_visee(self, peintre, blanche):
        longueur = 100      # longueur de la flèche en pixels logiques

        # Point de départ : sur le bord de la blanche, pas en son centre
        x_debut = blanche.x + math.cos(self.angle_visee) * blanche.rayon
        y_debut = blanche.y + math.sin(self.angle_visee) * blanche.rayon

        # Point de fin
        x_fin = blanche.x + math.cos(self.angle_visee) * (blanche.rayon + longueur)
        y_fin = blanche.y + math.sin(self.angle_visee) * (blanche.rayon + longueur)

        # Ligne principale
        peintre.setPen(QPen(Qt.GlobalColor.white, 2))
        peintre.drawLine(QPointF(x_debut, y_debut), QPointF(x_fin, y_fin))

        # Pointe : petit triangle blanc à l'extrémité
        taille_pointe = 10
        angle_g = self.angle_visee + math.radians(150)
        angle_d = self.angle_visee - math.radians(150)
        x_g = x_fin + math.cos(angle_g) * taille_pointe
        y_g = y_fin + math.sin(angle_g) * taille_pointe
        x_d = x_fin + math.cos(angle_d) * taille_pointe
        y_d = y_fin + math.sin(angle_d) * taille_pointe

        triangle = QPolygonF([
            QPointF(x_fin, y_fin),
            QPointF(x_g, y_g),
            QPointF(x_d, y_d),
        ])
        peintre.setBrush(QBrush(Qt.GlobalColor.white))
        peintre.setPen(Qt.PenStyle.NoPen)
        peintre.drawPolygon(triangle)