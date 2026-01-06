from scripts.helpers import model4_topt_minutes

def main() -> None:
    print("--- Day F3 Demo: deadband vs runtime ---")
    e0 = 6.0
    c = 0.90
    for a in (1.0, 0.5, 0.25):
        t = model4_topt_minutes(deadband_deg=a, e0=e0, c=c)
        print(f"deadband={a:.2f}°F -> t_opt={t:.1f} minutes")

if __name__ == "__main__":
    main()
