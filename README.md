
# Distributed Computing 
# Assignment 1

## Additional File Explanation

- exp_comparison_plot.py
  * This file contains the code to generate the plots for the comparison of the Deadline mode with FIFO vs Shortest Deadline first.
- plot_frac_queue_len.py
  * This file contains the code to generate the plots for the fractional queue length (For Theoretical and Simulation).
- queue_sim_dl.py
  * This file contains the code to simulate the queue with deadline mode with EDF (Earliest Deadline First).
- queue_sim_sh_sjf.py
  *  This file contains the code to simulate the queue with Shortest Job First.

## Setup Instructions

To ensure that the environment is properly set up, please follow the steps below:

### 1. Create a Python Environment and Install Dependencies
Run the following script to create a Python virtual environment and install all the necessary dependencies:

```bash
  bash requirements.sh
```

Alternatively, you can manually install the dependencies listed in `requirements.txt` if you prefer.

### 2. Run the Queue Experiments
To simulate the experiments related to queues, execute the following script:

```bash
  cd Assignment1 && bash queue_experiments.sh
```

### 3. Queue Experiments with weibull distribution
This will run simulations with weibull distribution and generate the required data files for further processing.

```bash
  cd Assignment1 && bash queue_experiments_a_weibull.sh
```

### 4. Queue Experiments with Shortest job first
This will run simulations with shortest job first and generate the required data files for further processing.

```bash
  cd Assignment1 && bash queue_experiments_sch_sjf.sh
```

### 5. Queue Experiments with deadline mode 
This will run simulations with deadline mode and generate the required data files for further processing.

```bash
  cd Assignment1 && bash queue_experiments_dl.sh
```

### Plot the Queue Results
This will generate visualizations related to the queue waiting time.
```bash
  cd Assignment1 && bash queue_plot.sh
```

#### Plot Fractional Queue Length
To plot the fractional queue length, run the following script.

There are two approaches to run this script:
1. Run the script to produce theoretical results 
2. Run the script to produce simulation results (commented out in the script)
```bash
  cd Assignment1 && bash queue_plot_frac_len.sh
```

This will create plots for the fractional queue length over time.

---

## Cleanup
If you want to clean up the environment, deactivate the Python virtual environment and remove any generated files.

```bash
  deactivate
```

---

# Assignment 2

## Overview

This repository contains a **discrete-event simulation** system for experimenting with data backup and redundancy in various network configurations. The simulation models a set of nodes (or a single client plus multiple servers) that:

- **Fail** and **recover** randomly, based on a specified lifetime distribution.  
- **Exchange data blocks** (upload/download) using erasure coding parameters (`n`, `k`).  
- Optionally **adapt** how many blocks (`n_active`) they actually store if redundancy becomes threatened (“dynamic n”).

You can test two main scenarios:

1. **Peer-to-Peer (P2P)**:  
   Each node stores its own erasure-coded data across other peers.  
2. **Client-Server**:  
   A single client stores data on multiple dedicated servers.

## File Structure

- **`storage.py`**  
  - Main simulation driver and entry point.
  - Defines the `Backup` class (a subclass of `Simulation`) that schedules node events.
  - Implements the `Node` class for node state, upload/download speeds, etc.
  - Contains event subclasses (`Online`, `Fail`, `BlockBackupComplete`, etc.) that handle specific behaviors.
  - Includes the `main()` function for command-line argument parsing and launching simulations.

- **`discrete_event_sim.py`**  
  - Provides the **discrete-event simulation** framework.
  - Defines the `Simulation` base class with:
    - An event queue (priority queue, using `heapq`).
    - Methods to `schedule` events and `run` them until a time limit is reached.
  - Includes plotting utilities (using `matplotlib`) to parse simulation logs and generate line plots of failures, recoveries, backups, and data losses over time.

- **Configuration Files**
  - **`p2p.cfg`**: Settings for peer-to-peer simulations (e.g., number of peers, speeds, `n`, `k`, etc.).
  - **`client_server.cfg`**: Settings for a mixed client-server simulation.

- **`storage.sh`** (Bash script)
  - Example script showing how to invoke `storage.py` with different scenarios and flags (e.g., `--n-active`).
  - Creates `logs/` and `plots/` directories, then saves logs and plots there.

- **`logs/`**  
  - Directory where `.log` files from simulations are stored.
  This directory is produced when you run the storage.sh file. This directory is needed when plotting the diagrams.

- **`plots/`**  
  - Directory where `.png` plots (failures over time, recoveries, backups, data-loss, etc.) are saved.
  - This directory is produced when you run the storage.sh file.

## Installation

1. **Python 3.7+**  
   Make sure you have Python 3.7 or higher installed.

2. **Optional: Create a Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   
3. **Install Required Packages**

   You can install the required Python libraries with:
  
   ```bash
   pip install -r requirements.txt
   ```

  ---
  
## Usage

### 1. Basic Run

To run the simulation with a specific configuration, use the following command (you can change this part in the storage.sh file, run the code using that file for better results):

```bash
python3 storage.py p2p.cfg --max-t "100 years" --verbose
```

If you want to simulate using "n_active" feature, try the following command:

```bash
python3 storage.py p2p.cfg --max-t "100 years" --verbose --n-active 5  --tolerance 1 # or whatevet number you want
```

 --tolerance 1 means less than how many redundant blocks you think might put us in the danger zone.
Also you can simply run storage.sh or modify it with the desired configs.

---

## Key Features

### Dynamic `n_active`
The simulation supports a **dynamic redundancy strategy** where nodes can incrementally activate more blocks (`n_active`) as redundancy becomes insufficient. This feature:

- **Reduces overhead**: Nodes begin with fewer active blocks, requiring fewer backup operations initially.
- **Maintains reliability**: The system dynamically adjusts `n_active` to meet redundancy requirements, preventing excessive data loss.

### Visualization
The simulation produces visual outputs for quick analysis of system performance:

- **Failures over time**: Helps assess the failure rates of nodes in the system.
- **Recoveries over time**: Tracks how often nodes recover from failures.
- **Backups over time**: Shows the volume of backup operations under different scenarios.
- **Data Losses over time**: Highlights the system's ability to prevent unrecoverable data loss.

---

## Frequently Asked Questions (FAQ)

### 1. What is the purpose of `n` and `k`?
`n` and `k` are erasure-coding parameters:
- **`n`**: Total number of blocks (data + parity) used to store the data.
- **`k`**: Number of blocks required to recover the full data.

For example, if `n=10` and `k=8`, there are 2 parity blocks. Any 8 out of the 10 blocks can reconstruct the original data.

### 2. What is `n_active`?
`n_active` represents the number of blocks a node actively uses at a given time:
- By default, `n_active = n` (all blocks are used).
- Dynamic `n_active` allows nodes to start with fewer active blocks and increase the count only when redundancy becomes insufficient.

### 3. Can I simulate custom configurations?
Yes, you can edit the `.cfg` files to set custom parameters (e.g., node counts, lifetimes, speeds, and storage sizes). You can also modify the Python code to add new event types or redundancy strategies.
