#/bin/sh

VENV_DIR="../venv"
source $VENV_DIR/bin/activate

for LAMBD in 0.5 0.7 0.9 0.95 0.99; do
 for D in 1 2 5 10; do
  echo "\nRunning simulation with LAMBD=$LAMBD, D=$D"
  ./queue_sim.py --lambd $LAMBD --d $D --n 10 --csv out.csv --max-t 100_000 --verbose
 done
done
