# AIC & BIC Model Comparison Tool

A Python utility for **Bayesian model selection** in cosmological MCMC analyses. It reads the likelihood statistics produced by `getLikeStats()` (e.g., from CosmoMC/Cobaya pipelines), computes the **Akaike Information Criterion (AIC)** and the **Bayesian Information Criterion (BIC)**, and interprets the results using two established statistical scales.

---

## Table of Contents

- [Background](#background)
- [Formulae](#formulae)
- [Interpretation Scales](#interpretation-scales)
- [Requirements](#requirements)
- [Input File Format](#input-file-format)
- [Usage](#usage)
- [Output](#output)
- [License](#license)

---

## Background

When comparing competing cosmological models (e.g., ΛCDM vs. a model with extra parameters), maximising the likelihood alone always favours the more complex model. Information criteria penalise this complexity by adding a term proportional to the number of free parameters *k*, thereby implementing **Occam's razor** statistically.

---

## Formulae

### Akaike Information Criterion (AIC)

$$\text{AIC} = 2k - 2\ln\hat{L}$$

where:
- $k$ — number of free parameters in the model
- $\hat{L}$ — maximum likelihood of the model

The penalty term $2k$ grows **linearly** with the number of parameters, making AIC relatively lenient towards complexity. It is asymptotically equivalent to leave-one-out cross-validation and is most useful when the goal is **predictive accuracy**.

### Bayesian Information Criterion (BIC)

$$\text{BIC} = k\ln N - 2\ln\hat{L}$$

where:
- $N$ — total number of data points
- $k$ — number of free parameters
- $\hat{L}$ — maximum likelihood of the model

The penalty term $k\ln N$ grows **logarithmically with the dataset size**, making BIC more conservative than AIC for large $N$. It is derived as an approximation to the **log marginal likelihood** (Bayes factor) and is therefore better suited for **model selection**.

> **Note on the input value.** `getLikeStats()` reports `-log(Like)` = $-\ln\hat{L}$. The code recovers $\ln\hat{L} = -(-\ln\hat{L})$ before substituting into the formulae.

---

## Interpretation Scales

### AIC — Burnham & Anderson (2004)

The model with the **lower AIC** is preferred. Its competitors are ranked by $\Delta_i = AIC_i - AIC_{min}$:

| $\Delta_i$ | Interpretation |
|---|---|
| $\leq 2$ | Substantial support |
| $2 < \Delta_i < 4$ | Less support (intermediate) |
| $4 \leq \Delta_i \leq 7$ | Considerably less support |
| $7 < \Delta_i \leq 10$ | Marginal support |
| $> 10$ | Essentially no support |

### BIC — Jeffreys' Scale

$\Delta\text{BIC} = \text{BIC}_2 - \text{BIC}_1$. A **negative** value favours Model 2; a **positive** value favours Model 1.

| $\Delta BIC$ | Strength of evidence |
|---|---|
| $< 2$ | Weak / Inconclusive |
| 2-6 | Positive |
| 6-10 | Strong |
| $> 10$ | Very strong (decisive) |

---

## Requirements

- Python ≥ 3.7
- NumPy

Install dependencies with:

```bash
pip install numpy
```

---

## Input File Format

The script expects a plain-text statistics file containing a line of the form:

```
Best fit sample -log(Like) = <value>
```

This is the standard output of `getLikeStats()` in CosmoMC/Cobaya. Example:

```
Best fit sample -log(Like) = 1328.142200
```

The parser locates this line with `str.startswith()` and splits on `=` to extract the numerical value.

---

## Usage

Edit the `__main__` block in `AIC_&_BIC.py` to point to your statistics files:

```python
N_data_points = 2509          # Total number of data points

model_1 = {
    'name': 'LCDM',
    'path': '/path/to/LCDM/Like_statistics.txt',
    'k': 6                    # Number of free parameters
}

model_2 = {
    'name': 'MyModel',
    'path': '/path/to/MyModel/Like_statistics.txt',
    'k': 10
}

output_file = '/path/to/output/AIC_BIC_results.txt'

perform_model_comparison(model_1, model_2, N_data_points, output_file)
```

Then run:

```bash
python "AIC_&_BIC.py"
```

---

## Output

The script prints results to the terminal and writes them to `output_file`. A typical output looks like:

```
==========================================================
                MODEL COMPARISON ANALYSIS                 
==========================================================

Total number of data points (N): 2509

--- TABULAR RESULTS ---
Model                | k     | Max ln(L)    | AIC        | BIC       
-----------------------------------------------------------------------
LCDM                 | 6     | -1328.14     | 2668.28    | 2703.77   
TPM                  | 10    | -1320.05     | 2660.10    | 2719.07   

--- DIFFERENCES (Model 2 - Model 1) ---
Delta AIC: 8.18
Delta BIC: 15.30

--- CONCLUSIONS ---
AIC Analysis (Burnham & Anderson): 
  -> Model 'LCDM' has ESSENTIALLY NO support relative to the best model 'TPM' (Δ_AIC = 8.18)

BIC Analysis (Jeffreys' Scale): 
  -> Very strong (decisive) evidence favoring LCDM over TPM (|Delta BIC| = 15.30)
==========================================================
```

> This example illustrates a typical tension between AIC and BIC: AIC rewards the extra likelihood gained by the more complex model, while BIC's stronger complexity penalty favours the simpler one.

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
