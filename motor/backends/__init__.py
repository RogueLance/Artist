"""Backend adapters for different drawing applications."""

from motor.backends.base import BackendInterface
from motor.backends.krita_backend import KritaBackend
from motor.backends.simulation_backend import SimulationBackend

__all__ = [
    "BackendInterface",
    "KritaBackend",
    "SimulationBackend",
]
