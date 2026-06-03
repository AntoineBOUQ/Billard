# son.py
import pygame
import numpy as np


class GestionnaireSon:
    """
    Gère les sons de collision du billard.
    Le volume est proportionnel à la vitesse du choc.
    """

    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.volume_min = 0.1  # seuil minimum pour jouer un son
        self.volume_max = 1.0

        # Génère les sons synthétiques au démarrage
        self.son_bille_bille = self._generer_son_bille_bille()
        self.son_bille_bande = self._generer_son_bille_bande()

    def _generer_son_bille_bille(self):
        """
        Génère un son de choc entre deux billes —
        son court et claquant, fréquence haute.
        """
        frequence = 44100
        duree = 0.08  # 80ms
        t = np.linspace(0, duree, int(frequence * duree))

        # Onde sinusoïdale avec décroissance rapide
        signal = np.sin(2 * np.pi * 1200 * t)
        # Enveloppe : attaque immédiate, décroissance exponentielle
        enveloppe = np.exp(-t * 40)
        signal = signal * enveloppe

        # Normalise et convertit en int16
        signal = (signal * 32767).astype(np.int16)
        # Stéréo
        signal_stereo = np.column_stack([signal, signal])

        son = pygame.sndarray.make_sound(signal_stereo)
        return son

    def _generer_son_bille_bande(self):
        """
        Génère un son de rebond sur la bande —
        son plus grave et plus long.
        """
        frequence = 44100
        duree = 0.15  # 150ms
        t = np.linspace(0, duree, int(frequence * duree))

        # Fréquence plus basse pour la bande
        signal = np.sin(2 * np.pi * 400 * t)
        # Décroissance plus lente
        enveloppe = np.exp(-t * 15)
        signal = signal * enveloppe

        signal = (signal * 32767).astype(np.int16)
        signal_stereo = np.column_stack([signal, signal])

        son = pygame.sndarray.make_sound(signal_stereo)
        return son

    def jouer_collision_billes(self, vitesse_relative):
        """
        Joue le son de choc entre deux billes.

        Args:
            vitesse_relative: magnitude du choc (float)
        """
        volume = self._calculer_volume(vitesse_relative)
        if volume < self.volume_min:
            return
        self.son_bille_bille.set_volume(volume)
        self.son_bille_bille.play()

    def jouer_collision_bande(self, vitesse):
        """
        Joue le son de rebond sur une bande.

        Args:
            vitesse: vitesse de la bille au moment du rebond (float)
        """
        volume = self._calculer_volume(vitesse)
        if volume < self.volume_min:
            return
        self.son_bille_bande.set_volume(volume)
        self.son_bille_bande.play()

    def _calculer_volume(self, vitesse):
        """
        Convertit une vitesse en volume entre 0 et 1.

        Args:
            vitesse: vitesse du choc
        Returns:
            volume entre 0.0 et 1.0
        """
        vitesse_max = 20.0  # vitesse max possible dans le jeu
        volume = min(vitesse / vitesse_max, 1.0)
        return round(volume, 2)