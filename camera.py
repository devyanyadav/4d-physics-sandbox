import numpy as np
from rotation import *

class Camera():
    def __init__(self):
        self.orientation = np.array([[1,0,0,0],
                               [0,1,0,0],
                               [0,0,1,0],
                               [0,0,0,1]])
        self.position = np.array([0,0,0,0],dtype=float)

    def travel_x(self,constant):
        new_x = self.position[0] + constant
        self.position[0] = new_x
        return self.position

    def travel_y(self,constant):
            new_y = self.position[1] + constant
            self.position[1] = new_y
            return self.position
            

    def travel_z(self,constant):
         new_z = self.position[2] + constant 
         self.position[2] = new_z
         return self.position

    def travel_w(self,constant): 
         new_w = self.position[3] + constant
         self.position[3] = new_w
         return self.position

    def direction_xy(self, theta):
        R = xy_rotation_matrix(theta)
        self.orientation = self.orientation @ R

    def direction_xz(self, theta):
        R = xz_rotation_matrix(theta)
        self.orientation = self.orientation @ R
        return self.orientation

    def direction_yz(self, theta):
        R = yz_rotation_matrix(theta)
        self.orientation = self.orientation @ R
        return self.orientation

    def direction_xw(self, theta):
        R = xw_rotation_matrix(theta)
        self.orientation = self.orientation @ R

    def direction_yw(self, theta):
        R = yw_rotation_matrix(theta)
        self.orientation = self.orientation @ R

    def direction_zw(self, theta):
        R = zw_rotation_matrix(theta)
        self.orientation = self.orientation @ R

    def default(self):
         self.orienatation = np.array([[1,0,0,0],
                                   [0,1,0,0],
                                   [0,0,1,0],
                                   [0,0,0,1]])
            