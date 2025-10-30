import pandas as pd
import matplotlib.pyplot as plt
import argparse

def load_data(file_path):
    """Load CSV data from the given file path."""
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return None

def plot_lambda_vs_miss_rate(files, labels):
    """Generate Lambda vs Miss Rate plot."""
    plt.figure(figsize=(10, 6))
    for file, label in zip(files, labels):
        data = load_data(file)
        if data is not None:
            grouped = data.groupby("Lambda", as_index=False).mean()
            plt.plot(grouped['Lambda'], grouped['Miss Rate (%)'], label=label)

    plt.title("Lambda vs Miss Rate")
    plt.xlabel("Lambda (λ)")
    plt.ylabel("Miss Rate (%)")
    plt.legend()
    plt.grid(True)
    plt.show()
    plt.savefig('output_plot_queue_exp_comparison1.png', format='png', dpi=300)

def plot_slack_margin_vs_miss_rate(files, labels):
    """Generate Slack Margin vs Miss Rate plot."""
    plt.figure(figsize=(10, 6))
    for file, label in zip(files, labels):
        data = load_data(file)
        if data is not None:
            grouped = data.groupby("Slack Margin", as_index=False).mean()
            plt.plot(grouped['Slack Margin'], grouped['Miss Rate (%)'], label=label)

    plt.title("Slack Margin vs Miss Rate")
    plt.xlabel("Slack Margin")
    plt.ylabel("Miss Rate (%)")
    plt.legend()
    plt.grid(True)
    plt.show()
    plt.savefig('output_plot_queue_exp_comparison2.png', format='png', dpi=300)

def main():
    parser = argparse.ArgumentParser(description="Compare results from multiple CSV files.")
    parser.add_argument("--files", nargs='+', required=True, help="Paths to the CSV files.")
    parser.add_argument("--labels", nargs='+', required=True, help="Labels for the CSV files.")
    args = parser.parse_args()

    if len(args.files) != len(args.labels):
        print("Error: Number of files and labels must match.")
        return

    # Generate plots
    plot_lambda_vs_miss_rate(args.files, args.labels)
    plot_slack_margin_vs_miss_rate(args.files, args.labels)

if __name__ == "__main__":
    main()
