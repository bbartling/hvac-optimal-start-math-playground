import math

def minutes_to_deadband(a: float, e0: float, c: float) -> float:
    return math.log(a / abs(e0)) / math.log(c)

def main() -> None:
    print("--- Day F2 Demo: logs -> time to deadband ---")
    a = 0.5
    e0 = 6.0
    for c in (0.95, 0.90, 0.85):
        n = minutes_to_deadband(a, e0, c)
        print(f"c={c}: minutes_to_deadband={n:.2f}")

if __name__ == "__main__":
    main()
