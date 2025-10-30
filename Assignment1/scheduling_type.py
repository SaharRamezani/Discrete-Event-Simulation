from enum import Enum

class SchedulingType(Enum):
    FIFO = "FIFO" # First In First Out
    SJF = "SJF"  # Shortest Job First
    EDF = "EDF"  # Earliest Deadline First
