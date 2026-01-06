from scripts.helpers import estimate_c_least_squares, model4_topt_minutes

def main() -> None:
    print("--- Day F5 Demo: window -> c -> t_opt ---")
    deadband = 0.5
    errors = [6.0, 5.3, 4.7, 4.2, 3.8, 3.4]  # pretend sampled after startup
    c = estimate_c_least_squares(errors)
    t = model4_topt_minutes(deadband_deg=deadband, e0=errors[0], c=c)
    print("errors:", errors)
    print("c_hat :", round(c, 4))
    print("t_opt :", round(t, 2), "minutes")

if __name__ == "__main__":
    main()
