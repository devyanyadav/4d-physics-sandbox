import numpy as np
from rotation import *

class Camera():
    def __init__(self):
        self.orientation = np.array([[1,0,0,0],
                               [0,1,0,0],
                               [0,0,1,0],
                               [0,0,0,1]])
        self.position = np.array([0,0,0,0],dtype=float)

    def _travel(self, axis, distance):
        """Move `distance` along one of the camera's OWN axes (0=x, 1=y, 2=z, 3=w)."""
        step = np.zeros(4)
        step[axis] = distance                        # 1. build the step in the camera's own axes
        world_step = step @ self.orientation         # 2. turn it into a world-space step
        self.position = self.position + world_step   # 3. add it to the position
        return self.position

    def travel_x(self, constant):
        return self._travel(0, constant)

    def travel_y(self, constant):
        return self._travel(1, constant)

    def travel_z(self, constant):
        return self._travel(2, constant)

    def travel_w(self, constant):   # unused now that w-translation is unbound; safe to delete
        return self._travel(3, constant)


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
        return self.orientation
    def direction_yw(self, theta):
        R = yw_rotation_matrix(theta)
        self.orientation = self.orientation @ R
        return self.orientation

    def direction_zw(self, theta):
        R = zw_rotation_matrix(theta)
        self.orientation = self.orientation @ R
        return self.orientation

    def default(self):
         self.orientation = np.array([[1,0,0,0],
                                   [0,1,0,0],
                                   [0,0,1,0],
                                   [0,0,0,1]])
            