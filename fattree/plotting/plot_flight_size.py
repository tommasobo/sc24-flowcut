import re
import sys
import argparse
import matplotlib.pyplot as plt


def parse_file(fname):
    # Pattern to capture flow flight size with timer
    flight_pattern = re.compile(r"Flow\s+(.+?)\s+--\s+Flight Size\s+(\d+)\s+--\s+Timer\s+(\d+)")
    # Pattern to capture stop-sending markers
    marker_pattern = re.compile(r"Flowcut must send stop sending \d+ at (\d+)")

    data = {}
    markers = []
    with open(fname) as f:
        for line in f:
            # check for stop-sending markers
            mm = marker_pattern.search(line)
            if mm:
                markers.append(int(mm.group(1)))
                continue
            # extract flight size entries with timer
            fmatch = flight_pattern.search(line)
            if not fmatch:
                continue
            flowname, size, timer = fmatch.group(1), int(fmatch.group(2)), int(fmatch.group(3))
            data.setdefault(flowname, []).append((timer, size))
    # sort each series by time
    for flow in data:
        data[flow].sort(key=lambda x: x[0])
    return data, markers


def plot_data(data, markers, title):
    fig, ax = plt.subplots(figsize=(10, 6))
    for flow, pts in data.items():
        times, sizes = zip(*pts)
        ax.plot(times, sizes, label=flow)
    # plot vertical markers for stop-sending events
    for t in markers:
        ax.axvline(t, color='red', linestyle='--', alpha=0.7)
    ax.set_xlabel("Time (µs)")
    ax.set_ylabel("Flight Size (bytes)")
    ax.set_title(title)
    ax.grid(True, which='both', ls=':', lw=0.5)
    ax.legend(loc='best', fontsize='small', ncol=2)
    plt.tight_layout()
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Plot flow flight sizes over time")
    parser.add_argument("file", help="input trace file")
    args = parser.parse_args()
    data, markers = parse_file(args.file)
    plot_data(data, markers, f"Flight Sizes in {args.file}")


if __name__ == "__main__":
    main()
