import numpy as np

G = 1        # gravitational constant (toy units)
DT = 0.01    # fixed physics timestep, independent of render dt
STEPS = 10   # start at 10 to check against entry 13, then raise to thousands

INITIAL_POSITIONS = np.array([[0.0, 0.0, 0.0, 0.0],
                              [1.0, 3.0, 9.0, 2.0]])
INITIAL_VELOCITIES = np.array([[-1.0, 1.0, 0.0, 4.0],
                               [0.0, -1.0, 0.0, 0.0]])
MASSES = np.array([5.0, 8.0])


def compute_acceleration(positions, masses):
    n = len(masses)
    accelerations = []
    for i in range(n):
        force_accumulated = np.zeros_like(positions[i])  # reset once per i
        for j in range(n):
            if j == i:
                continue
            separation = positions[j] - positions[i]
            r = np.sqrt(np.sum(separation**2))
            force_accumulated += (G * masses[i] * masses[j]) / r**4 * separation
        accelerations.append(force_accumulated / masses[i])
    return np.array(accelerations)


def total_energy(positions, velocities, masses):
    kinetic_energy = 0
    potential_energy = 0
    for i in range(len(masses)):
        kinetic_energy += 0.5 * masses[i] * np.dot(velocities[i], velocities[i])
        for j in range(i + 1, len(masses)):  # j > i: each pair counted once
            separation = positions[j] - positions[i]
            separation_squared = np.dot(separation, separation)
            potential_energy += (-G * masses[i] * masses[j]) / (2 * separation_squared)
    return kinetic_energy + potential_energy


def euler_step(positions, velocities, masses, dt):
    """Semi-implicit Euler: velocity first, then position uses the new velocity."""
    acceleration = compute_acceleration(positions, masses)
    new_velocities = velocities + acceleration * dt
    new_positions = positions + new_velocities * dt
    return new_positions, new_velocities


def rk4_step(positions, velocities, masses, dt):
    # each stage computes its r-slope and v-slope together
    k1_r = velocities
    k1_v = compute_acceleration(positions, masses)

    k2_r = velocities + (dt / 2) * k1_v
    k2_v = compute_acceleration(positions + (dt / 2) * k1_r, masses)

    k3_r = velocities + (dt / 2) * k2_v
    k3_v = compute_acceleration(positions + (dt / 2) * k2_r, masses)

    k4_r = velocities + dt * k3_v
    k4_v = compute_acceleration(positions + dt * k3_r, masses)

    new_velocities = velocities + (dt / 6) * (k1_v + 2 * k2_v + 2 * k3_v + k4_v)
    new_positions = positions + (dt / 6) * (k1_r + 2 * k2_r + 2 * k3_r + k4_r)
    return new_positions, new_velocities



def run(step_fn, dt, steps):
    positions = INITIAL_POSITIONS.copy()
    velocities = INITIAL_VELOCITIES.copy()
    energy_drift = []
    initial_energy = total_energy(positions,velocities,MASSES)
    
    for i in range(steps):
        positions,velocities = step_fn(positions,velocities,MASSES,dt)
        new_energy = total_energy(positions,velocities,MASSES)
        energy_drift.append((new_energy-initial_energy)/abs(initial_energy))

    return energy_drift

    


if __name__ == "__main__":
    euler_drift = run(euler_step, DT, STEPS)
    rk4_drift = run(rk4_step, DT, STEPS)
    print("Euler final drift:", euler_drift[-1],)
    print("RK4   final drift:", rk4_drift[-1],)