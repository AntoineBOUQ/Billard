
import sys
import math
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import QTimer

from jeu import Jeu


class FenetreDebut(QMainWindow):

    #___Initialisation___
    def __init__(self):
        super().__init__()
        # Charge l'interface graphique dessinée dans Qt Designer
        uic.loadUi("interface.ui", self)

        # ── Connexions des boutons aux méthodes correspondantes ──
        self.Boutton_Quitter.clicked.connect(self.close)
        self.pages.setCurrentIndex(0)               # on commence sur la page d'accueil
        self.Boutton_regle.clicked.connect(self.Fenetreregle)
        self.Boutton_Retour_regle.clicked.connect(self.Fenetredebut)
        self.Boutton_jouer.clicked.connect(self.Fenetrejeu1)
        self.Boutton_Suivant.clicked.connect(self.Fenetrejeu2)
        self.Boutton_Suivant.clicked.connect(self.Changer_label)
        self.Boutton_Jouer_Coup.clicked.connect(self.jouer_coup)
        self.jeu = None                             # le Jeu sera créé au lancement de la partie
        self.timer = QTimer(self)                   # timer pour animer les billes
        self.timer.timeout.connect(self._frame_animation)

    # ───── Navigation entre pages ─────
    def Fenetreregle(self):
        self.pages.setCurrentIndex(1)               # page des règles

    def Fenetredebut(self):
        self.pages.setCurrentIndex(0)               # retour à l'accueil

    def Fenetrejeu1(self):
        self.pages.setCurrentIndex(2)               # saisie des noms

    def Fenetrejeu2(self):
        self.pages.setCurrentIndex(3)               # page de jeu
        self._lancer_partie()                       # création du Jeu

    #___Mise à jour du label "Match de X contre Y"___
    def Changer_label(self):
        self.Label_jeu.setText(
            f"Match de {self.Edit_J1.text()} contre {self.Edit_J2.text()}"
        )

    # ───── Logique de partie ─────

    #___Création du Jeu et branchement à la TableBillard___
    def _lancer_partie(self):
        if self.jeu is not None:
            return                                  # déjà lancé, on ne refait pas

        # Récupération des noms (valeur par défaut si vide)
        nom1 = self.Edit_J1.text() or "Joueur 1"
        nom2 = self.Edit_J2.text() or "Joueur 2"

        # On crée la partie
        self.jeu = Jeu(nom1, nom2)
        # On relie le widget visuel au modèle (table) et inversement
        self.tableBillard.table = self.jeu.table
        self.jeu.table_billard = self.tableBillard

        # Connexion : quand on clique sur la table, on lance _coup_par_clic
        self.tableBillard.angle_choisi.connect(self._coup_par_clic)

        # Premier dessin (les 16 billes apparaissent)
        self.tableBillard.update()

        # Affiche le nom du joueur tiré au sort
        joueur = self.jeu.joueur_actuel()
        self.Label_jeu.setText(f"Au tour de {joueur.nom}")

    #___Coup déclenché par le bouton "Jouer Coup"___
    def jouer_coup(self):
        # Sécurités
        if self.jeu is None:
            return
        if self.timer.isActive():
            return                                  # une animation est en cours

        # Lecture des sliders et conversion vers les unités attendues
        force = self.slider_Force.value() / 100.0   # 0..1
        angle = math.radians(self.slider_Angle.value())  # radians

        self.jeu.jouer_coup(angle, force)
        self.timer.start(16)                        # ~60 fps

    #___Coup déclenché par clic sur la table___
    def _coup_par_clic(self, angle_rad):
        """Slot appelé quand le joueur clique sur la table."""
        if self.timer.isActive():
            return

        force = self.slider_Force.value() / 100.0
        self.jeu.jouer_coup(angle_rad, force)

        self.tableBillard.visee_active = False
        self.tableBillard.curseur_x = None  # ← efface la position du curseur
        self.tableBillard.update()  # ← force le repaint sans flèche

        self.timer.start(16)

    #___Une frame d'animation, appelée 60 fois par seconde___
    def _frame_animation(self):
        # Délégation : c'est le Jeu qui gère la physique et le redessin
        self.jeu.mettre_a_jour()

        # Quand toutes les billes sont arrêtées, on conclut le coup
        if self.jeu.table.est_arretee():
            self.timer.stop()
            self.jeu.fin_de_coup()                  # règles du jeu (changement de tour, etc.)

            # Met à jour le label avec le joueur dont c'est le tour
            joueur = self.jeu.joueur_actuel()
            self.Label_jeu.setText(f"Au tour de {joueur.nom}")

            # On peut viser à nouveau
            self.tableBillard.visee_active = True
            self.tableBillard.update()

            # Si la partie est finie, on annonce le gagnant
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
    sys.exit(app.exec())