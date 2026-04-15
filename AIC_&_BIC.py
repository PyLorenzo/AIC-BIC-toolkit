import os
import numpy as np

def calculate_information_criteria(stats_file_path, k, N):
    """
    Reads the getLikeStats() output file to extract the Maximum Likelihood
    and computes both AIC and BIC.
    """
    if not os.path.exists(stats_file_path):
        raise FileNotFoundError(f"The file does not exist: {stats_file_path}")
        
    max_loglike = None
    
    # Read the file line by line for memory efficiency and speed
    with open(stats_file_path, 'r') as f:
        for line in f:
            # Look for the exact string identifying the best fit
            if line.startswith("Best fit sample -log(Like)"):
                # The line format is: "Best fit sample -log(Like) = 1328.142200"
                minus_loglike_str = line.split("=")[1].strip()
                
                # -log(Like) is minus_loglike. max_loglike is the negative of this.
                max_loglike = -float(minus_loglike_str)
                break 
                
    if max_loglike is None:
        raise ValueError(f"'Best fit sample -log(Like)' value not found in: {stats_file_path}")
    
    # AIC Calculation: 2k - 2ln(L)
    aic = 2 * k - 2 * max_loglike
    
    # BIC Calculation: k*ln(N) - 2ln(L)
    bic = k * np.log(N) - 2 * max_loglike
    
    return aic, bic, max_loglike

def get_jeffreys_evidence_statement(delta_val, criterion_name, model1_name, model2_name):
    """
    Evaluates the difference using Jeffreys' Scale (primarily used for BIC/Bayes Factors).
    delta_val = Model 2 - Model 1
    """
    abs_delta = abs(delta_val)
    
    if delta_val > 0:
        favored = model1_name
        disfavored = model2_name
    elif delta_val < 0:
        favored = model2_name
        disfavored = model1_name
    else:
        return f"Neither model is favored based on {criterion_name} (Delta = 0)."

    if abs_delta < 2:
        strength = "Weak/Inconclusive evidence"
    elif 2 <= abs_delta < 6:
        strength = "Positive evidence"
    elif 6 <= abs_delta < 10:
        strength = "Strong evidence"
    else: 
        strength = "Very strong (decisive) evidence"
        
    return f"{strength} favoring {favored} over {disfavored} (|Delta {criterion_name}| = {abs_delta:.2f})"

def get_burnham_anderson_statement(aic1, aic2, model1_name, model2_name):
    """
    Evaluates the AIC difference (Delta_i) using the Burnham and Anderson (2004) rules of thumb.
    Calculates delta as the absolute difference, always positive.
    """
    if aic1<aic2:
        delta_aic=aic2 - aic1
        best=model1_name
        worse=model2_name
    else:
        delta_aic=aic1 - aic2
        best=model2_name
        worse=model1_name

    # Burnham and Anderson rules of thumb for Delta_i
    if delta_aic <= 2:
        support = f"has SUBSTANTIAL support"
    elif 2 < delta_aic < 4:
        support = f"has LESS support (intermediate)"
    elif 4 <= delta_aic <= 7:
        support = f"has CONSIDERABLY LESS support"
    elif 7 < delta_aic <= 10:
        support = f"has MARGINAL support"
    else: 
        support = f"has ESSENTIALLY NO support"
        
    return f"Model '{worse}' {support} relative to the best model '{best}' (\u0394_AIC = {delta_aic:.2f})"

def perform_model_comparison(model1_info, model2_info, N, output_filename="model_comparison_results.txt"):
    """
    Executes the comparison, prints to console, and saves to file.
    """
    print(f"--- Extracting data for {model1_info['name']} ---")
    aic1, bic1, lnL1 = calculate_information_criteria(model1_info['path'], model1_info['k'], N)
    
    print(f"--- Extracting data for {model2_info['name']} ---")
    aic2, bic2, lnL2 = calculate_information_criteria(model2_info['path'], model2_info['k'], N)
    
    if aic1<aic2:
        delta_aic=aic2 - aic1    
    else:
        delta_aic=aic1 - aic2
    
    delta_bic = bic2 - bic1
    
    header = f"{'Model':<20} | {'k':<5} | {'Max ln(L)':<12} | {'AIC':<10} | {'BIC':<10}"
    separator = "-" * len(header)
    row1 = f"{model1_info['name']:<20} | {model1_info['k']:<5} | {lnL1:<12.2f} | {aic1:<10.2f} | {bic1:<10.2f}"
    row2 = f"{model2_info['name']:<20} | {model2_info['k']:<5} | {lnL2:<12.2f} | {aic2:<10.2f} | {bic2:<10.2f}"
    
    # Apply Burnham & Anderson for AIC and Jeffreys for BIC
    aic_statement = get_burnham_anderson_statement(aic1, aic2, model1_info['name'], model2_info['name'])
    bic_statement = get_jeffreys_evidence_statement(delta_bic, "BIC", model1_info['name'], model2_info['name'])
    
    final_output = (
        "==========================================================\n"
        "                MODEL COMPARISON ANALYSIS                 \n"
        "==========================================================\n\n"
        f"Total number of data points (N): {N}\n\n"
        "--- TABULAR RESULTS ---\n"
        f"{header}\n"
        f"{separator}\n"
        f"{row1}\n"
        f"{row2}\n\n"
        "--- DIFFERENCES (Model 2 - Model 1) ---\n"
        f"Delta AIC: {delta_aic:.2f}\n"
        f"Delta BIC: {delta_bic:.2f}\n\n"
        "--- CONCLUSIONS ---\n"
        f"AIC Analysis (Burnham & Anderson): \n  -> {aic_statement}\n\n"
        f"BIC Analysis (Jeffreys' Scale): \n  -> {bic_statement}\n"
        "=========================================================="
    )
    
    print("\n" + final_output)
    
    try:
        os.makedirs(os.path.dirname(output_filename), exist_ok=True)
        with open(output_filename, "w") as f:
            f.write(final_output)
        print(f"\nResults successfully saved to '{output_filename}'.")
    except Exception as e:
        print(f"\nError saving to file: {e}")

# ==========================================
# EXAMPLE USAGE
# ==========================================
if __name__ == "__main__":
    
    N_data_points = 2509
    
    model_1 = {
        'name': 'LCDM',
        'path': '/home/lbaldazzi/Documents/Dottorato/MCMCs/LCDM/No_H0_prior/Planck+DESI_BAO_DR2+DESY5_SNe/Like_statistics.txt', 
        'k': 6
    }
    
    model_2 = {
        'name': 'TPM',
        'path': '/home/lbaldazzi/Documents/Dottorato/MCMCs/TPM/No_H0_prior/Planck+DESI_BAO_DR2+DESY5_SNe/Like_statistics.txt', 
        'k': 10 
    }
    
    output_file = "/home/lbaldazzi/Documents/Dottorato/Scripts/Script_generici/Model_comparison/Results/No_H0_prior/PlikLiteHM-TTTEEE+low-TT+low-EE+PR4-Lensing+DESI_BAO_DR2+DESY5-SneIa/AIC_BIC_model_comparison.txt"
    
    perform_model_comparison(model_1, model_2, N_data_points, output_file)