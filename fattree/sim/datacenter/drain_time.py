import argparse
import re
import numpy as np

def analyze_draining_times(file_path):
    # Read the file and extract lines
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Extract draining times using regex
    draining_times = []
    pattern = r"Total Time Spend Draining \d+ \d+ of \d+ -- (\d+\.\d+)"

    for line in lines:
        match = re.search(pattern, line)
        if match:
            draining_times.append(float(match.group(1)))

    # Calculate min, max, avg, and median
    draining_min = np.min(draining_times) if draining_times else None
    draining_max = np.max(draining_times) if draining_times else None
    draining_avg = np.mean(draining_times) if draining_times else None
    draining_median = np.median(draining_times) if draining_times else None
    number_of_flows = len(draining_times)

    # Print results
    print(f"Total flows analyzed: {number_of_flows}")
    print(f"Minimum draining time: {draining_min:.2f}%")
    print(f"Maximum draining time: {draining_max:.2f}%")
    print(f"Average draining time: {draining_avg:.2f}%")
    print(f"Median draining time: {draining_median:.2f}%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze draining times from simulation logs.')
    parser.add_argument('--file_path', type=str, help='Path to the input log file.')
    args = parser.parse_args()
    
    analyze_draining_times(args.file_path)
