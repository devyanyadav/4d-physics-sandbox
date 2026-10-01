import numpy as np
import matplotlib.pyplot as plt

G = 1        # gravitational constant (toy units)
DT = 0.01    # fixed physics timestep, independent of render dt
STEPS = 5000

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
    """Returns (relative energy drift per step, closest separation seen)."""
    positions = INITIAL_POSITIONS.copy()
    velocities = INITIAL_VELOCITIES.copy()
    energy_drift = []
    initial_energy = total_energy(positions, velocities, MASSES)
    min_seperation = float("inf")  # minimum distance between two objects; initially infinity

    for i in range(steps):
        positions, velocities = step_fn(positions, velocities, MASSES, dt)
        new_energy = total_energy(positions, velocities, MASSES)
        energy_drift.append((new_energy - initial_energy) / abs(initial_energy))
        seperation = positions[1] - positions[0]
        r = np.sqrt(np.dot(seperation, seperation))
        min_seperation = min(min_seperation, r)

    return energy_drift, min_seperation


def plot_drift(euler_drift, rk4_drift, dt):
    t = np.arange(1, len(euler_drift) + 1) * dt
    # running max: "worst error so far". Never decreases, so no log-axis dips.
    euler_max = np.maximum.accumulate(np.abs(euler_drift))
    rk4_max = np.maximum.accumulate(np.abs(rk4_drift))

    plt.figure(figsize=(8, 5))
    plt.semilogy(t, euler_max, label="Euler (semi-implicit)")
    plt.semilogy(t, rk4_max, label="RK4")
    plt.axhline(1e-16, color="gray", linestyle="--", label="rounding-noise scale")
    plt.xlabel("time")
    plt.ylabel("running max |relative energy drift|")
    plt.title("Energy drift: Euler vs RK4 (scattering encounter, DT = " + str(dt) + ")")
    plt.legend()
    plt.grid(True, which="both", alpha=0.3)
    plt.tight_layout()
    plt.savefig("drift.png", dpi=150)
    plt.show()

def sweep(step_fn,dts,T):
    drifts = []
    seperations = []
    for dt in dts: 
        steps = int(np.round(T/dt))
        energy_drift,min_seperation = run(step_fn,dt,steps)
        max_drift = np.max(np.abs(energy_drift))
        drifts.append(max_drift)
        seperations.append(min_seperation)
    return drifts,seperations

def orders(dts, errors):
    ps = []
    for k in range(len(dts) - 1):
        p = np.log(errors[k] / errors[k + 1]) / np.log(dts[k] / dts[k + 1])
        ps.append(p)
    return ps


if __name__ == "__main__":
    euler_dts = [0.01, 0.005, 0.0025]
    rk4_dts = [0.4, 0.2, 0.1, 0.05]
    euler_drifts,euler_seperations =sweep(euler_step,euler_dts,50)
    rk4_drifts,rk4_seperations=sweep(rk4_step,rk4_dts,50)
    for i in range(len(euler_dts)):
        print(f"{euler_dts[i]} | {euler_drifts[i]} | {euler_seperations[i]}",)
    for i in range(len(rk4_dts)):
        print(f"{rk4_dts[i]} | {rk4_drifts[i]} | {rk4_seperations[i]}")
    print("Euler p:", orders(euler_dts, euler_drifts))
    print("RK4 p:  ", orders(rk4_dts, rk4_drifts))
    