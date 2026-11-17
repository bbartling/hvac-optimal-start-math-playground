from scripts.helpers import ema, clamp

def main() -> None:
    print("--- Day F6 Demo: EMA smoothing of c ---")
    c_ema = 0.92
    w = 0.30
    daily = [0.90, 0.94, 1.02, 0.91, 0.88]  # includes an out-of-range value
    for d in daily:
        c_new = clamp(d, 0.80, 0.99)
        c_ema = ema(c_ema, c_new, w)
        print(f"raw={d:.2f} -> clamped={c_new:.2f} -> c_ema={c_ema:.4f}")

if __name__ == "__main__":
    main()
