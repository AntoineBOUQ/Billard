import numpy as np

class Billard(object):
    def __init__(self, billard,coords,fonction):
        self.nb_billard = billard
        self.__coords = coords
        self.fonction = fonction

    @property
    def trajectoire_bille(self ):
        return self.fonction

    @trajectoire_bille.setter
    def trajectoire_bille(self, trajectoire_bille):
        self.__fonction = trajectoire_bille

    def coords(self):
            return self.__coords

class Poche(Billard):






class Bande(Billard):







class tapis(Billard):

#Hola buenos dias