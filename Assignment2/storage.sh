#!/bin/bash

echo "Running the simulation ..."

VENV_DIR="../venv"
source $VENV_DIR/bin/activate

mkdir -p logs
mkdir -p plots

# Run the storage simulation with the provided configuration
python3 storage.py p2p.cfg --max-t "100 years" --verbose > logs/simulation_p2p.log 2>&1
python3 storage.py client_server.cfg --max-t "100 years" --verbose > logs/simulation_client_server.log 2>&1

echo "Simulation result is saved in simulation_p2p.log and simulation_client_server.log file."

# Run the storage simulation with the provided configuration
python3 storage.py p2p.cfg --max-t "100 years" --verbose --n-active 5 --tolerance 1 > logs/extension_simulation_p2p.log 2>&1
python3 storage.py client_server.cfg --max-t "100 years" --verbose --n-active 5 --tolerance 1 > logs/extension_simulation_client_server.log 2>&1

echo "Simulation (extension) result is saved in extension_simulation_p2p.log and extension_simulation_client_server.log file."

deactivate

# Check if the current directory is ~/Desktop/DC_2/dcasign/
if [ "$(pwd)" == "$HOME/Desktop/DC_2/dcasign" ]; then
    cd Assignment2
fi