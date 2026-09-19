import numpy as np
import itertools
from functions import edge_list


class Tesseract():

    def __init__(self,x,y,z,w):
        self.position = np.array([x,y,z,w]) 
        self.vertices = np.array(list(itertools.product([-1,1],repeat=4)))






                            
