import time

class Timer:
    def __init__(self):
        self._start_time = time.perf_counter()
        
    def reset(self):
        self._start_time = time.perf_counter()
        
    def elapsed(self):
        return time.perf_counter() - self._start_time  