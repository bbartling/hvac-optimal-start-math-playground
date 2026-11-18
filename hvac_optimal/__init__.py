"""Portable optimal start/stop driver. Core imports need only Python's stdlib."""

from .reference import Config, Inputs, OptimizedStartStop, State, TickResult, TimeAdapter

__version__ = "0.1.0"
__all__ = ["Config", "Inputs", "OptimizedStartStop", "State", "TickResult", "TimeAdapter"]
