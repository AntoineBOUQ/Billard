# son.py
import numpy as np
import sounddevice as sd
import threading


class GestionnaireSon:
    """
    Gère les sons de collision du billard via sounddevice.
    Le volume est proportionnel à la vitesse du choc.
    """

    def __init__(self):
        try:
            self.frequence = 44100
            self.volume_min = 0.1
            self.volume_max = 1.0
            # Test rapide pour vérifier que sounddevice fonctionne
            sd.query_devices()
            self.actif = True
            print("Son initialisé avec succès")
        except Exception as e:
            print(f"Son désactivé : {e}")
            self.actif = False

    def _jouer_signal(self, signal, volume):
        """Joue un signal audio dans un thread séparé pour ne pas bloquer le jeu."""
        def _play():
            try:
                sd.play(signal * volume, self.frequence)
            except Exception:
                pass
        threading.Thread(target=_play, daemon=True).start()

    def _generer_son_bille_bille(self, volume):
        """Son court et claquant — choc entre deux billes."""
        duree = 0.08
        t = np.linspace(0, duree, int(self.frequence * duree))
        signal = np.sin(2 * np.pi * 1200 * t)
        enveloppe = np.exp(-t * 40)
        signal = (signal * enveloppe).astype(np.float32)
        return signal

    def _generer_son_bille_bande(self, volume):
        """Son plus grave — rebond sur une bande."""
        duree = 0.15
        t = np.linspace(0, duree, int(self.frequence * duree))
        signal = np.sin(2 * np.pi * 400 * t)
        enveloppe = np.exp(-t * 15)
        signal = (signal * enveloppe).astype(np.float32)
        return signal

    def jouer_collision_billes(self, vitesse_relative):
        """
        Joue le son de choc entre deux billes.

        Args:
            vitesse_relative: magnitude du choc (float)
        """
        if not self.actif:
            return
        volume = self._calculer_volume(vitesse_relative)
        if volume < self.volume_min:
            return
        signal = self._generer_son_bille_bille(volume)
        self._jouer_signal(signal, volume)

    def jouer_collision_bande(self, vitesse):
        """
        Joue le son de rebond sur une bande.

        Args:
            vitesse: vitesse de la bille au moment du rebond (float)
        """
        if not self.actif:
            return
        volume = self._calculer_volume(vitesse)
        if volume < self.volume_min:
            return
        signal = self._generer_son_bille_bande(volume)
        self._jouer_signal(signal, volume)

    def _calculer_volume(self, vitesse):
        """
        Convertit une vitesse en volume entre 0 et 1.

        Args:
            vitesse: vitesse du choc
        Returns:
            volume entre 0.0 et 1.0
        """
        vitesse_max = 20.0
        volume = min(vitesse / vitesse_max, 1.0)
        return round(volume, 2)