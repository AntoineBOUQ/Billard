import sys
import math
from PyQt6 import uic
from PyQt6.QtWidgets import (QApplication, QMainWindow, QMessageBox,
                             QHBoxLayout, QVBoxLayout, QTextEdit, QWidget)
from PyQt6.QtCore import QTimer, Qt
from panneau_joueurs import PanneauJoueurs
from jeu import Jeu
from menu_billard import MenuBillard, BilleSuivant, SliderForce


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
        self.label_2.setFixedHeight(28)
        self.label.setFixedHeight(28)

        layout = self.page_7.layout()
        if layout:
            layout.setSpacing(0)
            layout.setContentsMargins(200, 50, 200, 50)

        # ── Bille Suivant ──
        self.Boutton_Suivant.hide()
        rayon = min(self.screen().availableGeometry().width(),
                    self.screen().availableGeometry().height()) // 14
        self.bille_suivant = BilleSuivant(rayon, self)
        self.bille_suivant.hide()
        self.bille_suivant.clicked.connect(self.Fenetrejeu2)
        self.bille_suivant.clicked.connect(self.Changer_label)

        # ── Connexions des boutons des autres pages ──
        self.pages.setCurrentIndex(0)
        self.Boutton_Retour_regle.clicked.connect(self.Fenetredebut)
        self.Boutton_Suivant.clicked.connect(self.Fenetrejeu2)
        self.Boutton_Suivant.clicked.connect(self.Changer_label)

        # Jeu et timer
        self.jeu = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._frame_animation)

        # ── Panneau latéral des joueurs ──
        self.panneau = None
        self._installer_panneau_joueurs()

        # ── Remplissage de la page des règles ──
        self._remplir_page_regles()

        # ── Menu billes (créé en dernier) ──
        self.menu_billard = MenuBillard(self.page_5)
        self.menu_billard.signal_jouer.connect(self.Fenetrejeu1)
        self.menu_billard.signal_quitter.connect(self.close)
        self.menu_billard.signal_regles.connect(self.Fenetreregle)
        self.menu_billard.signal_score.connect(lambda: print("Score à venir"))

        # ── Slider force personnalisé ──
        self.slider_force_custom = SliderForce()

        self.horizontalLayout_9.replaceWidget(
            self.slider_Force,
            self.slider_force_custom
        )

        self.slider_Force.hide()
        self.slider_force_custom.setValue(50)

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
        w = self.width()
        h = self.height()
        rayon = self.bille_suivant.rayon
        x = (w - rayon * 2) // 2
        y = int(h * 0.65)
        self.bille_suivant.move(x, y)
        if self.pages.currentIndex() == 2:
            self.bille_suivant.show()



    #___Remplit la page des règles___
    def _remplir_page_regles(self):
        page = self.page_6
        bouton = self.Boutton_Retour_regle
        bouton.setParent(None)
        ancien = page.layout()
        if ancien is not None:
            QWidget().setLayout(ancien)

        col = QVBoxLayout(page)
        col.setContentsMargins(20, 16, 20, 16)
        col.setSpacing(12)

        barre = QHBoxLayout()
        barre.addWidget(bouton)
        barre.addStretch(1)
        col.addLayout(barre)

        texte = QTextEdit(page)
        texte.setReadOnly(True)
        texte.setStyleSheet(
            "QTextEdit{background:#1f1f23; color:#e8e8e8; border:none;"
            " padding:8px; font-size:14px;}"
        )
        texte.setHtml(self._html_regles())
        col.addWidget(texte, 1)

    #___Contenu HTML des règles___
    def _html_regles(self):
        return """
        <h1 style="color:#ffe03c;">Règles du jeu — Billard 8-ball</h1>

        <h2 style="color:#7ecb7e;">Le matériel et le but</h2>
        <ul>
          <li>15 billes numérotées plus la blanche. Les <b>pleines</b> sont les
              billes 1 à 7, les <b>rayées</b> les billes 9 à 15, et la
              <b>noire</b> est le 8.</li>
          <li>Deux joueurs s'affrontent. Chacun doit empocher toutes les billes
              de son groupe (pleines ou rayées), puis terminer par la noire.</li>
        </ul>

        <h2 style="color:#7ecb7e;">Déroulement d'une partie</h2>
        <ul>
          <li>Le premier joueur est tiré au sort. Les billes sont disposées en
              triangle et la blanche est placée sur la ligne de service.</li>
          <li>On joue à tour de rôle : on vise avec la souris et on règle la
              puissance avec la barre de force.</li>
          <li>Tant qu'on empoche au moins une de <b>ses</b> billes sans faute,
              on rejoue. Sinon, c'est à l'adversaire.</li>
        </ul>

        <h2 style="color:#7ecb7e;">L'attribution des groupes</h2>
        <ul>
          <li>Au début, aucun joueur n'a de groupe : la table est «&nbsp;ouverte&nbsp;».</li>
          <li>Le groupe est attribué au premier joueur qui empoche une bille
              <b>sans faute</b>.</li>
        </ul>

        <h2 style="color:#e0653c;">Les fautes</h2>
        <p>Chacune de ces fautes donne <b>deux coups</b> à l'adversaire :</p>
        <ul>
          <li>Empocher la blanche.</li>
          <li>Ne toucher <b>aucune</b> bille avec la blanche.</li>
          <li>Toucher en premier une bille du <b>groupe adverse</b>.</li>
          <li>Empocher une bille du <b>groupe adverse</b>.</li>
          <li>Toucher la noire en premier avant d'avoir fini son groupe.</li>
        </ul>

        <h2 style="color:#7ecb7e;">Gagner la partie : la noire</h2>
        <ul>
          <li>Empocher la noire dès le tout premier coup : victoire immédiate.</li>
          <li>Empocher la noire avant d'avoir rentré toutes ses billes :
              défaite immédiate.</li>
          <li>Une fois son groupe terminé, on vise la noire pour gagner.</li>
        </ul>
        """

    #___Insère le panneau des joueurs à droite de la table___
    def _installer_panneau_joueurs(self):
        layout_v = self.page_8.layout()
        if layout_v is None:
            return
        idx = layout_v.indexOf(self.tableBillard)
        if idx == -1:
            return
        layout_v.takeAt(idx)
        ligne = QHBoxLayout()
        ligne.setContentsMargins(0, 0, 0, 0)
        ligne.setSpacing(8)
        ligne.addWidget(self.tableBillard, 1)
        self.panneau = PanneauJoueurs(self.page_8)
        ligne.addWidget(self.panneau, 0)
        layout_v.insertLayout(idx, ligne)

    # ───── Navigation ─────
    def Fenetreregle(self):
        self.pages.setCurrentIndex(1)
        self.bille_suivant.hide()

    def Fenetredebut(self):
        self.pages.setCurrentIndex(0)
        self.bille_suivant.hide()

    def Fenetrejeu1(self):
        self.pages.setCurrentIndex(2)
        w = self.width()
        h = self.height()
        rayon = self.bille_suivant.rayon
        self.bille_suivant.move((w - rayon * 2) // 2, int(h * 0.65))
        self.bille_suivant.show()
        self.bille_suivant.raise_()

    def Fenetrejeu2(self):
        self.pages.setCurrentIndex(3)
        self.bille_suivant.hide()
        self._lancer_partie()

    #___Mise à jour du label___
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
        if self.panneau is not None:
            self.panneau.rafraichir(self.jeu)

    #___Coup déclenché par le bouton "Jouer Coup"___
    def jouer_coup(self):
        if self.jeu is None:
            return
        if self.timer.isActive():
            return
        force = self.slider_force_custom.value() / 100.0
        angle = math.radians(self.slider_Angle.value())
        self.jeu.jouer_coup(angle, force)
        self.timer.start(16)

    #___Coup déclenché par clic sur la table___
    def _coup_par_clic(self, angle_rad):
        if self.timer.isActive():
            return
        if self.jeu is None or self.jeu.est_termine():
            return
        force = self.slider_force_custom.value() / 100.0
        if force <= 0:
            return
        self.jeu.jouer_coup(angle_rad, force)
        self.tableBillard.visee_active = False
        self.tableBillard.curseur_x = None
        self.tableBillard.update()
        self.timer.start(16)

    #___Une frame d'animation___
    def _frame_animation(self):
        self.jeu.mettre_a_jour()
        if self.jeu.table.est_arretee():
            self.timer.stop()
            self.jeu.fin_de_coup()
            if self.jeu.est_termine():
                if self.panneau is not None:
                    self.panneau.rafraichir()
                message = (f"{self.jeu.gagnant.nom} a gagné "
                           f"en {self.jeu.nb_coups} coups !")
                if self.jeu.raison_fin:
                    message += f"\n\n{self.jeu.raison_fin}"
                QMessageBox.information(self, "Fin de partie", message)
                return
            joueur = self.jeu.joueur_actuel()
            if self.panneau is not None:
                self.panneau.rafraichir()
            if self.jeu.blanche_en_main:
                self.jeu.blanche_en_main = False
                self.Label_jeu.setText(
                    f"{joueur.nom} : placez la blanche sur la ligne, puis visez vers l'avant"
                )
                self.tableBillard.commencer_placement()
            else:
                self.Label_jeu.setText(f"Au tour de {joueur.nom}")
                self.tableBillard.visee_active = True
            self.tableBillard.update()

    # ───── Fermeture ─────
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