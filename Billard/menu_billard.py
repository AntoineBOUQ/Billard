# menu_billard.py
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QRadialGradient, QPen, QFont
from PyQt6.QtCore import Qt, pyqtSignal

# (numéro, couleur, rayé, texte_affiché)
# Disposition réglementaire 8-ball
# Rangée 1 : [1]
# Rangée 2 : [2, 3]  (pleine, rayée)
# Rangée 3 : [4, 8, 5]  (pleine, noire, pleine→Score)
# Rangée 4 : [6, 7, 9, 10]
# Rangée 5 : [11, 3rayée, 12, 13, 15]

BILLES_DATA = [
    # Rangée 1 — sommet
    (1,  "#FFD700", False, "Jouer"),    # bille 1 jaune pleine

    # Rangée 2
    (10, "#0000CC", True,  ""),         # bleue rayée
    (4,  "#800080", False, ""),         # violette pleine

    # Rangée 3
    (3,  "#CC0000", False, ""),         # rouge pleine
    (8,  "#111111", False, "Quitter"),  # noire au centre → Quitter
    (11, "#CC0000", True,  "Règles"),   # rouge rayée → Règles

    # Rangée 4
    (12, "#800080", True,  ""),         # violette rayée
    (5,  "#FF6600", False, "Score"),    # orange pleine → Score
    (13, "#FF6600", True,  ""),         # orange rayée
    (6,  "#006600", False, ""),         # verte pleine

    # Rangée 5 — base
    (7,  "#8B0000", False, ""),         # marron pleine
    (9,  "#FFD700", True,  ""),         # jaune rayée
    (14, "#006600", True,  ""),         # verte rayée
    (2,  "#0000CC", False, ""),         # bleue pleine
    (15, "#8B0000", True,  ""),         # marron rayée
]


class BilleBouton(QWidget):
    clicked = pyqtSignal(int)

    def __init__(self, numero, couleur, raye, rayon, texte="", parent=None):
        super().__init__(parent)
        self.numero = numero
        self.couleur = QColor(couleur)
        self.raye = raye
        self.rayon = rayon
        self.texte = texte          # ← attribut texte ajouté
        self.est_bouton = texte != ""  # ← True si c'est un bouton actif
        self.survol = False
        self.setFixedSize(rayon * 2, rayon * 2)
        self.setMouseTracking(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.rayon, self.rayon
        r = self.rayon - 2

        # Fond blanc pour les rayées
        if self.raye:
            painter.setBrush(QColor(240, 240, 240))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        # Corps de la bille
        if self.raye:
            painter.setBrush(self.couleur)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawChord(cx - r, cy - r, r * 2, r * 2, 30 * 16, 120 * 16)
            painter.drawChord(cx - r, cy - r, r * 2, r * 2, 210 * 16, 120 * 16)
        else:
            painter.setBrush(self.couleur)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        # Reflet lumineux
        gradient = QRadialGradient(cx - r * 0.3, cy - r * 0.3, r * 0.6)
        gradient.setColorAt(0, QColor(255, 255, 255, 160))
        gradient.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        # Cercle blanc central
        nr = int(r * 0.42)
        painter.setBrush(QColor(255, 255, 255, 220))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(cx - nr, cy - nr, nr * 2, nr * 2)

        # Texte dans le cercle blanc
        painter.setPen(QColor(0, 0, 0))
        if self.texte:
            taille = max(6, int(nr * 0.9 / max(1, len(self.texte) * 0.4)))
            font = QFont("Arial", taille, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(
                cx - nr, cy - nr, nr * 2, nr * 2,
                Qt.AlignmentFlag.AlignCenter,
                self.texte
            )
        else:
            font = QFont("Arial", max(8, int(r * 0.3)), QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(
                cx - nr, cy - nr, nr * 2, nr * 2,
                Qt.AlignmentFlag.AlignCenter,
                str(self.numero)
            )
            # ── Voile gris pour les billes décoratives ──
            if not self.est_bouton:
                painter.setBrush(QColor(0, 0, 0, 80))  # noir semi-transparent
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        # Contour
        pen = QPen(QColor(255, 255, 255, 180), 2.5) if self.survol \
              else QPen(QColor(80, 80, 80), 1.5)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)

    def enterEvent(self, event):
        self.survol = True
        self.update()
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def leaveEvent(self, event):
        self.survol = False
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.numero)


class MenuBillard(QWidget):
    signal_jouer   = pyqtSignal()
    signal_quitter = pyqtSignal()
    signal_regles  = pyqtSignal()
    signal_score   = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._placer_billes()

    def _placer_billes(self):
        # Supprime les anciens widgets
        for child in self.findChildren(BilleBouton):
            child.deleteLater()

        w, h = self.width(), self.height()
        if w == 0 or h == 0:
            return                  # pas encore de taille, on attend

        rayon = min(w, h) // 10
        espacement = rayon * 2
        rangees = [1, 2, 3, 4, 5]

        hauteur_triangle = len(rangees) * espacement
        y_depart = (h - hauteur_triangle) // 2

        idx = 0
        for rang, nb in enumerate(rangees):
            largeur_rang = nb * espacement
            x_depart = (w - largeur_rang) // 2
            for i in range(nb):
                numero, couleur, raye, texte = BILLES_DATA[idx]  # ← 4 valeurs
                bille = BilleBouton(numero, couleur, raye, rayon, texte, self)
                bille.move(x_depart + i * espacement,
                           y_depart + rang * espacement)
                bille.show()
                bille.clicked.connect(self._on_bille_clicked)
                idx += 1

    def _on_bille_clicked(self, numero):
        if numero == 1:
            self.signal_jouer.emit()
        elif numero == 11:
            self.signal_regles.emit()
        elif numero == 8:
            self.signal_quitter.emit()
        elif numero == 5:
            self.signal_score.emit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(31, 122, 31))