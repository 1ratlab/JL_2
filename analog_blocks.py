"""
analog_blocks.py

Digital analog-computer blocks for particle-pool biochemical modeling.
Includes:
- BlockBase: common parent for all blocks
- PoolBlock: particle pool (ATP, O2, CO2, etc.)
- Node: generic voltage-like node (if needed for other analog constructs)
- Diffusion subsystem: base + constant/default/variable diffusion
- DoseBlock: composite block for fixed-dose injection
"""

# ---------------------------------------------------------------------
# Core base class
# ---------------------------------------------------------------------

class BlockBase:
    """Base class for all analog-computer blocks."""

    def __init__(self, name):
        self.name = name
        self.parameters = {}
        self.state = {}
        self.connections = {}

    def update(self):
        """Advance one simulation step. Must be overridden."""
        raise NotImplementedError

    def summarize(self):
        """Return metadata for introspection/logging."""
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "parameters": self.parameters,
            "state": self.state,
            "connections": {
                k: getattr(v, "name", str(v))
                for k, v in self.connections.items()
            },
        }


# ---------------------------------------------------------------------
# Node (generic voltage-like node, optional but useful)
# ---------------------------------------------------------------------

class Node(BlockBase):
    """Simple node with a scalar value (e.g., voltage, concentration)."""

    def __init__(self, name, initial_V=0.0):
        super().__init__(name)
        self.V = initial_V
        self.state["V"] = self.V

    def update(self):
        # Node itself may be passive; updated by connected blocks.
        self.state["V"] = self.V


# ---------------------------------------------------------------------
# PoolBlock: particle pool (ATP, O2, CO2, etc.)
# ---------------------------------------------------------------------

class PoolBlock(BlockBase):
    """
    Particle pool representing a biochemical compartment.

    particles: number of particles in the pool
    capacity: maximum "capacity" (used to compute density)
    density: particles / capacity
    """

    def __init__(self, name, particles, capacity):
        super().__init__(name)
        self.particles = float(particles)
        self.capacity = float(capacity)

        self.parameters["capacity"] = self.capacity
        self.state["particles"] = self.particles
        self.state["density"] = self.density

    @property
    def density(self):
        if self.capacity == 0:
            return 0.0
        return self.particles / self.capacity

    def update(self):
        # Just refresh density in state; particles are updated by other blocks.
        self.state["particles"] = self.particles
        self.state["density"] = self.density


# ---------------------------------------------------------------------
# Diffusion subsystem
# ---------------------------------------------------------------------

class DiffusionBase(BlockBase):
    """
    Base class for diffusion between two pools.

    Subclasses define how the diffusion coefficient D is obtained.
    """

    def __init__(self, name, pool_a: PoolBlock, pool_b: PoolBlock):
        super().__init__(name)
        self.pool_a = pool_a
        self.pool_b = pool_b

        self.connections["pool_a"] = pool_a
        self.connections["pool_b"] = pool_b

    def get_coefficient(self) -> float:
        """Return diffusion coefficient D. Must be overridden."""
        raise NotImplementedError

    def update(self):
        D = float(self.get_coefficient())
        delta = self.pool_a.density - self.pool_b.density
        flow = D * delta

        # Update particle counts (simple symmetric exchange)
        self.pool_a.particles -= flow
        self.pool_b.particles += flow

        # Record state
        self.state["D"] = D
        self.state["delta_density"] = delta
        self.state["flow"] = flow


class ConstantDiffusionBlock(DiffusionBase):
    """Diffusion with a fixed coefficient D."""

    def __init__(self, name, pool_a, pool_b, D):
        super().__init__(name, pool_a, pool_b)
        self.D = float(D)
        self.parameters["D"] = self.D

    def get_coefficient(self):
        return self.D


class DefaultDiffusionBlock(DiffusionBase):
    """Diffusion with default coefficient D = 1.0."""

    def __init__(self, name, pool_a, pool_b):
        super().__init__(name, pool_a, pool_b)
        self.parameters["D"] = 1.0

    def get_coefficient(self):
        return 1.0


class VariableDiffusionBlock(DiffusionBase):
    """
    Diffusion with coefficient driven by a pool.

    coefficient_pool.density is used as D.
    """

    def __init__(self, name, pool_a, pool_b, coefficient_pool: PoolBlock):
        super().__init__(name, pool_a, pool_b)
        self.coefficient_pool = coefficient_pool
        self.connections["coefficient_pool"] = coefficient_pool

    def get_coefficient(self):
        return self.coefficient_pool.density


# ---------------------------------------------------------------------
# DoseBlock: composite block for fixed-dose injection
# ---------------------------------------------------------------------

class DoseBlock(BlockBase):
    """
    Composite analog block:
    - stores a dose (charge/particles)
    - leaks through a resistor-like path
    - triggers a fixed injection into a node

    States:
        idle      – holds initial charge
        draining  – drains into node
        triggered – injects fixed dose into node
    """

    def __init__(self, name, node: Node, C, R, dose_quantity, dt=0.1):
        super().__init__(name)

        # Parameters
        self.node = node
        self.C = float(C)
        self.R = float(R)
        self.dose_quantity = float(dose_quantity)
        self.dt = float(dt)

        self.parameters.update({
            "C": self.C,
            "R": self.R,
            "dose_quantity": self.dose_quantity,
            "dt": self.dt,
        })

        # Internal state
        self.V = self.dose_quantity / self.C  # initial "voltage"
        self.state_mode = "idle"
        self.remaining_dose = self.dose_quantity

        self.state.update({
            "V": self.V,
            "mode": self.state_mode,
            "remaining_dose": self.remaining_dose,
        })

        self.connections["node"] = node

    def update(self):
        if self.state_mode == "idle":
            # No change
            pass

        elif self.state_mode == "draining":
            # Resistor-like drain into node
            I = self.V / self.R
            dV = -(I / self.C) * self.dt
            self.V += dV
            self.node.V += I * self.dt

            if self.V <= 0:
                self.V = 0.0
                self.state_mode = "idle"

        elif self.state_mode == "triggered":
            # Inject fixed dose as current over dt
            I = self.remaining_dose / self.dt
            self.node.V += I * self.dt
            self.remaining_dose = 0.0
            self.state_mode = "idle"

        # Update state dict
        self.state.update({
            "V": self.V,
            "mode": self.state_mode,
            "remaining_dose": self.remaining_dose,
        })

    def trigger(self):
        """Switch block into triggered mode."""
        self.state_mode = "triggered"

    def start_draining(self):
        """Begin draining mode."""
        self.state_mode = "draining"


# ---------------------------------------------------------------------
# Simple simulation helper (optional)
# ---------------------------------------------------------------------

def run_iteration(blocks, max_steps=1000, epsilon=1e-6):
    """
    Run blocks until approximate stability.

    blocks: list of BlockBase instances
    max_steps: maximum iterations
    epsilon: threshold for change in state (simple heuristic)
    """
    prev_states = [b.summarize()["state"].copy() for b in blocks]

    for step in range(max_steps):
        for b in blocks:
            b.update()

        stable = True
        for i, b in enumerate(blocks):
            current = b.summarize()["state"]
            prev = prev_states[i]
            # crude stability check: sum of absolute differences
            diff = 0.0
            for k in current:
                if isinstance(current[k], (int, float)) and k in prev:
                    diff += abs(current[k] - prev[k])
            if diff > epsilon:
                stable = False
            prev_states[i] = current.copy()

        if stable:
            break

    return {b.name: b.summarize()["state"] for b in blocks}

# ---------------------------------------------------------------------
# RespirationBase(BlockBase)
# ---------------------------------------------------------------------

class RespirationBase(BlockBase):    
    def __init__(self, name, fuel_pool, o2_pool, adp_pool, atp_pool, co2_pool):
        super().__init__(name)
        self.fuel_pool = fuel_pool
        self.o2_pool = o2_pool
        self.adp_pool = adp_pool
        self.atp_pool = atp_pool
        self.co2_pool = co2_pool

        self.connections.update({
            "fuel": fuel_pool,
            "o2": o2_pool,
            "adp": adp_pool,
            "atp": atp_pool,
            "co2": co2_pool,
        })

    def update(self):
        """ 
        Override in subclasses.
        """
        raise NotImplementedError

