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

    return np.array(force_tesseracts), np.array(acceleration_tesseracts), tesseracts_r

force_tesseracts, acceleration_tesseracts, tesseracts_r = compute_force_and_acceleration(position_tesseracts, mass_of_tesseracts, n)

#comparing euler's method and RK4
euler_velocities = []
euler_positions = []

rk4_velocities = []
rk4_positions = []

f = 0
while f < 10:
    f += 1

    # acceleration comes from wherever the euler trajectory currently is,
    positions_for_accel = euler_positions if len(euler_positions) != 0 else position_tesseracts
    _, acceleration_tesseracts, _ = compute_force_and_acceleration(positions_for_accel, mass_of_tesseracts, n)

    new_velocities = []
    new_positions = []
    for i in range(n):
        old_velocity = tesseract_velocities[i] if len(euler_velocities) == 0 else euler_velocities[i]
        old_position = position_tesseracts[i] if len(euler_positions) == 0 else euler_positions[i]

        # semi-implicit euler: velocity first, then position uses the *new* velocity
        v_new = old_velocity + acceleration_tesseracts[i] * DT
        r_new = old_position + v_new * DT

        new_velocities.append(v_new)
        new_positions.append(r_new)

    euler_velocities = new_velocities
    euler_positions = new_positions

    #RK4
    positions_for_accel = rk4_positions if len(rk4_positions) != 0 else position_tesseracts
    velocity_for_r = rk4_velocities if len(rk4_velocities) != 0 else tesseract_velocities

    # four stages, each computing its r-slope and v-slope together,
    # so each stage only ever depends on the previous stage's results

    # stage 1
    k1_r = velocity_for_r
    _, k1_v, _ = compute_force_and_acceleration(positions_for_accel, mass_of_tesseracts, n)

    # stage 2 (half-step, using stage 1's results)
    k2_r = velocity_for_r + (DT/2)*k1_v
    _, k2_v, _ = compute_force_and_acceleration(positions_for_accel + (DT/2)*k1_r, mass_of_tesseracts, n)

    # stage 3 (half-step, using stage 2's results)
    k3_r = velocity_for_r + (DT/2)*k2_v
    _, k3_v, _ = compute_force_and_acceleration(positions_for_accel + (DT/2)*k2_r, mass_of_tesseracts, n)

    # stage 4 (full step, using stage 3's results)
    k4_r = velocity_for_r + DT*k3_v
    _, k4_v, _ = compute_force_and_acceleration(positions_for_accel + DT*k3_r, mass_of_tesseracts, n)

    new_velocities = []
    new_positions = []
    for i in range(n):
        v_new = velocity_for_r[i] + (DT/6)*(k1_v[i] + 2*k2_v[i] + 2*k3_v[i] + k4_v[i])
        r_new = positions_for_accel[i] + (DT/6)*(k1_r[i] + 2*k2_r[i] + 2*k3_r[i] + k4_r[i])

        new_velocities.append(v_new)
        new_positions.append(r_new)

    rk4_velocities = np.array(new_velocities)
    rk4_positions = np.array(new_positions)