import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

data = pd.read_csv("./simulation/simulated_right_dominant.csv")

mean_phases = []
unique_ratios = sorted(data['ratio'].unique())

for r in unique_ratios:
    p1 = data[(data['ratio'] == r) & (data['config'] == 1)]['perceived_phase'].mean()
    p2 = data[(data['ratio'] == r) & (data['config'] == 2)]['perceived_phase'].mean()
    mean_phases.append((p1 - p2) / 2)

x_data = np.array(unique_ratios)
y_data = np.array(mean_phases)

def model_func(delta, alpha, gamma):
    theta = 45.0
    theta_rad = np.radians(theta)
    numerator = (delta/alpha)**gamma - 1
    denominator = (delta/alpha)**gamma + 1
    phi = 2 * np.degrees(np.arctan((numerator / denominator) * np.tan(theta_rad / 2)))
    return phi


popt, pcov = curve_fit(model_func, x_data, y_data, p0=[1.0, 1.5])
alpha_fit, gamma_fit = popt
alpha_db = 20 * np.log10(alpha_fit)
print(f"Alpha (dB): {alpha_db:.2f} dB | Gamma: {gamma_fit:.3f}")

x_smooth_ratio = np.logspace(-1, 1, 500)
y_smooth = model_func(x_smooth_ratio, alpha_fit, gamma_fit)

x_data_db = 20 * np.log10(x_data)
x_smooth_db = 20 * np.log10(x_smooth_ratio)

plt.figure(figsize=(10, 7))
plt.plot(x_smooth_db, y_smooth, color='#6b8e23', linewidth=3, label='Model Fit')
plt.scatter(x_data_db, y_data, color='red', edgecolor='black', s=60, zorder=5, label='Mean Data')

plt.axhline(0, color='lightgray', linewidth=2)
plt.axvline(0, color='lightgray', linewidth=2)
plt.axvline(alpha_db, color='#db7093', linestyle='--', label=f'Balance Point: {alpha_db:.2f}dB')

plt.xlim(-12, 12)
plt.ylim(-25, 25)
plt.xlabel("Contrast ratio (dB)")
plt.ylabel("Perceived phase (deg)")
plt.title("Binocular Phase Combination (Fixed Slope)")
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()