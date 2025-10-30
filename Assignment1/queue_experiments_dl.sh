#/bin/sh

VENV_DIR="../venv"
source $VENV_DIR/bin/activate

# Set the scheduling type here (FIFO, SJF, or EDF)
SCHEDULING="EDF"

for SLACK_MARGIN in 1 2 5 10; do
  for LAMBD in 0.5 0.7 0.9 0.95 0.99; do
   for D in 1 2 5 10; do
    echo "\nRunning simulation with LAMBDA=$LAMBD, d=$D in deadline mode with scheduling $SCHEDULING and slack margin $SLACK_MARGIN"
    # Running in deadline mode (Each task have a deadline)
    ./queue_sim_dl.py --lambd $LAMBD --d $D --n 10 --csv out.csv --max-t 100_000 --deadline_mode --slack_margin $SLACK_MARGIN --scheduling_type $SCHEDULING
   done
  done
done
