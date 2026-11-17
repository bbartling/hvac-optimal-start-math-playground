# hvac-optimal-start-math-playground → `hvac_optimal`

Data-driven **optimal start** and **optimal stop** for HVAC, in pure Python with no
dependencies. Every algorithm was benchmarked closed loop on the NeurIPS 2026
smart-buildings simulator, across many buildings, AHUs, zones, climates and seasons.

> **Work in progress:** the benchmark is still running. The results tables and the final
> recommended defaults will land in this README before the PR leaves draft.

## Layout

| path | what |
|---|---|
| `src/hvac_optimal/` | the package: start models, stop models, multi-zone planners |
| `tests/` | pytest suite (PNNL equations, PNNL EMA vs aems-edge, planners, stop bounds) |
| `benchmarks/neurips_sim/` | closed-loop simulator harness and analysis ([README](benchmarks/neurips_sim/README.md)) |
| `examples/quickstart.py` | a minimal start + stop loop |
| `docs/LEARN_THE_MATH.md` | the original learning guide (formerly this README) |
| `lessons/`, `README_LESSON_DETAILS.md` | the 50-day lessons |
| `archive/` | the original tutorial scripts, unchanged ([README](archive/README.md)) |
| `PNNL_Paper/` | the reference paper |

## Quick start

```bash
pip install -e .[dev]
pytest
python examples/quickstart.py
python -m hvac_optimal          # lists algorithms and recommended defaults
```

```python
from hvac_optimal import OptimalStartPlanner, OptimalStopPlanner, ZoneReading

start = OptimalStartPlanner.recommended()
zones = [ZoneReading("vav-1", temp=64.0, heat_sp=70.0, cool_sp=75.0)]
if start.should_start(minutes_to_occupancy=45, zones=zones, oat=20.0):
    ...  # command the AHU / RTU on (warm-up)
```

## License

MIT, see [LICENSE](LICENSE).
