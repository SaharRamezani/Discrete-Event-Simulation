#!/usr/bin/env python3
# plot_frac_queue_len.py
import argparse
import csv
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np


def process_csv_data(csv_file):
    """
    Processes CSV data into a nested dictionary structure.
    """
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    with open(csv_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            queue_length = int(row["queue_length"])
            count = int(row["count"])
            lambd = float(row["lambda"])
            d = int(row["d"])
            data[d][lambd][queue_length] += count
    return data


def theoretical_distribution(d, lambd, max_queue_length):
    """
    Computes the theoretical distribution using the formula.
    Raises an error if d <= 1 to avoid division by zero.
    """
    if d <= 1:
        raise ValueError(f"Invalid value of 'd': {d}. 'd' must be greater than 1.")

    fractions = []
    for i in range(1, max_queue_length + 1):
        fraction = lambd ** ((d ** i - 1) / (d - 1))
        fractions.append(fraction)
    return fractions


def plot_distributions(data, max_queue_length=14, min_queue_length=1, use_theoretical=False):
    """
    Plots queue length distributions, either theoretical or from CSV data.
    """
    choices = sorted(data.keys())  # Get all unique values of `d`
    lambd_values = sorted({lambd for d in data for lambd in data[d].keys()})  # Unique λ values

    colors = ['blue', 'orange', 'green', 'red']
    linestyles = ['-', '--', '-.', ':']

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()  # Flatten to iterate easily

    for idx, d in enumerate(choices):
        if idx >= len(axes):  # Avoid index errors for more than 4 choices
            break
        ax = axes[idx]

        for lambd_idx, lambd in enumerate(lambd_values):
            if use_theoretical:
                try:
                    # Plot theoretical distribution
                    queue_lengths = list(range(1, max_queue_length + 1))
                    fractions = theoretical_distribution(d, lambd, max_queue_length)
                except ValueError as e:
                    print(f"Skipping theoretical distribution for d={d}: {e}")
                    continue
            else:
                # Plot from CSV data
                queue_lengths = sorted(data[d][lambd].keys())
                counts = np.array([data[d][lambd][ql] for ql in queue_lengths])

                # Calculate the total count for normalization
                total_counts_lambda = sum(counts)

                # Calculate cumulative counts and normalize
                cumulative_counts = np.cumsum(counts[::-1])[::-1]
                fractions = cumulative_counts / total_counts_lambda if total_counts_lambda > 0 else np.zeros_like(
                    queue_lengths)

            ax.plot(queue_lengths, fractions, label=f'λ = {lambd}',
                    color=colors[lambd_idx % len(colors)],
                    linestyle=linestyles[lambd_idx % len(linestyles)])
        ax.set_xlim(min_queue_length, max_queue_length)
        ax.set_title(f"{d} choices")
        ax.set_xlabel("Queue length")
        ax.set_ylabel("Fraction of queues with at least that size")
        ax.legend()
    plt.tight_layout()
    plt.show()
    plt.savefig('output_plot_frac_queue_len.png', format='png', dpi=300)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot theoretical or CSV-based queue distributions.")
    parser.add_argument("--csv_file", type=str, default="d_out.csv", help="Path to the input CSV file.")
    parser.add_argument("--max_queue_length", type=int, default=14, help="Maximum queue length for the plot.")
    parser.add_argument("--min_queue_length", type=int, default=1, help="Minimum queue length for the plot.")
    parser.add_argument("--use_theoretical", action="store_true", help="Use theoretical data instead of CSV data.")

    args = parser.parse_args()

    if args.use_theoretical:
        #  Theoretical data for plotting the theoretical distribution
        unique_d = [2, 3, 5, 10]
        unique_lambdas = [0.5, 0.9, 0.95, 0.99]
        data = {d: {lambd: {} for lambd in unique_lambdas} for d in unique_d}

        for d in unique_d:
            for lambd in unique_lambdas:
                for i in range(1, args.max_queue_length + 1):
                    try:
                        fraction = lambd ** ((d ** i - 1) / (d - 1))
                        data[d][lambd][i] = fraction
                    except ZeroDivisionError:
                        print(f"Skipping theoretical calculation for d={d}, i={i} due to division by zero.")
    else:
        data = process_csv_data(args.csv_file)  # to plot for the simulated data

    plot_distributions(data, args.max_queue_length, args.min_queue_length, use_theoretical=args.use_theoretical)
