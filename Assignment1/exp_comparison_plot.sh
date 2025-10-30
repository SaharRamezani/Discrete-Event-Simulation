#!/bin/bash

VENV_DIR="../venv"
source $VENV_DIR/bin/activate

# Example usage of the Python script
python3 exp_comparison_plot.py \
  --files dl_mode_edf/dl.csv dl_mode_fifo/dl.csv \
  --labels "Deadline Mode with EDF" "Dealine Mode with FIFO"
