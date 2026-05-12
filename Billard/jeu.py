
from table import Table
from joueur import Joueur
from stockage import Stockage
import random


class Jeu:

    #___Initialisation___
    def __init__(self, nom_joueur1: str, nom_joueur2: str):
        self.table = Table()                            # table logique du jeu
        self.table_billard = None                       # widget visuel (relié par l'interface)
        self.joueurs = [Joueur(nom_joueur1), Joueur(nom_joueur2)]   # liste des joueurs
        self.tour_actuel = random.randint(0, 1)         # tirage au sort du premier joueur
        self.nb_coups = 0                               # coups joués au total
        self.gagnant = None                             # joueur vainqueur (None tant que pas fini)
        self.stockage = Stockage()                      # gestionnaire de sauvegarde SQLite
        self.nb_bille_empoche = 0                       # nb de billes empochées avant le coup en cours
        self._distribuer_billes()                       # attribue les billes aux joueurs

    #___Association des billes aux joueurs___
    def _distribuer_billes(self):
        # On exclut la blanche (index 0)
        billes_numerotees = self.table.billes[1:]
        # Joueur 0 : billes 1 à 7 (pleines)
        self.joueurs[0].billes_a_empocher = billes_numerotees[:7]
        # Joueur 1 : billes 9 à 15 (rayées) — la noire (n°8) n'est pour personne
        self.joueurs[1].billes_a_empocher = billes_numerotees[7:14]

    #___Récupération du joueur dont c'est le tour___
    def joueur_actuel(self):
        return self.joueurs[self.tour_actuel]

    #___Le joueur courant joue un coup___
    def jouer_coup(self, angle, force):
        # On mémorise le nombre de billes empochées AVANT le coup
        # (utile pour décider si on change de tour à la fin)
        self.nb_bille_empoche = self.nb_bille_rentre()

        joueur = self.joueur_actuel()
        bille_blanche = self.table.get_bille_blanche()
        # Délégation : le joueur sait comment jouer son coup (via sa queue)
        joueur.jouer_coup(bille_blanche, angle, force)
        self.nb_coups += 1

    #___Mise à jour physique d'une frame___
    def mettre_a_jour(self):
        # Une étape de simulation : déplacer, gérer les chocs, redessiner
        self.table.deplacer_toutes_billes()
        self.table.detecter_collisions()
        # On déclenche un repaint si la vue est branchée
        if self.table_billard is not None:
            self.table_billard.update()

    #___Fin de coup : appelée quand toutes les billes se sont arrêtées___
    def fin_de_coup(self):
        # 1. Gestion du scratch : si la blanche est tombée, on la replace
        blanche = self.table.get_bille_blanche()
        if blanche.empochee:
            blanche.reinitialiser(200, 250)

        # 2. Changement de tour : on alterne sauf si le joueur a empoché au moins
        # une bille pendant le coup (récompense classique au billard)
        if self.nb_bille_rentre() == self.nb_bille_empoche:
            self._changer_tour()
        else:
            self.nb_bille_empoche = self.nb_bille_rentre()

        # 3. Vérifie si quelqu'un a gagné
        self._verifier_victoire()
        # 4. Sauvegarde de l'état dans la base SQLite
        self.sauvegarder()

    #___Accesseur du compteur de billes rentrées___
    def nb_bille_rentre(self):
        return self.table._nb_bille_rentre()

    #___Alternance des tours (0 → 1 → 0 → 1 ...)___
    def _changer_tour(self):
        self.tour_actuel = 1 - self.tour_actuel

    #___Vérification de victoire___
    def _verifier_victoire(self):
        # Le premier joueur qui a empoché toutes SES billes gagne
        for joueur in self.joueurs:
            if joueur.a_gagne():
                self.gagnant = joueur

    #___La partie est-elle finie ?___
    def est_termine(self):
        return self.gagnant is not None

    #___Sauvegarde dans la base SQLite___
    def sauvegarder(self):
        self.stockage.sauvegarder_etat(self)