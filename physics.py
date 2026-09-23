import numpy as np
import sympy as sp



G = 1 # universal constant of gravity
#testing
position_tesseracts = np.array([[0,0,0,0],[1,3,9,2]])
tesseract_velocities = np.array([
    [-1.0, 1.0, 0.0, 4.0],
    [0.0, -1.0, 0.0, 0.0]
])
mass_of_tesseracts = [5,8] #this array represents the mass of different tesseracts
charge_of_tesseracts = [-1,1] #this array represents the charge of different tesseracts


#calculation of force 
n = len(position_tesseracts)
force_tesseracts = []

for i in range(n):
    force_accumulated = 0
    for j in range(n):
        if j == i : 
            continue
        # calculating r(straight line distance between two objects)
        seperation = position_tesseracts[j] - position_tesseracts[i]
        r = np.sqrt(np.sum(seperation**2))
        # calculating gravitational force exerted by second object on first object
        force = (G*mass_of_tesseracts[j]*mass_of_tesseracts[i])/r**4 * seperation
        force_accumulated += force
    force_tesseracts.append(force_accumulated)

#calculating acceleration 
#F=ma
acceleration_tesseracts = []
for i in range(len(force_tesseracts)):
    acceleration = force_tesseracts[i]/mass_of_tesseracts[i]
    acceleration_tesseracts.append(acceleration)
