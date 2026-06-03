
import math
from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QPolygonF
from PyQt6.QtCore import Qt, QPointF, pyqtSignal


class TableBillard(QWidget):
    # Dimensions logiques de la table (référentiel utilisé par Table)
    LARGEUR_LOGIQUE = 800
    HAUTEUR_LOGIQUE = 500
    BISEAU = 50
    RAYON_TROU = 18
    MARGE_CADRE = 25
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
        self.couleur_bois = QColor(74, 48, 24)
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
        # ___Calcul de la mise à l'échelle (logique → pixels)___
    def _calculer_transformation(self):

        w = self.width()
        h = self.height()
        marge = self.MARGE_CADRE

            # Taille totale à faire rentrer = table + cadre des deux côtés
        largeur_totale = self.LARGEUR_LOGIQUE + 2 * marge
        hauteur_totale = self.HAUTEUR_LOGIQUE + 2 * marge

        echelle = min(w / largeur_totale, h / hauteur_totale)

        dx = (w - largeur_totale * echelle) / 2 + marge * echelle
        dy = (h - hauteur_totale * echelle) / 2 + marge * echelle
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

        # ___Méthode appelée par Qt à chaque redessin___
    def paintEvent(self, event):
        peintre = QPainter(self)
        peintre.setRenderHint(QPainter.RenderHint.Antialiasing)

            # 1. Fond extérieur neutre (gris) — ce qu'on voit AU-DELÀ du cadre
        peintre.fillRect(self.rect(), QColor(40, 40, 40))

            # 2. Transformation logique → pixels
        echelle, dx, dy = self._calculer_transformation()
        peintre.translate(dx, dy)
        peintre.scale(echelle, echelle)

        W = self.LARGEUR_LOGIQUE
        H = self.HAUTEUR_LOGIQUE
        b = self.BISEAU

        # 3. Cadre en bois marron : rectangle qui déborde du tapis des 4 côtés
        marge = 18
        peintre.setPen(Qt.PenStyle.NoPen)
        peintre.setBrush(QBrush(self.couleur_bois))  # marron
        peintre.drawRect(int(-marge), int(-marge),
                         int(W + 2 * marge), int(H + 2 * marge))

            # 4. Tapis vert (par-dessus le cadre)
        peintre.setBrush(QBrush(QColor(0, 100, 0)))
        peintre.drawRect(0, 0, W, H)

            # 5. Biseaux des coins (triangles marron) : la diagonale est une bande
        peintre.setBrush(QBrush(self.couleur_bois))
        peintre.drawPolygon(QPolygonF([QPointF(0, 0), QPointF(b, 0), QPointF(0, b)]))
        peintre.drawPolygon(QPolygonF([QPointF(W, 0), QPointF(W - b, 0), QPointF(W, b)]))
        peintre.drawPolygon(QPolygonF([QPointF(0, H), QPointF(b, H), QPointF(0, H - b)]))
        peintre.drawPolygon(QPolygonF([QPointF(W, H), QPointF(W - b, H), QPointF(W, H - b)]))

            # 6. Trous : 4 coins (au milieu du biseau) + 2 milieux
        peintre.setBrush(QBrush(Qt.GlobalColor.black))
        rayon_trou = self.RAYON_TROU
        positions_trous = [
            (b / 2, b / 2),
            (W - b / 2, b / 2),
            (b / 2, H - b / 2),
            (W - b / 2, H - b / 2),
            (W / 2, 0),
            (W / 2, H),
        ]
        for x, y in positions_trous:
            peintre.drawEllipse(int(x - rayon_trou), int(y - rayon_trou),
                                rayon_trou * 2, rayon_trou * 2)

            # 7. Ligne de service et cercle de service (côté blanche)
        peintre.setPen(QPen(QColor(255, 255, 255, 80), 1))
        peintre.setBrush(Qt.BrushStyle.NoBrush)
        x_service = W // 4
        peintre.drawLine(x_service, 0, x_service, H)
        rayon_cercle = 60
        peintre.drawEllipse(x_service - rayon_cercle, H // 2 - rayon_cercle,
                            rayon_cercle * 2, rayon_cercle * 2)

            # 8. Billes
        if self.table is not None and hasattr(self.table, "billes"):
            for i, bille in enumerate(self.table.billes):
                if bille.empochee:
                    continue
                couleur = self.table.billes_couleur[i]
                if i <= 8:
                    self._dessiner_boule_pleine(peintre, bille.x, bille.y, couleur)
                else:
                    self._dessiner_boule_rayee(peintre, bille.x, bille.y, couleur)

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