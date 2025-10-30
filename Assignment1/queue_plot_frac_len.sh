#!/bin/bash

VENV_DIR="../venv"
source $VENV_DIR/bin/activate

CSV_FILE="d_out.csv"
MIN_QUEUE_LENGTH=1
MAX_QUEUE_LENGTH=14

#python3 ./plot_frac_queue_len.py --csv_file "$CSV_FILE" --min_queue_length "$MIN_QUEUE_LENGTH" --max_queue_length "$MAX_QUEUE_LENGTH"
python3 ./plot_frac_queue_len.py --min_queue_length "$MIN_QUEUE_LENGTH" --max_queue_length "$MAX_QUEUE_LENGTH" --use_theoretical