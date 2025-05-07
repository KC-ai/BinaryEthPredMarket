import json
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple

def load_sequence() -> List[dict]:
    """Load and parse the odds sequence from JSON."""
    with open('odds_sequence.json', 'r') as f:
        data = json.load(f)
    
    # Convert string ETH amounts to floats
    for entry in data:
        entry['yesPool'] = float(entry['yesPool'])
        entry['noPool'] = float(entry['noPool'])
    
    return data

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

def plot_reliability_diagram(bin_centers: List[float], empirical_freqs: List[float], ece: float, brier: float):
    """Plot the reliability diagram with calibration metrics."""
    plt.figure(figsize=(8, 8))
    
    # Plot diagonal (perfect calibration)
    plt.plot([0, 1], [0, 1], 'k--', label='Perfect calibration')
    
    # Plot calibration points
    plt.scatter(bin_centers, empirical_freqs, c='blue', label='Calibration points')
    
    # Add labels and title
    plt.xlabel('Predicted Probability')
    plt.ylabel('Empirical Frequency')
    plt.title(f'Reliability Diagram\nECE = {ece:.3f}, Brier = {brier:.3f}')
    plt.legend()
    plt.grid(True)
    
    # Save plot
    plt.savefig('reliability_diagram.png')
    plt.close()

def main():
    # Parameters
    p_true = 0.7  # True probability of Yes outcome
    n_simulations = 1000  # Number of simulations per probability
    
    # Load and process data
    sequence = load_sequence()
    probabilities = [entry['probability'] for entry in sequence]
    
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
    plot_reliability_diagram(bin_centers, empirical_freqs, ece, brier)
    print("\nReliability diagram saved as 'reliability_diagram.png'")

if __name__ == "__main__":
    main() 