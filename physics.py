import numpy as np
import sympy as sp



G = 1 # universal constant of gravity
DT = 0.01  # fixed physics timestep, independent of render dt

#testing
position_tesseracts = np.array([[0.0,0.0,0.0,0.0],[1.0,3.0,9.0,2.0]])
tesseract_velocities = np.array([
    [-1.0, 1.0, 0.0, 4.0],
    [0.0, -1.0, 0.0, 0.0]
])
mass_of_tesseracts = [5,8] #this array represents the mass of different tesseracts
charge_of_tesseracts = [-1,1] #this array represents the charge of different tesseracts

n = len(position_tesseracts)

#calculation of force and acceleration, wrapped as a function
def compute_force_and_acceleration(positions, masses, n):
    force_tesseracts = []
    tesseracts_r = []

    for i in range(n):
        force_accumulated = 0 # gravitational force exerted on one one body by all the other bodies
        for j in range(n):
            if j == i : 
                continue
            # calculating r(straight line distance between two objects)
            seperation = positions[j] - positions[i]
            r = np.sqrt(np.sum(seperation**2))
            tesseracts_r.append(r)
            # calculating gravitational force exerted by second object on first object
            force = (G*masses[j]*masses[i])/r**4 * seperation
            force_accumulated += force
        force_tesseracts.append(force_accumulated) 

    #calculating acceleration 
    #F=ma
    acceleration_tesseracts = []
    for i in range(len(force_tesseracts)):
        acceleration = force_tesseracts[i]/masses[i]
        acceleration_tesseracts.append(acceleration)

    return force_tesseracts, acceleration_tesseracts, tesseracts_r

force_tesseracts, acceleration_tesseracts, tesseracts_r = compute_force_and_acceleration(position_tesseracts, mass_of_tesseracts, n)

#comparing euler's method and RK4
f = 0
while f<10:
    f+=1
    #findign changing acceleration
    _,acceleration_tesseracts,_ = compute_force_and_acceleration(position_tesseracts,mass_of_tesseracts,n)
    for i in range(n):
        #euler's method
        euler_new_velocity = tesseract_velocities[i] + acceleration_tesseracts[i] * DT
        tesseract_velocities[i] = euler_new_velocity
        euler_r = position_tesseracts[i] + tesseract_velocities[i] * DT
        position_tesseracts[i] = euler_r
        #RK4