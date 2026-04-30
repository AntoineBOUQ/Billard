import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox

class FenetreDebut(QMainWindow):
    def __init__(self):
        super().__init__() #hérite de la class QMainWindow
        uic.loadUi("interface.ui", self)#lie les widgets au self
        self.Boutton_Quitter.clicked.connect(self.close) #connecte self.close à Boutton_Quitter
        self.pages.setCurrentIndex(0)
        self.Boutton_regle.clicked.connect(self.Fenetreregle)
        self.Boutton_Retour_regle.clicked.connect(self.Fenetredebut)
    def Fenetreregle(self):
        return self.pages.setCurrentIndex(1)
    def Fenetredebut(self):
        return self.pages.setCurrentIndex(0)
    def closeEvent(self, event): #Methode de QMainWindow qui reconnait l'evenement "fermeture"
        reponse = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir quitter ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if reponse == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()









if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = FenetreDebut()
    fenetre.show()
    sys.exit(app.exec())