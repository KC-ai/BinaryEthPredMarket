import json
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple

def load_results() -> Tuple[List[float], List[int]]:
    """Load and parse the simulation results from JSON."""
    with open('data/odds_sequence.json', 'r') as f:
        data = json.load(f)
    
    # Extract probabilities and convert outcomes to binary
    probabilities = [entry['p_final'] for entry in data]
    outcomes = [1 if entry['outcome'] == 'Yes' else 0 for entry in data]
    
    return probabilities, outcomes

def simulate_outcomes(probabilities: List[float], p_true: float, n_simulations: int = 1000) -> List[Tuple[float, float]]:
    """Simulate market outcomes for each probability."""
    results = []
    for p in probabilities:
        # Simulate n_simulations outcomes for this probability
        outcomes = np.random.binomial(1, p_true, n_simulations)
        # Record (probability, average outcome)
        results.append((p, np.mean(outcomes)))
    return results

def compute_calibration_metrics(x_t: List[float], y_t: List[float], n_bins: int = 10) -> Tuple[float, float, List[float], List[float], List[int]]:
    """Compute ECE and Brier score, and prepare data for reliability diagram."""
    # Sort data by predicted probability
    sorted_indices = np.argsort(x_t)
    x_t = np.array(x_t)[sorted_indices]
    y_t = np.array(y_t)[sorted_indices]
    
    # Create bins
    bin_edges = np.linspace(0, 1, n_bins + 1)
    bin_indices = np.digitize(x_t, bin_edges) - 1
    
    # Initialize arrays for bin statistics
    bin_centers = []
    empirical_freqs = []
    bin_counts = []
    
    # Compute statistics for each bin
    for i in range(n_bins):
        mask = bin_indices == i
        if np.any(mask):
            bin_centers.append(np.mean(x_t[mask]))
            empirical_freqs.append(np.mean(y_t[mask]))
            bin_counts.append(np.sum(mask))
        else:
            bin_centers.append(np.nan)
            empirical_freqs.append(np.nan)
            bin_counts.append(0)
    
    # Remove empty bins
    valid_mask = ~np.isnan(bin_centers)
    bin_centers = np.array(bin_centers)[valid_mask]
    empirical_freqs = np.array(empirical_freqs)[valid_mask]
    bin_counts = np.array(bin_counts)[valid_mask]
    
    # Compute ECE
    ece = np.sum(np.abs(empirical_freqs - bin_centers) * (bin_counts / len(x_t)))
    
    # Compute Brier score
    brier = np.mean((x_t - y_t) ** 2)
    
    return ece, brier, bin_centers, empirical_freqs, bin_counts

def plot_reliability_diagram(bin_centers: List[float], empirical_freqs: List[float], bin_counts: List[int], ece: float, brier: float):
    """Plot the reliability diagram with calibration metrics."""
    plt.figure(figsize=(10, 8))
    
    # Plot diagonal (perfect calibration)
    plt.plot([0, 1], [0, 1], 'k--', label='Perfect calibration')
    
    # Plot calibration points
    plt.scatter(bin_centers, empirical_freqs, c='blue', s=100, label='Calibration points')
    
    # Add error bars (binomial confidence intervals)
    n = len(bin_centers)
    for i in range(n):
        p = empirical_freqs[i]
        n_samples = bin_counts[i]
        if n_samples > 0:
            ci = 1.96 * np.sqrt(p * (1-p) / n_samples)  # 95% confidence interval
            plt.errorbar(bin_centers[i], p, yerr=ci, fmt='none', color='blue', alpha=0.3)
    
    # Add labels and title
    plt.xlabel('Predicted Probability (Market Price)', fontsize=12)
    plt.ylabel('Empirical Frequency (Actual Outcomes)', fontsize=12)
    plt.title(f'Market Reliability Diagram\nECE = {ece:.3f}, Brier = {brier:.3f}', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Set axis limits and ticks
    plt.xlim(-0.05, 1.05)
    plt.ylim(-0.05, 1.05)
    plt.xticks(np.linspace(0, 1, 11))
    plt.yticks(np.linspace(0, 1, 11))
    
    # Save plot
    plt.savefig('data/single_run_reliability.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    # Parameters
    p_true = 0.7  # True probability of Yes outcome
    n_simulations = 1000  # Number of simulations per probability
    
    # Load and process data
    probabilities, outcomes = load_results()
    
    # Simulate outcomes
    results = simulate_outcomes(probabilities, p_true, n_simulations)
    x_t = [r[0] for r in results]
    y_t = [r[1] for r in results]
    
    # Compute calibration metrics
    ece, brier, bin_centers, empirical_freqs, bin_counts = compute_calibration_metrics(x_t, y_t)
    
    # Print results
    print(f"\nCalibration Analysis (p_true = {p_true})")
    print(f"Expected Calibration Error (ECE): {ece:.4f}")
    print(f"Brier Score: {brier:.4f}")
    print("\nBin Statistics:")
    for i in range(len(bin_centers)):
        print(f"Bin {i+1}:")
        print(f"  Center: {bin_centers[i]:.3f}")
        print(f"  Empirical Frequency: {empirical_freqs[i]:.3f}")
        print(f"  Count: {bin_counts[i]}")
    
    # Plot reliability diagram
    plot_reliability_diagram(bin_centers, empirical_freqs, bin_counts, ece, brier)
    print("\nReliability diagram saved as 'data/single_run_reliability.png'")

if __name__ == "__main__":
    main() 