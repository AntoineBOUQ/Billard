# test/test_bille.py
import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Billard'))

from bille import Bille, BilleBlanche, BilleNumerotee


class TestBille(unittest.TestCase):

    def setUp(self):
        self.bille = Bille(100.0, 200.0)

    def test_initialisation_position(self):
        self.assertEqual(self.bille.x, 100.0)
        self.assertEqual(self.bille.y, 200.0)

    def test_initialisation_vitesse_nulle(self):
        self.assertEqual(self.bille.vitesse_x, 0.0)
        self.assertEqual(self.bille.vitesse_y, 0.0)

    def test_deplacer_met_a_jour_position(self):
        self.bille.vitesse_x = 10.0
        self.bille.vitesse_y = 5.0
        self.bille.deplacer()
        self.assertAlmostEqual(self.bille.x, 110.0)
        self.assertAlmostEqual(self.bille.y, 205.0)

    def test_deplacer_applique_frottement(self):
        self.bille.vitesse_x = 10.0
        self.bille.deplacer()
        self.assertAlmostEqual(self.bille.vitesse_x, 9.8)

    def test_est_en_mouvement_vrai(self):
        self.bille.vitesse_x = 5.0
        self.assertTrue(self.bille.est_en_mouvement())

    def test_est_en_mouvement_faux(self):
        self.assertFalse(self.bille.est_en_mouvement())


class TestBilleBlanche(unittest.TestCase):

    def setUp(self):
        self.bille_b = BilleBlanche(200.0, 250.0)

    def test_heritage_bille(self):
        self.assertIsInstance(self.bille_b, Bille)

    def test_reinitialiser_position(self):
        self.bille_b.x = 500.0
        self.bille_b.empochee = True
        self.bille_b.reinitialiser(200.0, 250.0)
        self.assertEqual(self.bille_b.x, 200.0)
        self.assertFalse(self.bille_b.empochee)

    def test_reinitialiser_vitesse_nulle(self):
        self.bille_b.vitesse_x = 10.0
        self.bille_b.reinitialiser(200.0, 250.0)
        self.assertEqual(self.bille_b.vitesse_x, 0.0)


class TestBilleNumerotee(unittest.TestCase):

    def setUp(self):
        self.bille_n = BilleNumerotee(300.0, 250.0, 5, "orange")

    def test_heritage_bille(self):
        self.assertIsInstance(self.bille_n, Bille)

    def test_numero_correct(self):
        self.assertEqual(self.bille_n.numero, 5)

    def test_couleur_correcte(self):
        self.assertEqual(self.bille_n.couleur, "orange")


if __name__ == "__main__":
    unittest.main()