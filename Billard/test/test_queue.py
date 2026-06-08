# test/test_queue.py
import unittest
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Billard'))

from queue import Queue
from bille import BilleBlanche


class TestQueue(unittest.TestCase):

    def setUp(self):
        """Crée une queue et une bille blanche de test."""
        self.queue = Queue()
        self.bille = BilleBlanche(200.0, 250.0)

    def test_initialisation_angle(self):
        """Vérifie que l'angle initial est 0."""
        self.assertEqual(self.queue.angle, 0.0)

    def test_initialisation_force_max(self):
        """Vérifie que la force maximale est bien définie."""
        self.assertGreater(self.queue.force_max, 0)

    def test_viser_modifie_angle(self):
        """Vérifie que viser() modifie bien l'angle."""
        self.queue.viser(math.pi / 4)
        self.assertAlmostEqual(self.queue.angle, math.pi / 4)

    def test_viser_angle_negatif(self):
        """Vérifie que viser() accepte un angle négatif."""
        self.queue.viser(-math.pi / 3)
        self.assertAlmostEqual(self.queue.angle, -math.pi / 3)

    def test_frapper_donne_vitesse(self):
        """Vérifie que frapper() applique une vitesse non nulle."""
        self.queue.viser(0.0)
        self.queue.frapper(self.bille, 1.0)
        self.assertNotEqual(self.bille.vitesse_x, 0.0)

    def test_frapper_force_nulle(self):
        """Vérifie qu'une force nulle ne bouge pas la bille."""
        self.queue.frapper(self.bille, 0.0)
        self.assertEqual(self.bille.vitesse_x, 0.0)
        self.assertEqual(self.bille.vitesse_y, 0.0)

    def test_frapper_angle_horizontal(self):
        """Vérifie la décomposition pour un angle horizontal."""
        self.queue.viser(0.0)
        self.queue.frapper(self.bille, 1.0)
        self.assertAlmostEqual(self.bille.vitesse_y, 0.0, places=5)
        self.assertGreater(self.bille.vitesse_x, 0.0)

    def test_frapper_angle_vertical(self):
        """Vérifie la décomposition pour un angle vertical."""
        self.queue.viser(math.pi / 2)
        self.queue.frapper(self.bille, 1.0)
        self.assertAlmostEqual(self.bille.vitesse_x, 0.0, places=5)
        self.assertGreater(self.bille.vitesse_y, 0.0)

    def test_frapper_limite_force_max(self):
        """Vérifie que la force est limitée à 1.0."""
        self.queue.viser(0.0)
        self.queue.frapper(self.bille, 999.0)
        self.assertLessEqual(self.bille.vitesse_x, self.queue.force_max)

    def test_frapper_force_negative(self):
        """Vérifie que la force négative est ramenée à 0."""
        self.queue.viser(0.0)
        self.queue.frapper(self.bille, -1.0)
        self.assertEqual(self.bille.vitesse_x, 0.0)


if __name__ == "__main__":
    unittest.main()