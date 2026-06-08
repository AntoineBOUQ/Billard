import sys
import math
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import QTimer
from menu_billard import MenuBillard
from Jeu import Jeu


class FenetreDebut(QMainWindow):

    #___Initialisation___
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
        self.Boutton_Suivant.clicked.connect(self.Fenetrejeu2)
        self.Boutton_Suivant.clicked.connect(self.Changer_label)

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
        # Délai pour laisser le temps à showMaximized de s'appliquer
        QTimer.singleShot(100, self._ajuster_menu)

    def _ajuster_menu(self):
        """Ajuste le menu après que la fenêtre soit en plein écran."""
        # Force le QStackedWidget et page_5 à prendre toute la place
        self.pages.setGeometry(self.centralWidget().rect())
        self.page_5.setGeometry(self.pages.rect())
        self.menu_billard.setGeometry(self.page_5.rect())

        self.page_5.resizeEvent = lambda e: (
            self.pages.setGeometry(self.centralWidget().rect()),
            self.page_5.setGeometry(self.pages.rect()),
            self.menu_billard.setGeometry(self.page_5.rect())
        )
    # ───── Navigation entre pages ─────
    def Fenetreregle(self):
        self.pages.setCurrentIndex(1)

    def Fenetredebut(self):
        self.pages.setCurrentIndex(0)

    def Fenetrejeu1(self):
        self.pages.setCurrentIndex(2)

    def Fenetrejeu2(self):
        self.pages.setCurrentIndex(3)
        self._lancer_partie()

    #___Mise à jour du label "Match de X contre Y"___
    def Changer_label(self):
        self.Label_jeu.setText(
            f"Match de {self.Edit_J1.text()} contre {self.Edit_J2.text()}"
        )

    # ───── Logique de partie ─────

    #___Création du Jeu et branchement à la TableBillard___
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

    #___Coup déclenché par clic sur la table___
    def _coup_par_clic(self, angle_rad):
        if self.timer.isActive():
            return

        force = self.slider_Force.value() / 100.0
        if force <= 0:  # sécurité : pas de coup si force nulle
            return

        self.jeu.jouer_coup(angle_rad, force)

        self.tableBillard.visee_active = False
        self.tableBillard.curseur_x = None
        self.tableBillard.update()

        self.timer.start(16)

    #___Une frame d'animation, appelée 60 fois par seconde___
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

    # ───── Fermeture ─────

    #___Demande de confirmation à la fermeture___
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
    fenetre.show()          # ← manquait cette ligne !
    sys.exit(app.exec())