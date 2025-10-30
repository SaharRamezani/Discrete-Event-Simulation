#!/bin/sh

VENV_DIR="../venv"
source $VENV_DIR/bin/activate

# Assign default values to variables or accept overrides via environment variables
POPULATION=${POPULATION:-100000}
INFECTED=${INFECTED:-3}
SEED=${SEED:-10}
AVG_CONTACT_TIME=${AVG_CONTACT_TIME:-1}
AVG_RECOVERY_TIME=${AVG_RECOVERY_TIME:-3}
VERBOSE=${VERBOSE:-true}
PLOT_INTERVAL=${PLOT_INTERVAL:-1}

# Construct the command with all the required arguments
python3 ./sir.py \
    --population $POPULATION \
    --infected $INFECTED \
    --seed $SEED \
    --avg-contact-time $AVG_CONTACT_TIME \
    --avg-recovery-time $AVG_RECOVERY_TIME \
    --plot_interval $PLOT_INTERVAL \
    $( [ "$VERBOSE" = true ] && echo "--verbose" )
