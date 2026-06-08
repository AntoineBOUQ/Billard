# test/test_joueur.py
import unittest
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Billard'))

from joueur import Joueur
from bille import BilleBlanche, BilleNumerotee
from queue import Queue


class TestJoueur(unittest.TestCase):

    def setUp(self):
        """Crée un joueur de test avec des billes assignées."""
        self.joueur = Joueur("Arthur")
        self.bille_blanche = BilleBlanche(200.0, 250.0)
        # Assigne 3 billes numérotées au joueur
        self.joueur.billes_a_empocher = [
            BilleNumerotee(300.0, 250.0, 1, "jaune"),
            BilleNumerotee(320.0, 250.0, 2, "bleu"),
            BilleNumerotee(340.0, 250.0, 3, "rouge"),
        ]

    def test_initialisation_nom(self):
        """Vérifie que le nom est correctement initialisé."""
        self.assertEqual(self.joueur.nom, "Arthur")

    def test_initialisation_score_zero(self):
        """Vérifie que le score initial est 0."""
        self.assertEqual(self.joueur.score, 0)

    def test_initialisation_possede_queue(self):
        """Vérifie que le joueur possède bien une Queue."""
        self.assertIsInstance(self.joueur.queue, Queue)

    def test_ajouter_point_incremente_score(self):
        """Vérifie que ajouter_point() incrémente le score."""
        self.joueur.ajouter_point()
        self.assertEqual(self.joueur.score, 1)

    def test_ajouter_point_multiple(self):
        """Vérifie que plusieurs points s'accumulent correctement."""
        self.joueur.ajouter_point()
        self.joueur.ajouter_point()
        self.joueur.ajouter_point()
        self.assertEqual(self.joueur.score, 3)

    def test_a_gagne_faux_au_depart(self):
        """Vérifie que le joueur n'a pas gagné au départ."""
        self.assertFalse(self.joueur.a_gagne())

    def test_a_gagne_vrai_quand_toutes_empochees(self):
        """Vérifie que a_gagne() retourne True quand tout est empoché et groupe défini."""
        self.joueur.groupe = "pleines"  # ← groupe nécessaire
        for bille in self.joueur.billes_a_empocher:
            bille.empochee = True
        self.assertTrue(self.joueur.a_gagne())


    def test_jouer_coup_incremente_nb_coups(self):
        """Vérifie que jouer_coup() incrémente le compteur de coups."""
        self.joueur.jouer_coup(self.bille_blanche, 0.0, 0.5)
        self.assertEqual(self.joueur.nb_coups, 1)

    def test_jouer_coup_applique_vitesse(self):
        """Vérifie que jouer_coup() donne une vitesse à la bille blanche."""
        self.joueur.jouer_coup(self.bille_blanche, 0.0, 1.0)
        self.assertTrue(self.bille_blanche.est_en_mouvement())

    def test_joueur_sans_billes_a_gagne(self):
        """Vérifie que a_gagne() retourne False si la liste est vide."""
        self.joueur.groupe = "pleines"
        self.joueur.billes_a_empocher = []
        self.assertFalse(self.joueur.a_gagne())

    def test_a_gagne_faux_sans_groupe(self):
        """Vérifie que a_gagne() retourne False si aucun groupe n'est attribué."""
        self.joueur.groupe = None
        for bille in self.joueur.billes_a_empocher:
            bille.empochee = True
        self.assertFalse(self.joueur.a_gagne())


if __name__ == "__main__":
    unittest.main()