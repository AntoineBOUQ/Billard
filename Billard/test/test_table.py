# test/test_table.py
import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Billard'))

from table import Table
from bille import Bille, BilleBlanche, BilleNumerotee


class TestTable(unittest.TestCase):

    def setUp(self):
        """Crée une table de test avant chaque test."""
        self.table = Table()

    def test_nombre_billes(self):
        """Vérifie que la table contient bien 16 billes."""
        self.assertEqual(len(self.table.billes), 16)

    def test_premiere_bille_est_blanche(self):
        """Vérifie que la première bille est la bille blanche."""
        self.assertIsInstance(self.table.billes[0], BilleBlanche)

    def test_billes_numerotees(self):
        """Vérifie que les billes 1 à 15 sont bien numérotées."""
        for i, bille in enumerate(self.table.billes[1:], start=1):
            self.assertIsInstance(bille, BilleNumerotee)
            self.assertEqual(bille.numero, i)

    def test_table_arretee_au_depart(self):
        """Vérifie que toutes les billes sont immobiles au départ."""
        self.assertTrue(self.table.est_arretee())

    def test_table_non_arretee_avec_mouvement(self):
        """Vérifie que est_arretee() retourne False si une bille bouge."""
        self.table.billes[0].vitesse_x = 5.0
        self.assertFalse(self.table.est_arretee())

    def test_empochage_bille(self):
        """Vérifie qu'une bille placée sur un trou est empochée."""
        bille = self.table.billes[1]
        tx, ty, _ = self.table.trous[0]
        bille.x = tx
        bille.y = ty
        self.table._verifier_trou(bille)
        self.assertTrue(bille.empochee)

    def test_empochage_arrete_bille(self):
        """Vérifie que la vitesse est nulle après empochage."""
        bille = self.table.billes[1]
        bille.vitesse_x = 5.0
        bille.vitesse_y = 3.0
        tx, ty, _ = self.table.trous[0]
        bille.x = tx
        bille.y = ty
        self.table._verifier_trou(bille)
        self.assertEqual(bille.vitesse_x, 0.0)
        self.assertEqual(bille.vitesse_y, 0.0)

    def test_rebond_bord_gauche(self):
        """Vérifie le rebond sur le bord gauche."""
        bille = self.table.billes[0]
        bille.x = bille.rayon - 1
        bille.vitesse_x = -5.0
        self.table._rebondir_sur_bandes(bille)
        self.assertGreater(bille.vitesse_x, 0)

    def test_rebond_bord_droit(self):
        """Vérifie le rebond sur le bord droit."""
        bille = self.table.billes[0]
        bille.x = self.table.largeur - bille.rayon + 1
        bille.vitesse_x = 5.0
        self.table._rebondir_sur_bandes(bille)
        self.assertLess(bille.vitesse_x, 0)

    def test_collision_entre_billes(self):
        """Vérifie que deux billes en collision échangent leurs vitesses."""
        b1 = self.table.billes[0]
        b2 = self.table.billes[1]
        b1.x, b1.y = 100.0, 250.0
        b2.x, b2.y = 100.0 + b1.rayon + b2.rayon - 1, 250.0
        b1.vitesse_x = 10.0
        b2.vitesse_x = 0.0
        self.table._resoudre_collision(b1, b2)
        self.assertLess(b1.vitesse_x, 10.0)
        self.assertGreater(b2.vitesse_x, 0.0)

    def test_compteur_billes_rentrees(self):
        """Vérifie que le compteur s'incrémente quand une bille est empochée."""
        bille = self.table.billes[1]
        tx, ty, _ = self.table.trous[0]
        bille.x = tx
        bille.y = ty
        self.table._verifier_trou(bille)
        self.assertEqual(self.table.nb_bille_rentre, 1)

    def test_blanche_ne_compte_pas(self):
        """Vérifie que la bille blanche n'incrémente pas le compteur."""
        blanche = self.table.billes[0]
        tx, ty, _ = self.table.trous[0]
        blanche.x = tx
        blanche.y = ty
        self.table._verifier_trou(blanche)
        self.assertEqual(self.table.nb_bille_rentre, 0)


if __name__ == "__main__":
    unittest.main()