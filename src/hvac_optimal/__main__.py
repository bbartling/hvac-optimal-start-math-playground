"""`python -m hvac_optimal` lists the algorithms and the recommended defaults."""
from . import START_MODELS, STOP_MODELS, __version__
from .start_planner import RECOMMENDED_START_MODEL
from .stop_planner import RECOMMENDED_STOP_MODEL


def main() -> None:
    print(f"hvac_optimal {__version__}")
    print(f"recommended start: {RECOMMENDED_START_MODEL}")
    print(f"recommended stop : {RECOMMENDED_STOP_MODEL}")
    print("start models:", ", ".join(sorted(START_MODELS)))
    print("stop models :", ", ".join(sorted(STOP_MODELS)))


if __name__ == "__main__":
    main()
