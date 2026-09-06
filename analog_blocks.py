# 1. Base Block Classes

class BlockBase:
    def __init__(self, name):
        self.name = name
        self.state = {}
        self.connections = {}
        self.parameters = {}

    def update(self):
        pass

    def summarize(self):
        return {
            "name": self.name,
            "state": self.state.copy(),
            "parameters": self.parameters.copy()
        }

# 2. PoolBlock (particles + density)
class PoolBlock(BlockBase):
    def __init__(self, name, particles, capacity):
        super().__init__(name)
        self.particles = particles
        self.capacity = capacity

    @property
    def density(self):
        return self.particles / self.capacity

# 3. RespirationBase
class RespirationBase(BlockBase):
    def __init__(self, name, fuel_pool, o2_pool, adp_pool, atp_pool, amp_pool, co2_pool):
        super().__init__(name)

        self.fuel_pool = fuel_pool
        self.o2_pool = o2_pool
        self.adp_pool = adp_pool
        self.atp_pool = atp_pool
        self.amp_pool = amp_pool
        self.co2_pool = co2_pool

        self.connections.update({
            "fuel": fuel_pool,
            "o2": o2_pool,
            "adp": adp_pool,
            "atp": atp_pool,
            "amp": amp_pool,
            "co2": co2_pool
        })

#4. RespirationBlock (ATP/O₂/ADP/CO₂ + AMP production)
class RespirationBlock(RespirationBase):
    def __init__(self, name, fuel_pool, o2_pool, adp_pool, atp_pool, amp_pool, co2_pool):
        super().__init__(name, fuel_pool, o2_pool, adp_pool, atp_pool, amp_pool, co2_pool)

        self.parameters.update({
            "ATP_per_O2": 10,        # stronger O2 consumption
            "CO2_per_O2": 1,
            "fuel_per_ATP": 1/20,    # stronger fuel use
            "AMP_ratio": 0.5,        # stronger AMP production
        })


    def update(self):
        max_ATP_from_O2 = self.o2_pool.particles * self.parameters["ATP_per_O2"]
        max_ATP_from_ADP = self.adp_pool.particles

        ATP_produced = min(max_ATP_from_O2, max_ATP_from_ADP)

        O2_used = ATP_produced / self.parameters["ATP_per_O2"]
        ADP_used = ATP_produced
        CO2_produced = O2_used
        fuel_used = ATP_produced * self.parameters["fuel_per_ATP"]
        AMP_produced = ADP_used * self.parameters["AMP_ratio"]

        self.o2_pool.particles -= O2_used
        self.adp_pool.particles -= ADP_used
        self.atp_pool.particles += ATP_produced
        self.co2_pool.particles += CO2_produced
        self.fuel_pool.particles -= fuel_used
        self.amp_pool.particles += AMP_produced

        self.state.update({
            "ATP_produced": ATP_produced,
            "O2_used": O2_used,
            "ADP_used": ADP_used,
            "CO2_produced": CO2_produced,
            "fuel_used": fuel_used,
            "AMP_produced": AMP_produced
        })

# 5. RespirationWithAutonomics
class RespirationWithAutonomics(RespirationBase):
    def __init__(self, name, fuel_pool, o2_pool, adp_pool, atp_pool, amp_pool, co2_pool,
                 autonomic_pool, base_rate=1.0):
        super().__init__(name, fuel_pool, o2_pool, adp_pool, atp_pool, amp_pool, co2_pool)

        self.autonomic_pool = autonomic_pool
        self.parameters.update({
            "ATP_per_O2": 32,
            "CO2_per_O2": 1,
            "fuel_per_ATP": 1/32,
            "AMP_ratio": 0.1,
            "base_rate": base_rate
        })

    def update(self):
        modulation = self.autonomic_pool.density
        respiration_rate = self.parameters["base_rate"] * modulation

        max_ATP_from_O2 = self.o2_pool.particles * self.parameters["ATP_per_O2"]
        max_ATP_from_ADP = self.adp_pool.particles

        ATP_produced_raw = min(max_ATP_from_O2, max_ATP_from_ADP)
        ATP_produced = ATP_produced_raw * respiration_rate

        O2_used = ATP_produced / self.parameters["ATP_per_O2"]
        ADP_used = ATP_produced
        CO2_produced = O2_used
        fuel_used = ATP_produced * self.parameters["fuel_per_ATP"]
        AMP_produced = ADP_used * self.parameters["AMP_ratio"]

        self.o2_pool.particles -= O2_used
        self.adp_pool.particles -= ADP_used
        self.atp_pool.particles += ATP_produced
        self.co2_pool.particles += CO2_produced
        self.fuel_pool.particles -= fuel_used
        self.amp_pool.particles += AMP_produced

        self.state.update({
            "ATP_produced": ATP_produced,
            "O2_used": O2_used,
            "ADP_used": ADP_used,
            "CO2_produced": CO2_produced,
            "fuel_used": fuel_used,
            "AMP_produced": AMP_produced,
            "modulation": modulation,
            "respiration_rate": respiration_rate
        })
# 6. Stability Iteration Engine
def iterate_to_stability(blocks, max_steps=200, epsilon=1e-6):
    prev_states = None

    for step in range(max_steps):
        for b in blocks:
            b.update()

        current_states = {b.name: b.summarize()["state"].copy() for b in blocks}

        if prev_states is not None:
            diffs = []
            for name in current_states:
                for key in current_states[name]:
                    old = prev_states[name].get(key, 0)
                    new = current_states[name][key]
                    diffs.append(abs(new - old))
            if max(diffs) < epsilon:
                return current_states

        prev_states = current_states

    return current_states


