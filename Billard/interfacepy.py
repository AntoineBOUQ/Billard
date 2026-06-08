import sys
import math
from PyQt6 import uic
from PyQt6.QtWidgets import (QApplication, QMainWindow, QMessageBox,
                             QHBoxLayout, QVBoxLayout, QTextEdit, QWidget)
from PyQt6.QtCore import QTimer
from menu_billard import MenuBillard
from panneau_joueurs import PanneauJoueurs
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

        # ── Panneau latéral des joueurs (à droite de la table) ──
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
    #___Remplit la page des règles avec une zone de texte défilable___
    def _remplir_page_regles(self):
        page = self.page_6
        bouton = self.Boutton_Retour_regle
        bouton.setParent(None)                      # détache le bouton de l'ancien layout
        ancien = page.layout()
        if ancien is not None:
            QWidget().setLayout(ancien)             # widget jetable : libère l'ancien layout

        col = QVBoxLayout(page)
        col.setContentsMargins(20, 16, 20, 16)
        col.setSpacing(12)

        # Barre du haut : bouton Retour à gauche
        barre = QHBoxLayout()
        barre.addWidget(bouton)
        barre.addStretch(1)
        col.addLayout(barre)

        # Zone de texte défilable contenant les règles
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
              <b>sans faute</b> : la première bille rentrée détermine son groupe,
              et l'adversaire hérite de l'autre.</li>
        </ul>

        <h2 style="color:#e0653c;">Les fautes</h2>
        <p>Chacune de ces fautes donne <b>deux coups</b> à l'adversaire :</p>
        <ul>
          <li>Empocher la blanche.</li>
          <li>Ne toucher <b>aucune</b> bille avec la blanche.</li>
          <li>Toucher en premier une bille du <b>groupe adverse</b>.</li>
          <li>Empocher une bille du <b>groupe adverse</b>.</li>
          <li>Toucher la noire en premier (ou l'empocher) <b>avant</b> d'avoir
              fini son groupe.</li>
        </ul>

        <h2 style="color:#7ecb7e;">La règle des deux coups</h2>
        <ul>
          <li>Après une faute de l'adversaire, le joueur dispose de deux coups.</li>
          <li>Le deuxième coup n'est accordé que si le premier n'est
              <b>pas lui-même une faute</b>.</li>
          <li>Empocher une de ses billes pendant ces deux coups fait simplement
              poursuivre le jeu normalement.</li>
        </ul>

        <h2 style="color:#7ecb7e;">La bille en main</h2>
        <ul>
          <li>Quand la blanche est empochée, l'adversaire la <b>replace</b>
              lui-même le long de la ligne de service.</li>
          <li>Depuis cette position, il ne peut jouer que <b>vers l'avant</b>
              (vers le reste de la table).</li>
        </ul>

        <h2 style="color:#ffe03c;">Gagner la partie : la noire</h2>
        <ul>
          <li>Empocher la noire <b>dès le tout premier coup</b> de la partie :
              victoire immédiate.</li>
          <li>Empocher la noire <b>avant</b> d'avoir rentré toutes ses billes :
              défaite immédiate.</li>
          <li>Une fois son groupe terminé, on vise la noire ; il faut l'empocher
              sans faute pour gagner.</li>
          <li><b>Cas particulier :</b> lorsque les <b>deux</b> joueurs ont fini
              leur groupe, la noire doit être empochée sans faute <b>et en
              bande</b> — la noire ou la blanche doit toucher au moins une bande
              pendant le coup. Sinon, la partie est perdue.</li>
        </ul>
        """

    #___Insère le panneau des joueurs à droite de la table (page de jeu)___
    def _installer_panneau_joueurs(self):
        layout_v = self.page_8.layout()
        if layout_v is None:
            return
        idx = layout_v.indexOf(self.tableBillard)
        if idx == -1:
            return
        # On retire la table du layout vertical pour la replacer dans une ligne
        layout_v.takeAt(idx)
        ligne = QHBoxLayout()
        ligne.setContentsMargins(0, 0, 0, 0)
        ligne.setSpacing(8)
        ligne.addWidget(self.tableBillard, 1)       # la table prend l'espace restant
        self.panneau = PanneauJoueurs(self.page_8)
        ligne.addWidget(self.panneau, 0)            # panneau à largeur fixe, à droite
        layout_v.insertLayout(idx, ligne)

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

        # Branche le panneau latéral sur la partie en cours
        if self.panneau is not None:
            self.panneau.rafraichir(self.jeu)

    #___Coup déclenché par clic sur la table___
    def _coup_par_clic(self, angle_rad):
        if self.timer.isActive():
            return
        if self.jeu is None or self.jeu.est_termine():
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

            # Partie terminée : on annonce le résultat et on ne réarme rien
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

            # Met à jour le panneau (billes rentrées, tour, faute)
            if self.panneau is not None:
                self.panneau.rafraichir()

            # Blanche en main (après une faute) : le joueur la replace d'abord
            if self.jeu.blanche_en_main:
                self.jeu.blanche_en_main = False        # consommé
                self.Label_jeu.setText(
                    f"{joueur.nom} : placez la blanche sur la ligne, puis visez vers l'avant"
                )
                self.tableBillard.commencer_placement()
            else:
                self.Label_jeu.setText(f"Au tour de {joueur.nom}")
                self.tableBillard.visee_active = True

            self.tableBillard.update()

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


