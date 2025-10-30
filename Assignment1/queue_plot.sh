#!/bin/sh

VENV_DIR="../venv"
source $VENV_DIR/bin/activate

./plot_queue_w.py out.csv --n 10 --d 1 2 5 10 --max-t 100_000 --log-scale