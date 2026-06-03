import sys
import math
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import QTimer, Qt
from menu_billard import MenuBillard, BilleSuivant
from Jeu import Jeu


class FenetreDebut(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi("interface.ui", self)

        # Cache les anciens boutons de page_5
        self.Boutton_jouer.hide()
        self.Boutton_score.hide()
        self.Boutton_regle.hide()
        self.Boutton_Quitter.hide()

        # ── Connexions des boutons des autres pages ──
        self.pages.setCurrentIndex(0)
        self.Boutton_Retour_regle.clicked.connect(self.Fenetredebut)
        self.Boutton_Jouer_Coup.clicked.connect(self.jouer_coup)

        # ── Stylesheet page_7 ──
        self.page_7.setStyleSheet("""
            #page_7 {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f3d0f,
                    stop:0.3 #1a6b1a,
                    stop:0.5 #145214,
                    stop:0.7 #1a6b1a,
                    stop:1 #0f3d0f
                );
            }
            QLabel {
                background-color: transparent;
                color: white;
                font-size: 22px;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #5a0000;
                border-radius: 8px;
                padding: 6px;
                font-size: 18px;
            }
            QLineEdit:focus {
                border: 2px solid #8b0000;
            }
        """)
        # style de la page de règles
        self.page_6.setStyleSheet("""
            #page_6 {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f3d0f,
                    stop:0.3 #1a6b1a,
                    stop:0.5 #145214,
                    stop:0.7 #1a6b1a,
                    stop:1 #0f3d0f
                );
            }
            QLabel {
                background-color: transparent;
                color: white;
                font-size: 18px;
            }
            QPushButton {
                background-color: #6b0000;
                color: #d4d4d4;
                border: 2px solid #5a0000;
                border-radius: 8px;
                padding: 6px;
                font-size: 14px;
                min-width: 150px;
                max-width: 150px;
            }
            QPushButton:hover {
                background-color: #7a0000;
                color: #e0e0e0;
            }
        """)

        # Centre le titre et réduit marges
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_2.setContentsMargins(0, 0, 0, 0)
        self.label.setContentsMargins(0, 0, 0, 0)
        self.Edit_J1.setContentsMargins(0, 0, 0, 0)
        self.Edit_J2.setContentsMargins(0, 0, 0, 0)

        # Fixe la hauteur des labels pour les coller aux champs
        self.label_2.setFixedHeight(28)
        self.label.setFixedHeight(28)

        # Réduit l'espacement dans le layout de page_7
        layout = self.page_7.layout()
        if layout:
            layout.setSpacing(0)
            layout.setContentsMargins(200, 50, 200, 50)

        # ── Bille Suivant — parent = fenêtre principale ──
        self.Boutton_Suivant.hide()
        rayon = min(self.screen().availableGeometry().width(),
                    self.screen().availableGeometry().height()) // 14
        self.bille_suivant = BilleSuivant(rayon, self)  # parent = self
        self.bille_suivant.hide()                        # cachée au départ
        self.bille_suivant.clicked.connect(self.Fenetrejeu2)
        self.bille_suivant.clicked.connect(self.Changer_label)

        # Jeu et timer
        self.jeu = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._frame_animation)

        # ── Menu billes (créé en dernier) ──
        self.menu_billard = MenuBillard(self.page_5)
        self.menu_billard.signal_jouer.connect(self.Fenetrejeu1)
        self.menu_billard.signal_quitter.connect(self.close)
        self.menu_billard.signal_regles.connect(self.Fenetreregle)
        self.menu_billard.signal_score.connect(lambda: print("Score à venir"))

    def showEvent(self, event):
        super().showEvent(event)
        self.showMaximized()
        QTimer.singleShot(100, self._ajuster_menu)
        QTimer.singleShot(200, self._ajuster_page7)

    def _ajuster_menu(self):
        self.pages.setGeometry(self.centralWidget().rect())
        self.page_5.setGeometry(self.pages.rect())
        self.menu_billard.setGeometry(self.page_5.rect())
        self.page_5.resizeEvent = lambda e: (
            self.pages.setGeometry(self.centralWidget().rect()),
            self.page_5.setGeometry(self.pages.rect()),
            self.menu_billard.setGeometry(self.page_5.rect())
        )

    def _ajuster_page7(self):
        """Centre la bille Suivant sur la fenêtre principale."""
        w = self.width()
        h = self.height()
        rayon = self.bille_suivant.rayon
        x = (w - rayon * 2) // 2
        y = int(h * 0.65)
        self.bille_suivant.move(x, y)
        # On ne l'affiche que si on est sur la page de saisie
        if self.pages.currentIndex() == 2:
            self.bille_suivant.show()

    # ───── Navigation ─────
    def Fenetreregle(self):
        self.pages.setCurrentIndex(1)
        self.bille_suivant.hide()

    def Fenetredebut(self):
        self.pages.setCurrentIndex(0)
        self.bille_suivant.hide()

    def Fenetrejeu1(self):
        self.pages.setCurrentIndex(2)
        # Repositionne et affiche la bille
        w = self.width()
        h = self.height()
        rayon = self.bille_suivant.rayon
        self.bille_suivant.move((w - rayon * 2) // 2, int(h * 0.65))
        self.bille_suivant.show()
        self.bille_suivant.raise_()  # passe au premier plan

    def Fenetrejeu2(self):
        self.pages.setCurrentIndex(3)
        self.bille_suivant.hide()
        self._lancer_partie()

    def Changer_label(self):
        self.Label_jeu.setText(
            f"Match de {self.Edit_J1.text()} contre {self.Edit_J2.text()}"
        )

    # ───── Logique de partie ─────
    def _lancer_partie(self):
        if self.jeu is not None:
            return
        nom1 = self.Edit_J1.text() or "Joueur 1"
        nom2 = self.Edit_J2.text() or "Joueur 2"
        self.jeu = Jeu(nom1, nom2)
        self.tableBillard.table = self.jeu.table
        self.jeu.table_billard = self.tableBillard
        self.tableBillard.angle_choisi.connect(self._coup_par_clic)
        self.tableBillard.update()
        joueur = self.jeu.joueur_actuel()
        self.Label_jeu.setText(f"Au tour de {joueur.nom}")

    def jouer_coup(self):
        if self.jeu is None:
            return
        if self.timer.isActive():
            return
        force = self.slider_Force.value() / 100.0
        angle = math.radians(self.slider_Angle.value())
        self.jeu.jouer_coup(angle, force)
        self.timer.start(16)

    def _coup_par_clic(self, angle_rad):
        if self.timer.isActive():
            return
        force = self.slider_Force.value() / 100.0
        self.jeu.jouer_coup(angle_rad, force)
        self.tableBillard.visee_active = False
        self.tableBillard.curseur_x = None
        self.tableBillard.update()
        self.timer.start(16)

    def _frame_animation(self):
        self.jeu.mettre_a_jour()
        if self.jeu.table.est_arretee():
            self.timer.stop()
            self.jeu.fin_de_coup()
            joueur = self.jeu.joueur_actuel()
            self.Label_jeu.setText(f"Au tour de {joueur.nom}")
            self.tableBillard.visee_active = True
            self.tableBillard.update()
            if self.jeu.est_termine():
                QMessageBox.information(
                    self, "Fin de partie",
                    f"{self.jeu.gagnant.nom} a gagné en {self.jeu.nb_coups} coups !"
                )

    def closeEvent(self, event):
        reponse = QMessageBox.question(
            self, "Confirmation", "Êtes-vous sûr de vouloir quitter ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reponse == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = FenetreDebut()
    fenetre.show()
    sys.exit(app.exec())