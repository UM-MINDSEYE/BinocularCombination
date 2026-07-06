import numpy as np
import pandas as pd

def simulate_observer(filename, alpha_db, gamma=1.5, noise_std=1.5):
    # Parameters
    ratios = [0.5, 0.707, 1.0, 1.414, 2.0]
    reps = 8
    configs = [1, 2]
    theta = 45.0  # Total phase difference between eyes

    # Convert alpha_db to ratio alpha
    alpha = 10**(alpha_db / 20.0)

    data = []
    trial_count = 1

    for r in ratios:
        for c in configs:
            for _ in range(reps):
                # --- THE CRITICAL FIX ---
                # We change (1 - ratio) to (ratio - 1)
                # This ensures an increasing slope as the ratio increases.
                num = (r / alpha)**gamma - 1
                den = (r / alpha)**gamma + 1

                val = (num / den) * np.tan(np.radians(theta / 2))
                phi_base = 2 * np.degrees(np.arctan(val))

                # Configuration 2 flips the eyes, so we flip the sign here
                # to maintain the "bias-correction" logic in the analysis script.
                if c == 2:
                    phi_base = -phi_base

                # Add human noise (variability in alignment)
                perceived_phase = phi_base + np.random.normal(0, noise_std)

                data.append([trial_count, r, c, round(perceived_phase, 2)])
                trial_count += 1

    df = pd.DataFrame(data, columns=['trial', 'ratio', 'config', 'perceived_phase'])
    # Shuffle to simulate the random order of a real experiment
    df = df.sample(frac=1).reset_index(drop=True)
    df.to_csv(filename, index=False)
    print(f"File saved: {filename}")
    return filename

# Generate the files again with the new logic
simulate_observer("simulated_left_dominant.csv", alpha_db=-4.5)
simulate_observer("simulated_right_dominant.csv", alpha_db=3.8)