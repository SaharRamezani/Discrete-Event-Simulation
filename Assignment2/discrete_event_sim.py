import heapq
import logging
import sys
import matplotlib.pyplot as plt
import os
import re


# TODO: implement the event queue! - Done
# suggestion: have a look at the heapq library (https://docs.python.org/dev/library/heapq.html)
# and in particular heappush and heappop

class Simulation:
    """Subclass this to represent the simulation state.

    Here, self.t is the simulated time and self.events is the event queue.
    """

    def __init__(self):
        """Extend this method with the needed initialization.  - Done

        You can call super().__init__() there to call the code here.
        """

        self.t = 0  # simulated time
        self.events = []  # set up self.events as an empty queue

    def schedule(self, delay, event):
        """Add an event to the event queue after the required delay."""

        # add event to the queue at time self.t + delay
        event_time = self.t + delay
        heapq.heappush(self.events, (event_time, event))

    def decide_which_plot(self):
        # Get the path of the current file
        file_path = os.path.abspath(__file__)
        # Get the directory containing the current file
        current_dir = os.path.dirname(file_path)

        p2p_log_files = [
            os.path.join(current_dir, 'logs/simulation_p2p.log'),
            os.path.join(current_dir, 'logs/extension_simulation_p2p.log')
        ]
        client_server_log_files = [
            os.path.join(current_dir, 'logs/simulation_client_server.log'),
            os.path.join(current_dir, 'logs/extension_simulation_client_server.log')
        ]
        plots_p2p = [
            os.path.join(current_dir, 'plots/simulation_p2p.png'),
            os.path.join(current_dir, 'plots/extension_simulation_p2p.png')
        ]
        plots_client_server = [
            os.path.join(current_dir, 'plots/simulation_client_server.png'),
            os.path.join(current_dir, 'plots/extension_simulation_client_server.png')
        ]
        plots_combined = [
            os.path.join(current_dir, 'plots/combined_simulation_p2p.png'),
            os.path.join(current_dir, 'plots/combined_simulation_client_server.png')
        ]

        if any('p2p.cfg' in arg for arg in sys.argv):
            if '--n-active' in sys.argv:
                self.plot_results(p2p_log_files[1], 'P2P Extension Simulation Results', plots_p2p[1])
            else:
                self.plot_results(p2p_log_files[0], 'P2P Simulation Results', plots_p2p[0])
        elif any('client_server.cfg' in arg for arg in sys.argv):
            if '--n-active' in sys.argv:
                self.plot_results(client_server_log_files[1], 'Client-Server Extension Simulation Results', plots_client_server[1])
            else:
                self.plot_results(client_server_log_files[0], 'Client-Server Simulation Results',  plots_client_server[0])

        if all(os.path.exists(log_file) for log_file in p2p_log_files):
            self.plot_combined_results(p2p_log_files, 'Combined P2P Simulation Results', plots_combined[0])

        if all(os.path.exists(log_file) for log_file in client_server_log_files):
            self.plot_combined_results(client_server_log_files, 'Combined Client-Server Simulation Results', plots_combined[1])

    def run(self, max_t=float('inf')):
        """Run the simulation until the event queue is empty or max_t is reached."""
        while self.events and self.events[0][0] <= max_t:
            t, event = heapq.heappop(self.events)  # Get the first event from the queue
            if t > max_t:
                break
            self.t = t
            event.process(self)

        self.decide_which_plot()
        
    def plot_combined_results(self, log_file, title, file_path):
        def process_log_file(log_file):
            failures = []
            recoveries = []
            backups = []

            with open(log_file, 'r') as f:
                for line in f:
                    parts = line.strip().split(':')
                    try:
                        time_str = parts[1].strip()
                        event_type = parts[2].strip().split()[0]
                        time = self.convert_time_to_days(time_str)
                        if 'fails' in event_type:
                            failures.append((time, 1))
                        elif 'recovers' in event_type:
                            recoveries.append((time, 1))
                        elif 'BlockBackupComplete' in event_type or 'BlockRestoreComplete' in event_type:
                            backups.append((time, 1))
                    except:
                        continue

            # Convert to cumulative counts
            return {
                "failures": self.cumulative_count(failures),
                "recoveries": self.cumulative_count(recoveries),
                "backups": self.cumulative_count(backups),
            }

        # Process both log files
        data1 = process_log_file(log_file[0])
        data2 = process_log_file(log_file[1])

        # Plot the results
        plt.figure(figsize=(12, 8))

        plt.subplot(4, 1, 1)
        plt.plot(*zip(*data1["failures"]), label='Failures (Non-Dynamic)')
        plt.plot(*zip(*data2["failures"]), label='Failures (Dynamic)', linestyle='--')
        plt.xlabel('Time (days)')
        plt.ylabel('Failures')
        plt.title('Failures over time')
        plt.legend()

        plt.subplot(4, 1, 2)
        plt.plot(*zip(*data1["recoveries"]), label='Recoveries (Non-Dynamic)')
        plt.plot(*zip(*data2["recoveries"]), label='Recoveries (Dynamic)', linestyle='--')
        plt.xlabel('Time (days)')
        plt.ylabel('Recoveries')
        plt.title('Recoveries over time')
        plt.legend()

        plt.subplot(4, 1, 3)
        plt.plot(*zip(*data1["backups"]), label='Backups (Non-Dynamic)')
        plt.plot(*zip(*data2["backups"]), label='Backups (Dynamic)', linestyle='--')
        plt.xlabel('Time (days)')
        plt.ylabel('Backups')
        plt.title('Backups over time')
        plt.legend()

        plt.suptitle(title)
        plt.tight_layout()
        plt.savefig(file_path)   

    def plot_results(self, log_file, title, file_path):
        failures = []
        recoveries = []
        backups = []

        with open(log_file, 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                try:
                    time_str = parts[1].strip()
                    event_type = parts[2].strip().split()[0]
                    time = self.convert_time_to_days(time_str)
                    if 'fails' in event_type:
                        failures.append((time, 1))
                    elif 'recovers' in event_type:
                        recoveries.append((time, 1))
                    elif 'BlockBackupComplete' in event_type:
                        backups.append((time, 1))
                except:
                    continue

        # Convert to cumulative counts
        failures = self.cumulative_count(failures)
        recoveries = self.cumulative_count(recoveries)
        backups = self.cumulative_count(backups)

        plt.figure(figsize=(12, 8))

        plt.subplot(4, 1, 1)
        plt.plot(*zip(*failures), label='Failures')
        plt.xlabel('Time (days)')
        plt.ylabel('Failures')
        plt.title('Failures over time')
        plt.legend()

        plt.subplot(4, 1, 2)
        plt.plot(*zip(*recoveries), label='Recoveries')
        plt.xlabel('Time (days)')
        plt.ylabel('Recoveries')
        plt.title('Recoveries over time')
        plt.legend()

        plt.subplot(4, 1, 3)
        plt.plot(*zip(*backups), label='Backups')
        plt.xlabel('Time (days)')
        plt.ylabel('Backups')
        plt.title('Backups over time')
        plt.legend()

        plt.suptitle(title)
        plt.tight_layout()
        plt.savefig(file_path)

    def convert_time_to_days(self, time_str):
        """Helper function to convert time string to days."""
        # Define regex patterns for different time components
        patterns = {
            'years': r'(\d+)\s*years?',
            'weeks': r'(\d+)\s*weeks?',
            'days': r'(\d+)\s*days?',
            'hours': r'(\d+)\s*hours?',
            'minutes': r'(\d+)\s*minutes?',
            'seconds': r'(\d+)\s*seconds?'
        }
        
        # Initialize time components to zero
        years, weeks, days, hours, minutes, seconds = 0, 0, 0, 0, 0, 0
        
        # Extract time components using regex
        for unit, pattern in patterns.items():
            match = re.search(pattern, time_str)
            if match:
                value = int(match.group(1))
                if unit == 'years':
                    years = value
                elif unit == 'weeks':
                    weeks = value
                elif unit == 'days':
                    days = value
                elif unit == 'hours':
                    hours = value
                elif unit == 'minutes':
                    minutes = value
                elif unit == 'seconds':
                    seconds = value
        
        # Convert time components to days
        total_days = (years * 365) + (weeks * 7) + days + (hours / 24) + (minutes / 1440) + (seconds / 86400)
        return total_days

    def log_info(self, msg):
        logging.info(f'{self.t:.2f}: {msg}')

    def cumulative_count(self, events):
        """Helper function to convert event list to cumulative counts."""
        cumulative = []
        count = 0
        for time, value in events:
            count += value
            cumulative.append((time, count))
        return cumulative


class Event:
    """
    Subclass this to represent your events.

    You may need to define __init__ to set up all the necessary information.
    """

    def process(self, sim: Simulation):
        raise NotImplementedError

    def __lt__(self, other):
        """Method needed to break ties with events happening at the same time."""

        return id(self) < id(other)
