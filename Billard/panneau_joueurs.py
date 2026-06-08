# panneau_joueurs.py
from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt


class PanneauJoueurs(QWidget):
    """
    Panneau latéral (à droite de la table) affichant, pour chaque joueur :
    son nom, son groupe, les billes de son groupe (rentrées en couleur,
    restantes en grisé) et un indicateur de faute sous le nom.
    """

    LARGEUR = 240

    #___Initialisation___
    def __init__(self, parent=None, jeu=None):
        super().__init__(parent)
        self.jeu = jeu                      # référence vers le modèle (réglée par l'interface)
        self.setMinimumWidth(self.LARGEUR)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

    #___Rafraîchit l'affichage (à appeler après chaque coup)___
    def rafraichir(self, jeu=None):
        if jeu is not None:
            self.jeu = jeu
        self.update()

    #___Billes du groupe d'un joueur : (numero, rgb, rayee, rentree)___
    def _billes_du_groupe(self, joueur):
        if joueur.groupe == "pleines":
            numeros, rayee = range(1, 8), False
        elif joueur.groupe == "rayées":
            numeros, rayee = range(9, 16), True
        else:
            return []
        billes = []
        for n in numeros:
            bille = self.jeu.table.billes[n]            # billes[n] a pour numéro n
            rgb = self.jeu.table.billes_couleur[n]
            billes.append((n, rgb, rayee, bille.empochee))
        return billes

    #___Dessin du panneau___
    def paintEvent(self, event):
        peintre = QPainter(self)
        peintre.setRenderHint(QPainter.RenderHint.Antialiasing)
        peintre.fillRect(self.rect(), QColor(28, 28, 30))

        if self.jeu is None:
            return

        w = self.width()
        h = self.height()
        moitie = h // 2

        for index, joueur in enumerate(self.jeu.joueurs):
            self._dessiner_joueur(peintre, joueur, index, 0, index * moitie, w, moitie)

        # Séparateur entre les deux joueurs
        peintre.setPen(QPen(QColor(80, 80, 80), 1))
        peintre.drawLine(10, moitie, w - 10, moitie)

    #___Dessin du bloc d'un joueur___
    def _dessiner_joueur(self, peintre, joueur, index, x, y, w, h):
        marge = 16
        est_tour = (self.jeu.tour_actuel == index) and not self.jeu.est_termine()

        # Surbrillance si c'est au tour du joueur
        if est_tour:
            peintre.setBrush(QColor(255, 220, 0, 28))
            peintre.setPen(Qt.PenStyle.NoPen)
            peintre.drawRoundedRect(x + 6, y + 6, w - 12, h - 12, 8, 8)

        # Nom du joueur
        peintre.setPen(QColor(255, 224, 60) if est_tour else QColor(235, 235, 235))
        peintre.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        peintre.drawText(x + marge, y + marge, w - 2 * marge, 28,
                         Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         joueur.nom)

        # Groupe
        libelle = {"pleines": "Pleines", "rayées": "Rayées"}.get(joueur.groupe, "Groupe non défini")
        peintre.setPen(QColor(170, 170, 170))
        peintre.setFont(QFont("Arial", 10))
        peintre.drawText(x + marge, y + marge + 28, w - 2 * marge, 18,
                         Qt.AlignmentFlag.AlignLeft, libelle)

        # Indicateur sous le nom : FAUTE (rouge) ou 2 coups (vert)
        by = y + marge + 50
        if self.jeu.faute_joueur == index:
            self._dessiner_badge(peintre, x + marge, by, "FAUTE", QColor(200, 40, 40))
        elif est_tour and getattr(self.jeu, "coups_restants", 1) == 2:
            self._dessiner_badge(peintre, x + marge, by, "2 coups", QColor(40, 150, 70))

        # Billes du groupe (rentrées en couleur, restantes grisées)
        billes = self._billes_du_groupe(joueur)
        rayon = 12
        ecart = 28
        bx = x + marge + rayon
        cy = y + h - 30
        for (numero, rgb, rayee, rentree) in billes:
            self._dessiner_petite_bille(peintre, bx, cy, rayon, numero, rgb, rayee, rentree)
            bx += ecart

    #___Petit badge arrondi avec texte___
    def _dessiner_badge(self, peintre, x, y, texte, couleur):
        largeur, hauteur = 78, 22
        peintre.setBrush(couleur)
        peintre.setPen(Qt.PenStyle.NoPen)
        peintre.drawRoundedRect(x, y, largeur, hauteur, 5, 5)
        peintre.setPen(QColor(255, 255, 255))
        peintre.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        peintre.drawText(x, y, largeur, hauteur, Qt.AlignmentFlag.AlignCenter, texte)

    #___Dessin d'une petite bille (style boule de billard)___
    def _dessiner_petite_bille(self, peintre, cx, cy, r, numero, rgb, rayee, rentree):
        alpha = 255 if rentree else 55          # grisé tant qu'elle n'est pas rentrée
        couleur = QColor(rgb[0], rgb[1], rgb[2], alpha)

        if rayee:
            # Disque blanc puis bande colorée
            peintre.setBrush(QColor(240, 240, 240, alpha))
            peintre.setPen(Qt.PenStyle.NoPen)
            peintre.drawEllipse(cx - r, cy - r, 2 * r, 2 * r)
            peintre.setBrush(couleur)
            peintre.drawRect(cx - r, cy - r // 2, 2 * r, r)
        else:
            peintre.setBrush(couleur)
            peintre.setPen(Qt.PenStyle.NoPen)
            peintre.drawEllipse(cx - r, cy - r, 2 * r, 2 * r)

        # Pastille blanche centrale + numéro
        nr = int(r * 0.6)
        peintre.setBrush(QColor(255, 255, 255, alpha))
        peintre.setPen(Qt.PenStyle.NoPen)
        peintre.drawEllipse(cx - nr, cy - nr, 2 * nr, 2 * nr)
        peintre.setPen(QColor(20, 20, 20, alpha))
        peintre.setFont(QFont("Arial", max(7, nr), QFont.Weight.Bold))
        peintre.drawText(cx - nr, cy - nr, 2 * nr, 2 * nr,
                         Qt.AlignmentFlag.AlignCenter, str(numero))

        # Contour
        peintre.setPen(QPen(QColor(15, 15, 15, alpha), 1))
        peintre.setBrush(Qt.BrushStyle.NoBrush)
        peintre.drawEllipse(cx - r, cy - r, 2 * r, 2 * r)