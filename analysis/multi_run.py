import json
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple

def load_results() -> Tuple[List[float], List[int]]:
    """Load and parse the simulation results from JSON."""
    with open('data/final_probs.json', 'r') as f:
        data = json.load(f)
    
    # Extract probabilities and convert outcomes to binary
    probabilities = [entry['p_final'] for entry in data]
    outcomes = [1 if entry['outcome'] == '1' else 0 for entry in data]
    
    return probabilities, outcomes

def compute_calibration_metrics(x_t: List[float], y_t: List[int], n_bins: int = 10) -> Tuple[float, float, List[float], List[float], List[int]]:
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
    plt.savefig('data/multi_run_reliability.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    # Load data
    probabilities, outcomes = load_results()
    
    # Compute calibration metrics
    ece, brier, bin_centers, empirical_freqs, bin_counts = compute_calibration_metrics(
        probabilities, outcomes
    )
    
    # Print results
    print("\nMarket Calibration Analysis")
    print(f"Expected Calibration Error (ECE): {ece:.4f}")
    print(f"Brier Score: {brier:.4f}")
    print("\nBin Statistics:")
    for i in range(len(bin_centers)):
        print(f"\nBin {i+1}:")
        print(f"  Center: {bin_centers[i]:.3f}")
        print(f"  Empirical Frequency: {empirical_freqs[i]:.3f}")
        print(f"  Count: {bin_counts[i]}")
        if bin_counts[i] > 0:
            ci = 1.96 * np.sqrt(empirical_freqs[i] * (1-empirical_freqs[i]) / bin_counts[i])
            print(f"  95% Confidence Interval: ±{ci:.3f}")
    
    # Plot reliability diagram
    plot_reliability_diagram(bin_centers, empirical_freqs, bin_counts, ece, brier)
    print("\nReliability diagram saved as '../data/multi_run_reliability.png'")

if __name__ == "__main__":
    main() 