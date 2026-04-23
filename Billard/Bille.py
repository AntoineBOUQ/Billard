import numpy as np


class Bille():
    def __init__(self,xcoord,ycoord,num,billard,famille):
        self.coord=xcoord, ycoord
        self.num=num
        self.billard=billard
        self._empoche=False
        self.famille=famille

    @property
    def empoche(self):

        return self._empoche

