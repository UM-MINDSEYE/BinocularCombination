# Binocular Combination — Task & Model Focus

This README concentrates on the psychophysical task implemented in `scripts/bc.py` and the parametric model fitted in `scripts/fit.py`. It explains what the observer does during the experiment, what data are produced, and — most importantly — the formula used to model the data and its interpretation.

---

## Short summary of the task (what the subject does)

- The experiment presents a pair of near-identical Gabor patterns, one to each eye, with a fixed phase displacement (`theta`) between the two eye images.
- The two images are shown at different relative contrasts (an interocular contrast ratio, `delta`), and the experiment cycles through a set of `delta` values and two phase `config` conditions (opposite sign phase offsets).
- On each trial the observer adjusts a vertical `flanking_bar` until the perceived alignment (phase) is matched or minimized, then confirms the response.
- The vertical position of the `flanking_bar` is converted to a perceived phase estimate (degrees) using a conversion factor (`DEG_PER_PIX`) and saved as `perceived_phase` along with `ratio` (delta) and `config`.

The per-trial CSV rows (as saved by `bc.py`) are:
- `trial` — trial index
- `ratio` — interocular contrast ratio (`delta`)
- `config` — phase configuration (1 or 2)
- `perceived_phase` — reported phase (degrees)

`fit.py` groups trials by `ratio` and `config`, computes the mean perceived phase for each config, and forms a net phase per `ratio` as a summary measure for model fitting.

---

## The model — formula and intuition

The model predicts perceived phase `phi` as a function of `delta` (interocular contrast ratio) with two free parameters `alpha` and `gamma` and a fixed stimulus parameter `theta` (the maximum stimulus phase displacement).

The model is implemented in three conceptual steps:

1. Scale the ratio relative to the balance point:
   - `r = (delta / alpha)**gamma`

2. Convert `r` into a normalized interaction value bounded in (−1, +1):
   - `f = (r - 1) / (r + 1)`

   Note: algebraically this is equivalent to a hyperbolic tangent in log space:
   - f = tanh( (gamma / 2) * ln(delta / alpha) )

   This reveals that the model is symmetric in log(delta/alpha) and that multiplicative deviations above and below `alpha` produce opposite `f` values of equal magnitude.

3. Map the bounded interaction `f` to a predicted phase `phi` that is constrained to the stimulus limits ±theta:
   - `phi(delta) = 2 * atan( f * tan(theta / 2) )`

Putting it all together (compact algebraic form):
- r = (delta / alpha)^gamma
- f = (r − 1) / (r + 1)
- phi(delta) = 2 * atan( f * tan(theta / 2) )

In code (conceptually):  
`phi = 2 * degrees( atan( (( (delta/alpha)**gamma - 1 ) / ( (delta/alpha)**gamma + 1 )) * tan(theta_rad / 2) ) )`

---

## Interpretation of parameters and terms

- `delta` — interocular contrast ratio for a trial (how much one eye's contrast differs from the other).
- `alpha` — balance ratio. When `delta = alpha`, we get `r = 1`, `f = 0` and `phi = 0`. That is, the two eyes contribute equally and no phase bias is predicted. Converting to decibels (useful for plotting symmetric log-space): `alpha_db = 20 * log10(alpha)`.
- `gamma` — slope/steepness parameter. Higher `gamma` produces a sharper transition from one eye dominating to the other around `alpha`. It controls sensitivity of `phi` to changes in `delta` (in log space).
- `theta` — maximum phase displacement used in the stimuli (in your code `theta = 45°`). The mapping with `atan` ensures `phi` remains bounded between `−theta` and `+theta`.
- `f` — normalized interaction function in (−1, +1). The particular `(r − 1)/(r + 1)` form is chosen for smoothness and boundedness; equivalently a `tanh` of a scaled log-ratio.

Key properties:
- Balanced point: `delta = alpha` → `phi = 0`.
- Right-eye strong: `delta >> alpha` → `r → +∞`, `f → +1` → `phi → +theta`.
- Left-eye strong: `delta << alpha` → `r → 0`, `f → −1` → `phi → −theta`.
- The model is symmetric in log-ratio space: doubling `delta` above `alpha` vs halving below produces opposite-sign predictions.

---

## Linear approximation near the balance point

For small deviations from `alpha`, `f` is small and `atan(x) ≈ x` yields:
- phi ≈ 2 * f * tan(theta/2)

So near the balance point the response is approximately linear in `f` (and therefore approximately linear in tanh((gamma/2) ln(delta/alpha))). This gives an intuitive gain factor controlled by `tan(theta/2)`.

---

## Why this functional form is used

- Bounded output: The `atan` + `tan(theta/2)` mapping guarantees the predicted `phi` cannot exceed the physically presented maximum phase `theta`.
- Smooth S-shape in log space: The `(r − 1)/(r + 1)` (or equivalently `tanh`) provides a standard logistic/tanh-like transition in log(delta) that captures gradual and saturating dominance shifts between eyes.
- Interpretable parameters: `alpha` corresponds to the balance point (an intuitive scalar: where eyes contribute equally), and `gamma` controls sharpness — both are easy to reason about and to report (with `alpha` commonly expressed in dB).

---

## Fitting strategy used in `fit.py`

- Observed data: for each `ratio` you have mean perceived phase computed as `(p1 - p2) / 2` where `p1` and `p2` are the mean phases for the two opposite-phase `config` conditions. This cancels sign flips introduced by stimulus phase configurations.
- Fit the model `phi(delta; alpha, gamma)` to the observed `phi` values with `curve_fit` to estimate `alpha` and `gamma`.
- Convert `alpha` to decibels for plotting: `alpha_db = 20 * log10(alpha)`.
- Plot the data and fitted S-curve vs `20*log10(delta)` (dB) to visualize symmetry and the balance point.

Practical recommendations:
- Use positive bounds for `alpha` and `gamma` during fitting (e.g., `alpha > 0`, `gamma > 0`) to ensure physical meaning.
- Reasonable initial guesses: `alpha ≈ 1.0`, `gamma ≈ 1.0–2.0`.
- If the fitted curve is mirrored relative to expectations, check the sign when computing the net mean phase (swap `(p1 - p2)` to `(p2 - p1)` if necessary).

---

## Visualization tips

- Plot x-axis in dB: `x_db = 20 * log10(delta)` to linearize and symmetrize multiplicative changes in ratio.
- Draw vertical lines at `0 dB` (equal contrast) and at `alpha_db` (balance point) to aid interpretation.
- Display the fitted `alpha` (in dB) and `gamma` on the figure legend or title.

---

## Short note about data and code locations

- The experimental script is `scripts/bc.py`. It saves trial-level CSV to `data/baseline_full_data.csv` by default.
- The fitting script is `scripts/fit.py`. Edit the top of that script if you want it to read a different CSV (for example, the output of `bc.py` instead of a simulated CSV).
