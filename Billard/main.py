
import sys
from PyQt6.QtWidgets import QApplication
from interfacepy import FenetreDebut


if __name__ == "__main__":
    # Création de l'application Qt (obligatoire avant tout widget)
    app = QApplication(sys.argv)
    # Création de la fenêtre principale
    fenetre = FenetreDebut()
    # Affichage en mode plein écran (avec barre de titre)
    fenetre.showMaximized()
    # Lancement de la boucle d'événements Qt (bloquant jusqu'à fermeture)
    sys.exit(app.exec())