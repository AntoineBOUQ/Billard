from table import Table
from joueur import Joueur
from stockage import Stockage
import random


class Jeu:
    #___Catégories de billes___
    PLEINES = set(range(1, 8))      # billes 1 à 7
    RAYEES = set(range(9, 16))      # billes 9 à 15
    NOIRE = 8                       # bille noire

    #___Initialisation___
    def __init__(self, nom_joueur1: str, nom_joueur2: str):
        self.table = Table()                            # table logique du jeu
        self.table_billard = None                       # widget visuel (relié par l'interface)
        self.joueurs = [Joueur(nom_joueur1), Joueur(nom_joueur2)]   # liste des joueurs
        self.tour_actuel = random.randint(0, 1)         # tirage au sort du premier joueur
        self.nb_coups = 0                               # coups joués au total
        self.gagnant = None                             # joueur vainqueur (None tant que pas fini)
        self.raison_fin = ""                            # explication de la fin de partie
        self.stockage = Stockage()                      # gestionnaire de sauvegarde SQLite
        self.table_ouverte = True                       # aucun groupe attribué au départ
        self.coups_restants = 1                         # coups garantis au joueur courant (2 après une faute)
        self.blanche_en_main = False                    # True quand la blanche doit être replacée à la main
        self.faute_joueur = None                        # index du joueur ayant fait la dernière faute (None sinon)
        # NB : plus de _distribuer_billes() — les groupes se gagnent en jouant.

    #___Récupération du joueur dont c'est le tour___
    def joueur_actuel(self):
        return self.joueurs[self.tour_actuel]

    #___Récupération de l'adversaire___
    def _adversaire(self):
        return self.joueurs[1 - self.tour_actuel]

    #___Le joueur courant joue un coup___
    def jouer_coup(self, angle, force):
        if self.gagnant is not None:        # partie déjà terminée : on ignore
            return
        # On réinitialise le suivi des billes empochées AVANT le coup
        self.table.nouveau_coup()

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
        if self.table_billard is not None:
            self.table_billard.update()

    #___Fin de coup : appelée quand toutes les billes se sont arrêtées___
    def fin_de_coup(self):
        if self.gagnant is not None:        # sécurité : partie déjà finie
            return

        joueur = self.joueur_actuel()
        adversaire = self._adversaire()

        # Bilan du coup
        empochees = self.table.empochees_ce_coup            # numéros (ordre de chute)
        blanche_rentree = self.table.blanche_empochee_ce_coup
        noire_rentree = self.NOIRE in empochees
        billes_couleur = [n for n in empochees if n != self.NOIRE]

        # ── Fautes ──
        # a) empocher la blanche ;
        # b) la blanche ne touche AUCUNE bille ;
        # c) la 1re bille touchée appartient au groupe ADVERSE ;
        # d) la 1re bille touchée est la NOIRE alors qu'on n'y a pas encore droit ;
        # e) empocher une bille du groupe ADVERSE.
        # (c) et (e) ne s'appliquent que table fermée : sur table ouverte toute
        # bille de couleur est jouable.
        premiere = self.table.premiere_bille_touchee        # None = aucune bille touchée
        a_droit_noire = (joueur.groupe is not None and self._groupe_termine(joueur))

        faute = blanche_rentree
        if premiere is None:                                # (b) aucun contact
            faute = True
        if premiere == self.NOIRE and not a_droit_noire:    # (d) noire avant d'y avoir droit
            faute = True
        if not self.table_ouverte and adversaire.groupe is not None:
            groupe_adverse = self._set_groupe(adversaire.groupe)
            if premiere in groupe_adverse:                  # (c) mauvaise bille touchée
                faute = True
            if any(n in groupe_adverse for n in billes_couleur):  # (e) mauvaise bille empochée
                faute = True

        # Mémorise qui vient de commettre une faute (pour l'affichage), None sinon
        self.faute_joueur = self.tour_actuel if faute else None

        #___1. La noire est tombée → fin de partie (victoire ou défaite)___
        if noire_rentree:
            self._gerer_noire(joueur, adversaire, faute)
            self.sauvegarder()
            return

        #___2. Scratch : la blanche est tombée → elle repart "en main"___
        if blanche_rentree:
            blanche = self.table.get_bille_blanche()
            blanche.reinitialiser(200, 250)     # position de départ sur la ligne de service
            self.blanche_en_main = True         # l'adversaire la repositionnera lui-même

        #___3. Attribution éventuelle d'un groupe + coup légal ?___
        a_empoche_son_groupe = False
        if billes_couleur and not faute:
            # Table ouverte : la 1re bille de couleur empochée fixe les groupes
            if self.table_ouverte:
                self._attribuer_groupe(joueur, billes_couleur)
            # A-t-on empoché au moins une bille de SON propre groupe ?
            if joueur.groupe is not None:
                groupe_set = self._set_groupe(joueur.groupe)
                a_empoche_son_groupe = any(n in groupe_set for n in billes_couleur)

        #___4. Suite du coup : qui joue ensuite, et avec combien de coups ?___
        if faute:
            # Faute (blanche empochée OU bille adverse empochée) → l'adversaire
            # prend la main avec DEUX coups. La blanche n'est remise "en main" que
            # si c'est elle qui est tombée (géré à l'étape 2 ci-dessus).
            # Le 2e coup ne sera accordé que si le 1er coup de l'adversaire est propre.
            self._passer_la_main(coups=2)
        elif a_empoche_son_groupe:
            # Coup gagnant : on rejoue normalement (un éventuel coup bonus est consommé)
            self.coups_restants = 1
        else:
            # Coup légal mais aucune bille perso empochée → on consomme un coup
            self.coups_restants -= 1
            if self.coups_restants <= 0:
                self._passer_la_main(coups=1)
            # sinon : 2e coup offert par la faute précédente, le joueur rejoue

        self.sauvegarder()

    #___Gestion de l'empochage de la noire___
    def _gerer_noire(self, joueur, adversaire, faute):
        # Cas spécial : noire rentrée dès le tout premier coup → victoire immédiate
        if self.nb_coups == 1:
            self.gagnant = joueur
            self.raison_fin = f"{joueur.nom} a empoché la noire dès le premier coup !"
            return

        # A-t-on le droit de jouer la noire ? (son propre groupe est terminé)
        droit = (joueur.groupe is not None and self._groupe_termine(joueur))

        # Règle spéciale : si les DEUX groupes sont terminés, la noire doit être
        # jouée "en bande" (la noire OU la blanche doit toucher au moins une bande).
        deux_groupes_finis = droit and self._groupe_termine(adversaire)
        bande_ok = self.table.noire_ou_blanche_en_bande()
        bande_requise_ok = (not deux_groupes_finis) or bande_ok

        if not faute and droit and bande_requise_ok:
            self.gagnant = joueur
            if deux_groupes_finis:
                self.raison_fin = f"{joueur.nom} a rentré la noire en bande → victoire !"
            else:
                self.raison_fin = f"{joueur.nom} a rentré la noire après son groupe → victoire !"
        else:
            # Noire empochée illégalement → défaite
            self.gagnant = adversaire
            if faute and self.table.blanche_empochee_ce_coup:
                self.raison_fin = (f"{joueur.nom} a empoché la noire ET la blanche "
                                   f"→ victoire de {adversaire.nom}.")
            elif faute:
                self.raison_fin = (f"{joueur.nom} a empoché la noire en commettant une faute "
                                   f"→ victoire de {adversaire.nom}.")
            elif deux_groupes_finis and not bande_ok:
                self.raison_fin = (f"{joueur.nom} a rentré la noire sans bande "
                                   f"→ victoire de {adversaire.nom}.")
            else:
                self.raison_fin = (f"{joueur.nom} a rentré la noire trop tôt "
                                   f"→ victoire de {adversaire.nom}.")

    #___Attribution d'un groupe quand la table est ouverte___
    def _attribuer_groupe(self, joueur, billes_couleur):
        # Le groupe est déterminé par la PREMIÈRE bille de couleur empochée
        premiere = billes_couleur[0]
        groupe = "pleines" if premiere in self.PLEINES else "rayées"

        adversaire = self._adversaire()
        joueur.groupe = groupe
        adversaire.groupe = "rayées" if groupe == "pleines" else "pleines"

        # On remplit billes_a_empocher pour rester cohérent avec le reste du code
        joueur.billes_a_empocher = self._billes_du_groupe(joueur.groupe)
        adversaire.billes_a_empocher = self._billes_du_groupe(adversaire.groupe)

        self.table_ouverte = False      # les groupes sont désormais fixés

    #___Outils sur les groupes___
    def _set_groupe(self, groupe):
        return self.PLEINES if groupe == "pleines" else self.RAYEES

    def _billes_du_groupe(self, groupe):
        return [self._bille_par_numero(n) for n in sorted(self._set_groupe(groupe))]

    def _bille_par_numero(self, numero):
        for b in self.table.billes:
            if getattr(b, "numero", None) == numero:
                return b
        return None

    #___Le groupe du joueur est-il entièrement empoché ?___
    def _groupe_termine(self, joueur):
        if joueur.groupe is None:
            return False
        return all(b.empochee for b in self._billes_du_groupe(joueur.groupe))

    #___Passage de la main à l'adversaire (avec un nombre de coups donné)___
    def _passer_la_main(self, coups=1):
        self.tour_actuel = 1 - self.tour_actuel
        self.coups_restants = coups

    #___La partie est-elle finie ?___
    def est_termine(self):
        return self.gagnant is not None

    #___Sauvegarde dans la base SQLite___
    def sauvegarder(self):
        self.stockage.sauvegarder_etat(self)