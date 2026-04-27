# main.py
from jeu import Jeu

def main():
    """Point d'entrée du programme — version console pour tester."""
    print("=== Billard ===")
    nom1 = input("Nom du joueur 1 : ")
    nom2 = input("Nom du joueur 2 : ")

    jeu = Jeu(nom1, nom2)
    print(f"\nPartie lancée ! {jeu.joueur_actuel().nom} commence.")
    print("(Interface graphique PyQt5 à venir...)\n")

    # Boucle de test en console
    while not jeu.est_termine():
        joueur = jeu.joueur_actuel()
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

        jeu.sauvegarder()
        print(f"  {jeu.joueurs[0]}")
        print(f"  {jeu.joueurs[1]}")

    if jeu.gagnant:
        print(f"\n🎉 {jeu.gagnant.nom} a gagné en {jeu.nb_coups} coups !")

if __name__ == "__main__":
    main()