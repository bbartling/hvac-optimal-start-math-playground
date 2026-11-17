"""hvac_optimal: data-driven optimal START and optimal STOP for HVAC.

Pure Python (standard library only). Units are whatever you feed in, as long
as they are consistent; the PNNL reference constants (Model 2 reference OAT,
Model 3 /10 scaling) assume degrees Fahrenheit, which is the default.

Quick start::

    from hvac_optimal import OptimalStartPlanner, OptimalStopPlanner, ZoneReading

    start = OptimalStartPlanner.recommended()      # benchmark winner
    lead = start.lead_minutes([ZoneReading("z1", 62.0, 70.0, 75.0)], oat=20.0)
    if start.should_start(minutes_to_occupancy=45, zones=..., oat=20.0): ...

    # after each morning, feed back what actually happened:
    start.learn("z1", RecoveryEvent(...))

See README.md for the benchmark that chose the defaults.
"""
from .types import RecoveryEvent, ZoneReading, CoastSample, Mode
from .start_models import (
    StartModel, FixedLead, LinearRateEMA, PNNLModel1Quadratic, PNNLModel2OatRatio,
    PNNLModel3Regression, PNNLModel4Exponential, PNNLMedianEnsemble, RepoSGDModel5,
    RobustRLSStart, START_MODELS, make_start_model,
)
from .start_planner import OptimalStartPlanner
from .stop_models import (
    StopModel, NoEarlyStop, ConstantDrift, RecoveryRateProxy, LinearDriftEMA,
    FirstOrderCoast, STOP_MODELS, make_stop_model,
)
from .stop_planner import OptimalStopPlanner

__all__ = [
    "RecoveryEvent", "ZoneReading", "CoastSample", "Mode",
    "StartModel", "FixedLead", "LinearRateEMA", "PNNLModel1Quadratic", "PNNLModel2OatRatio",
    "PNNLModel3Regression", "PNNLModel4Exponential", "PNNLMedianEnsemble", "RepoSGDModel5",
    "RobustRLSStart", "START_MODELS", "make_start_model", "OptimalStartPlanner",
    "StopModel", "NoEarlyStop", "ConstantDrift", "RecoveryRateProxy", "LinearDriftEMA",
    "FirstOrderCoast", "STOP_MODELS", "make_stop_model", "OptimalStopPlanner",
]
__version__ = "1.0.0"
