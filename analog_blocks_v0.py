
# ============================================================
# Analog Computer Block Library
# ============================================================
# Author: Bill
# Description:
#     A collection of reusable analog‑computer simulation blocks
#     implemented as Python classes. These blocks replicate the
#     behavior of classic op‑amp analog computers using modern
#     numerical methods suitable for JupyterLab.
#
# Table of Contents
# ------------------------------------------------------------
#   1. Node (virtual summing junction)
#   2. Capacitor (storage/integrator)
#   3. Resistor (conductance block)
#   4. Diffusion (nonlinear flow block)
#   5. DelayLine (programmable delay line)
#   6. NegGainOpAmp (inverting amplifier stage)
#
# Usage:
#     import analog_blocks as ab
#     A = ab.Node("A", initial_V=0)
#     amp = ab.NegGainOpAmp("Stage1", Rin=10000, Rf=20000)
#
# Notes:
#     - All blocks are designed to be modular and chainable.
#     - Flows are implemented as functions to ensure live updates.
#     - This file is intended as a reusable library across notebooks.
# ============================================================


# ------------------------------------------------------------
# 1. Node
# ------------------------------------------------------------
class Node:
    """
    Virtual summing junction (analogous to an op‑amp summing node).

    Parameters
    ----------
    name : str
        Label for the node.
    initial_V : float, optional
        Initial particle density (voltage).

    Notes
    -----
    - A node stores a voltage representing particle density.
    - Flows are attached as functions so they recompute dynamically.
    - net_flow() enforces conservation of flow (Kirchhoff's law).
    """

    def __init__(self, name, initial_V=0.0):
        self.name = name
        self.V = initial_V
        self.flows = []

    def add_flow(self, flow_function):
        """Attach a flow function to the node."""
        self.flows.append(flow_function)

    def net_flow(self):
        """Compute the sum of all flows entering/leaving the node."""
        return sum(f() for f in self.flows)



# ------------------------------------------------------------
# 2. Capacitor
# ------------------------------------------------------------
class Capacitor:
    """
    Storage block representing a capacitor (integrator).

    Parameters
    ----------
    node : Node
        The node whose voltage is updated.
    C : float
        Capacitance.
    dt : float
        Time step.

    Notes
    -----
    - Updates node voltage using dV = (I / C) * dt.
    - This is the numerical analog of continuous‑time integration.
    """

    def __init__(self, node, C, dt):
        self.node = node
        self.C = C
        self.dt = dt

    def update(self):
        """Update the node voltage based on net flow."""
        I = self.node.net_flow()
        self.node.V += (I / self.C) * self.dt



# ------------------------------------------------------------
# 3. Resistor
# ------------------------------------------------------------
class Resistor:
    """
    Linear conductance block.

    Parameters
    ----------
    G : float
        Conductance (1/R).
    V_source : callable
        Function returning the current voltage.

    Notes
    -----
    - Implements I = G * V.
    - V_source must be a function to ensure live updates.
    """

    def __init__(self, G, V_source):
        self.G = G
        self.V_source = V_source

    def flow(self):
        """Compute flow based on current voltage."""
        return self.G * self.V_source()



# ------------------------------------------------------------
# 4. Diffusion
# ------------------------------------------------------------
class Diffusion:
    """
    Nonlinear diffusion block.

    Parameters
    ----------
    k : float
        Diffusion coefficient.
    V1 : callable
        Function returning voltage of compartment 1.
    V2 : callable
        Function returning voltage of compartment 2.

    Notes
    -----
    - Implements nonlinear diffusion:
          I = k * (V1 - V2)^2 * sign(V1 - V2)
    - Suitable for biochemical pathway modeling.
    """

    def __init__(self, k, V1, V2):
        self.k = k
        self.V1 = V1
        self.V2 = V2

    def flow_1_to_2(self):
        """Compute nonlinear diffusion flow from V1 to V2."""
        d = self.V1() - self.V2()
        return self.k * d * abs(d)



# ------------------------------------------------------------
# 5. DelayLine
# ------------------------------------------------------------
import numpy as np

class DelayLine:
    """
    Programmable delay line with tap weights.

    Parameters
    ----------
    name : str
        Label for the block.
    tap_weights : dict
        Dictionary {tap_index: weight}.

    Notes
    -----
    - Performs convolution of input signal with tap weights.
    - Ideal for demonstrating high‑speed convolution behavior.
    """

    def __init__(self, name, tap_weights):
        self.name = name
        self.tap_weights = tap_weights

    def convolve(self, input_dict):
        """Perform convolution and return input/output dictionaries."""
        max_in = max(input_dict.keys())
        max_tap = max(self.tap_weights.keys())

        input_signal = np.array([input_dict.get(i, 0.0)
                                 for i in range(max_in + 1)])
        tap_array = np.array([self.tap_weights.get(i, 0.0)
                              for i in range(max_tap + 1)])

        output_array = np.convolve(input_signal, tap_array, mode='full')

        output_dict = {i: output_array[i] for i in range(len(output_array))}

        return {
            "input": input_dict,
            "tap_weights": self.tap_weights,
            "output": output_dict
        }



# ------------------------------------------------------------
# 6. NegGainOpAmp
# ------------------------------------------------------------
class NegGainOpAmp:
    """
    Inverting op‑amp stage (virtual‑ground behavior).

    Parameters
    ----------
    name : str
        Label for the block.
    Rin : float
        Input resistor.
    Rf : float
        Feedback resistor.
    gain : float, optional
        Open‑loop gain (default = -10000).

    Notes
    -----
    - Implements classic inverting amplifier:
          Vout = -(Rf / Rin) * Vin
    - Suitable for multi‑stage amplifier cascades.
    """

    def __init__(self, name, Rin, Rf, gain=-10000):
        self.name = name
        self.Rin = Rin
        self.Rf = Rf
        self.gain = gain

    def compute(self, Vin):
        """Compute output voltage using closed‑loop gain."""
        closed_loop_gain = -(self.Rf / self.Rin)
        Vout = closed_loop_gain * Vin
        return {
            "stage": self.name,
            "input": Vin,
            "output": Vout,
            "closed_loop_gain": closed_loop_gain
        }


# -------------------------------------------------------------------------------------------------------
class DoseBlock(BlockBase):
    """
    A composite analog block that stores a dose (charge), leaks it through a resistor,
    and upon triggering becomes a current source delivering a fixed quantity of charge.

    States:
        idle      – capacitor holds initial charge
        draining  – resistor drains charge into node
        triggered – injects fixed dose into node
    """

    def __init__(self, name, node, C, R, dose_quantity, dt=0.1):
        super().__init__(name)

        # Parameters
        self.node = node
        self.C = C
        self.R = R
        self.dose_quantity = dose_quantity
        self.dt = dt

        # Internal state
        self.V = dose_quantity / C        # initial capacitor voltage
        self.state = "idle"
        self.remaining_dose = dose_quantity

    def update(self):
        """Advance the block one simulation step based on its state."""

        if self.state == "idle":
            # Capacitor simply holds its charge
            return

        elif self.state == "draining":
            # Resistor drains charge into node
            I = self.V / self.R
            dV = -(I / self.C) * self.dt
            self.V += dV
            self.node.V += I * self.dt

            # Stop draining when empty
            if self.V <= 0:
                self.V = 0
                self.state = "idle"

        elif self.state == "triggered":
            # Inject fixed dose as a current source
            I = self.remaining_dose / self.dt
            self.node.V += I * self.dt
            self.remaining_dose = 0
            self.state = "idle"

    def trigger(self):
        """Switch the block into triggered mode."""
        self.state = "triggered"

    def start_draining(self):
        """Begin resistor‑drain mode."""
        self.state = "draining"

    def summarize(self):
        """Pretty-print block metadata."""
        return summarize_block(self)
# --------------------------------------------------
















# ------------------------------------------------------------
# Utility Functions
# ------------------------------------------------------------

def inspect_block(obj):
    """
    Return a dictionary describing the object's class, attributes, and methods.

    Parameters
    ----------
    obj : object
        Any analog-computer block instance.

    Returns
    -------
    dict
        {
            "class": <class name>,
            "attributes": { ... },
            "methods": [ ... ]
        }
    """
    attrs = {k: v for k, v in obj.__dict__.items()}

    methods = [
        m for m in dir(obj)
        if callable(getattr(obj, m))
        and not m.startswith("__")
        and m not in attrs
    ]

    return {
        "class": obj.__class__.__name__,
        "attributes": attrs,
        "methods": methods
    }


def summarize_block(obj):
    """
    Pretty-print a readable summary of any analog-computer block.

    Parameters
    ----------
    obj : object
        Any block instance from the analog_blocks library.

    Returns
    -------
    str
        A formatted multi-line string describing the block.
    """
    info = inspect_block(obj)

    lines = []
    lines.append(f"Block Summary: {info['class']}")
    lines.append("-" * 50)

    # Attributes
    lines.append("Attributes:")
    for k, v in info["attributes"].items():
        lines.append(f"  • {k}: {v}")

    # Methods
    lines.append("\nMethods:")
    for m in info["methods"]:
        lines.append(f"  • {m}")

    return "\n".join(lines)
