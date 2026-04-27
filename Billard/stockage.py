# stockage.py
import sqlite3
import json
from datetime import datetime


class Stockage:
    """
    Gère la sauvegarde et le chargement des parties de billard.
    Utilise SQLite pour la persistance des données.
    """

    def __init__(self, chemin_db: str = "billard.db"):
        """
        Initialise la connexion à la base de données.
        Crée les tables si elles n'existent pas encore.

        Args:
            chemin_db: chemin vers le fichier SQLite
        """
        self.chemin_db = chemin_db
        self._initialiser_db()

    def _initialiser_db(self):
        """Crée les tables nécessaires si elles n'existent pas."""
        with sqlite3.connect(self.chemin_db) as conn:
            conn.execute("""
                         CREATE TABLE IF NOT EXISTS parties
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             date
                             TEXT
                             NOT
                             NULL,
                             joueur1
                             TEXT
                             NOT
                             NULL,
                             joueur2
                             TEXT
                             NOT
                             NULL,
                             gagnant
                             TEXT,
                             nb_coups
                             INTEGER
                         )
                         """)
            conn.execute("""
                         CREATE TABLE IF NOT EXISTS scores
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             partie_id
                             INTEGER
                             NOT
                             NULL,
                             joueur
                             TEXT
                             NOT
                             NULL,
                             score
                             INTEGER
                             NOT
                             NULL,
                             FOREIGN
                             KEY
                         (
                             partie_id
                         ) REFERENCES parties
                         (
                             id
                         )
                             )
                         """)
            conn.execute("""
                         CREATE TABLE IF NOT EXISTS sauvegardes
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             date
                             TEXT
                             NOT
                             NULL,
                             etat_json
                             TEXT
                             NOT
                             NULL
                         )
                         """)

    def sauvegarder_partie(self, jeu) -> int:
        """
        Sauvegarde le résultat final d'une partie.

        Args:
            jeu: instance de la classe Jeu
        Returns:
            l'id de la partie insérée
        """
        with sqlite3.connect(self.chemin_db) as conn:
            curseur = conn.execute("""
                                   INSERT INTO parties (date, joueur1, joueur2, gagnant, nb_coups)
                                   VALUES (?, ?, ?, ?, ?)
                                   """, (
                                       datetime.now().isoformat(),
                                       jeu.joueurs[0].nom,
                                       jeu.joueurs[1].nom,
                                       jeu.gagnant.nom if jeu.gagnant else None,
                                       jeu.nb_coups
                                   ))
            partie_id = curseur.lastrowid

            # Sauvegarde les scores de chaque joueur
            for joueur in jeu.joueurs:
                conn.execute("""
                             INSERT INTO scores (partie_id, joueur, score)
                             VALUES (?, ?, ?)
                             """, (partie_id, joueur.nom, joueur.score))

            return partie_id

    def sauvegarder_etat(self, jeu) -> None:
        """
        Sauvegarde l'état complet d'une partie en cours (pour reprendre plus tard).
        Sérialise les positions des billes en JSON.

        Args:
            jeu: instance de la classe Jeu
        """
        # On transforme l'état du jeu en dictionnaire sérialisable
        etat = {
            "joueurs": [
                {"nom": j.nom, "score": j.score}
                for j in jeu.joueurs
            ],
            "billes": [
                {
                    "numero": b.numero if hasattr(b, "numero") else 0,
                    "x": b.x,
                    "y": b.y,
                    "empochee": b.empochee
                }
                for b in jeu.table.billes
            ],
            "tour": jeu.tour_actuel
        }

        with sqlite3.connect(self.chemin_db) as conn:
            conn.execute("""
                         INSERT INTO sauvegardes (date, etat_json)
                         VALUES (?, ?)
                         """, (datetime.now().isoformat(), json.dumps(etat)))

    def charger_dernier_etat(self) -> dict | None:
        """
        Charge la sauvegarde la plus récente.

        Returns:
            un dictionnaire avec l'état du jeu, ou None si aucune sauvegarde
        """
        with sqlite3.connect(self.chemin_db) as conn:
            curseur = conn.execute("""
                                   SELECT etat_json
                                   FROM sauvegardes
                                   ORDER BY id DESC LIMIT 1
                                   """)
            ligne = curseur.fetchone()
            if ligne:
                return json.loads(ligne[0])
            return None

    def get_classement(self) -> list[dict]:
        """
        Retourne le classement des joueurs par nombre de victoires.

        Returns:
            liste de dicts {"joueur": str, "victoires": int}
        """
        with sqlite3.connect(self.chemin_db) as conn:
            curseur = conn.execute("""
                                   SELECT gagnant, COUNT(*) as victoires
                                   FROM parties
                                   WHERE gagnant IS NOT NULL
                                   GROUP BY gagnant
                                   ORDER BY victoires DESC
                                   """)
            return [
                {"joueur": row[0], "victoires": row[1]}
                for row in curseur.fetchall()
            ]