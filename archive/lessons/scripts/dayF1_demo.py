from scripts.helpers import simulate_first_order_errors

def main() -> None:
    print("--- Day F1 Demo: first-order error decay ---")
    for c in (0.95, 0.90, 0.85):
        print(f"\nUsing c={c}")
        errors = simulate_first_order_errors(e0=6.0, c=c, steps=12)
        for i, e in enumerate(errors):
            print(f"  minute {i:02d}: error={e:.3f}°F")

if __name__ == "__main__":
    main()
