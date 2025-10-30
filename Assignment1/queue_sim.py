#!/usr/bin/env python3
# queue_sim.py
import argparse
import collections
import csv
import logging
import os
from random import expovariate, sample, seed

from discrete_event_sim import Simulation, Event
from workloads import weibull_generator

# One possible modification is to use a different distribution for job sizes or and/or interarrival times.
# Weibull distributions (https://en.wikipedia.org/wiki/Weibull_distribution) are a generalization of the
# exponential distribution, and can be used to see what happens when values are more uniform (shape > 1,
# approaching a "bell curve") or less (shape < 1, "heavy tailed" case when most of the work is concentrated
# on few jobs).
# To use Weibull variates, for a given set of parameter do something like
# from workloads import weibull_generator
# gen = weibull_generator(shape, mean)
#
# and then call gen() every time you need a random variable

# columns saved in the CSV file
CSV_COLUMNS = ['lambd', 'mu', 'max_t', 'n', 'd', 'w']


class Queues(Simulation):
    """Simulation of a system with n servers and n queues.

    The system has n servers with one queue each. Jobs arrive at rate lambd and are served at rate mu.
    When a job arrives, according to the supermarket model, it chooses d queues at random and joins
    the shortest one.
    """

    def __init__(self, lambd, mu, n, d,
                 weibull_mode: bool, weibull_shape: float):
        super().__init__()
        self.running = [None] * n  # if not None, the id of the running job (per queue)
        self.queues = [collections.deque() for _ in range(n)]  # FIFO queues of the system
        # NOTE: we don't keep the running jobs in self.queues
        self.arrivals = {}  # dictionary mapping job id to arrival time
        self.completions = {}  # dictionary mapping job id to completion time
        self.lambd = lambd  # arrival rate
        self.n = n  # number of servers
        self.d = d  # number of queues to sample
        self.mu = mu  # service rate
        self.arrival_rate = lambd * n  # frequency of new jobs is proportional to the number of queues
        self.queue_length_distribution = collections.defaultdict(int)

        # New Modes
        self.weibull_mode = weibull_mode

        # Weibull mode
        if self.weibull_mode:
            self.weibull_shape = weibull_shape
            self.weibull_gen = weibull_generator(self.weibull_shape, 1 / self.arrival_rate)
            self.schedule(self.weibull_gen(), Arrival(0))
        else:
            self.schedule(expovariate(lambd), Arrival(0))

    def update_queue_length_distribution(self):
        for i in range(self.n):
            qlen = self.queue_len(i)
            self.queue_length_distribution[qlen] += 1

    def schedule_arrival(self, job_id):
        """Schedule the arrival of a new job."""

        # schedule the arrival following an exponential distribution, to compensate the number of queues the arrival
        # time should depend also on "n"

        # memoryless behavior results in exponentially distributed times between arrivals (we use `expovariate`)
        # the rate of arrivals is proportional to the number of queues
        if self.weibull_mode:
            next_arrival = self.weibull_gen()
        else:
            next_arrival = expovariate(self.arrival_rate)
        self.schedule(next_arrival, Arrival(job_id))

    def schedule_completion(self, job_id, queue_index):
        """Schedule the completion of a job."""

        # schedule the time of the completion event
        # check `schedule_arrival` for inspiration
        if self.weibull_mode:
            weibull_gen = weibull_generator(self.weibull_shape, self.mu)
            completion_delay = weibull_gen()
        else:
            completion_delay = expovariate(self.mu)

        # Schedule the job completion event
        self.schedule(completion_delay, Completion(job_id, queue_index))

    def queue_len(self, i):
        """Return the length of the i-th queue.
        
        Notice that the currently running job is counted even if it is not in self.queues[i]."""

        return (self.running[i] is not None) + len(self.queues[i])



class Arrival(Event):
    """Event representing the arrival of a new job."""

    def __init__(self, job_id):
        self.id = job_id

    def process(self, sim: Queues):
        """Process an arrival of a new job at the simulation."""
        sim.arrivals[self.id] = sim.t  # Log the arrival time

        sample_queues = sample(range(sim.n), sim.d)  # Choose d queues at random

        queue_index = min(sample_queues, key=sim.queue_len)

        if sim.running[queue_index] is None:
            sim.running[queue_index] = self.id
            sim.schedule_completion(self.id, queue_index)
        else:
            sim.queues[queue_index].append(self.id)

        sim.update_queue_length_distribution()  # Update after job is queued

        # Schedule the arrival of the next job
        next_job_id = self.id + 1  # increment to the next job ID
        sim.schedule_arrival(next_job_id)


class Completion(Event):
    """Job completion."""

    def __init__(self, job_id, queue_index):
        self.job_id = job_id  # currently unused, might be useful when extending
        self.queue_index = queue_index

    def process(self, sim: Queues):
        queue_index = self.queue_index
        assert sim.running[queue_index] == self.job_id  # the job must be the one running
        sim.completions[self.job_id] = sim.t

        queue = sim.queues[queue_index]

        if queue:  # If queue is not empty, choose next job based on scheduling type
            new_job_id = queue.popleft()
            sim.running[queue_index] = new_job_id  # Assign the next job
            sim.schedule_completion(new_job_id, queue_index)  # Schedule its completion
        else:
            sim.running[queue_index] = None  # No job is running on the queue

        sim.update_queue_length_distribution()


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--lambd', type=float, default=0.7, help="arrival rate")
    parser.add_argument('--mu', type=float, default=1, help="service rate")
    parser.add_argument('--max-t', type=float, default=1_000_000, help="maximum time to run the simulation")
    parser.add_argument('--n', type=int, default=1, help="number of servers")
    parser.add_argument('--d', type=int, default=1, help="number of queues to sample")
    parser.add_argument('--csv', help="CSV file in which to store results")
    parser.add_argument("--seed", help="random seed", default=42)
    parser.add_argument("--verbose", action='store_true')

    # weibull mode
    parser.add_argument("--weibull_mode", action='store_true',
                        help="Use Weibull distribution for arrival and service times")
    parser.add_argument("--weibull_shape", type=float, default=1, help="Shape parameter for Weibull distribution")

    args = parser.parse_args()

    params = [getattr(args, column) for column in CSV_COLUMNS[:-1]]
    # corresponds to params = [args.lambd, args.mu, args.max_t, args.n, args.d]

    if any(x <= 0 for x in params):
        logging.error("lambd, mu, max-t, n and d must all be positive")
        exit(1)

    if args.seed:
        seed(args.seed)  # set a seed to make experiments repeatable

    if args.verbose:
        # output info on stderr
        logging.basicConfig(format='{levelname}:{message}', level=logging.INFO, style='{')

    if args.lambd >= args.mu:
        logging.warning("The system is unstable: lambda >= mu")

    sim = Queues(args.lambd, args.mu, args.n, args.d,
                 args.weibull_mode, args.weibull_shape)

    sim.run(args.max_t)

    completions = sim.completions

    W = ((sum(completions.values()) - sum(sim.arrivals[job_id] for job_id in completions)) / len(completions))
    print(f"Average time spent in the system: {W}")

    # Theoretical M/M/1 (only valid if d=1, mu=1, etc.)
    if args.mu == 1 and args.lambd != 1 and args.d == 1:
        print(f"Theoretical expectation for random server choice (d=1): {1 / (1 - args.lambd)}")

    if args.csv is not None:
        with open(args.csv, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(params + [W])

    # Check if the CSV file exists
    file_name_plot = "d_out.csv"
    file_exists = os.path.isfile(file_name_plot)

    # Append results to CSV
    try:
        with open(file_name_plot, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(["queue_length", "count", "lambda", "d", "n"])

            for queue_length, count in sim.queue_length_distribution.items():
                writer.writerow([queue_length, count, args.lambd, args.d, args.n])
    except IOError as e:
        logging.error(f"Failed to write to file {file_name_plot}: {e}")
        exit(1)


if __name__ == '__main__':
    main()
