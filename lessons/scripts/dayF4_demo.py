from scripts.helpers import simulate_first_order_errors, estimate_c_least_squares

def main() -> None:
    print("--- Day F4 Demo: estimate c from a batch ---")
    true_c = 0.90
    errors = simulate_first_order_errors(e0=6.0, c=true_c, steps=12, noise=0.05, seed=42)
    c_hat = estimate_c_least_squares(errors)
    print("true_c:", true_c)
    print("c_hat :", round(c_hat, 4))
    print("errors (first 6):", [round(e, 3) for e in errors[:6]])

if __name__ == "__main__":
    main()
