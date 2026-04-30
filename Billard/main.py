# main.py
from Billard import bille, table
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from interfacepy import FenetreDebut
from jeu import Jeu
import sys


def main():

    print("=== Billard ===")
    nom1 = input("Nom du joueur 1 : ")
    nom2 = input("Nom du joueur 2 : ")

    jeu = Jeu(nom1, nom2) #initialisation du jeu
    print(f"\nPartie lancée! {jeu.joueur_actuel().nom} commence.")

    nb_bille_empoche=0

    while not jeu.est_termine(): #boucle des tours

        joueur = jeu.joueur_actuel() #element de classe joueur
        print(f"\nTour de {joueur.nom}")
        try:
            angle = float(input("Angle (en degrés) : "))
            force = float(input("Force (0.0 à 1.0) : "))
        except ValueError:
            print("Valeur invalide, réessaie.")
            continue

        import math
        jeu.jouer_coup(math.radians(angle), force)

        # Simule quelques frames de physique
        for _ in range(200):
            jeu.mettre_a_jour()

            if jeu.table.est_arretee():
                break
        if jeu.nb_bille_rentre()==nb_bille_empoche:
            jeu._changer_tour()
        else:
            nb_bille_empoche=jeu.nb_bille_rentre()

        jeu.sauvegarder()
        print(f"  {jeu.joueurs[0]}")
        print(f"  {jeu.joueurs[1]}")

    if jeu.gagnant:
        print(f"\n {jeu.gagnant.nom} a gagné en {jeu.nb_coups} coups !")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = FenetreDebut()
    fenetre.show()
    sys.exit(app.exec())
    main()