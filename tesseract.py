import numpy as np
import itertools
from functions import edge_list,rotate_xw

class Tesseract():

    def __init__(self,x,y,z,w):
        self.position = np.array([x,y,z,w]) 
        self.vertices = np.array(list(itertools.product([-1,1],repeat=4)))


tess = Tesseract(0,0,0,1)
result = edge_list(tess.vertices)
rotate_xw(tess.vertices,6)

                            
