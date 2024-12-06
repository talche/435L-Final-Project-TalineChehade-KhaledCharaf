# performance_profile.py

import pstats
from pstats import SortKey
import os

PROFILE_DIR = 'performance_profiler'

def analyze_profiles():
    for filename in os.listdir(PROFILE_DIR):
        if filename.endswith('.prof'):
            print(f"\n--- Profiling Report for {filename} ---")
            filepath = os.path.join(PROFILE_DIR, filename)
            p = pstats.Stats(filepath)
            p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(20)  # Top 20 functions


if __name__ == "__main__":
    analyze_profiles()
