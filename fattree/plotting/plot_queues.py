import re
import sys
import argparse
import matplotlib.pyplot as plt

def parse_file(fname):
    pattern = re.compile(r"Queue\s+(.+?)\s+-- Size\s+(\d+)\s+-- Time\s+(\d+)")
    data = {}
    with open(fname) as f:
        for line in f:
            m = pattern.search(line)
            if not m:
                continue
            qname, size, t = m.group(1), int(m.group(2)), int(m.group(3))
            data.setdefault(qname, []).append((t, size))
    # sort each series by time
    for q in data:
        data[q].sort(key=lambda x: x[0])
    return data

def plot_data(data, title):
    fig, ax = plt.subplots(figsize=(10, 6))
    # filter out queues with max size less than 16000 bytes
    threshold = 16000
    data = {q: pts for q, pts in data.items() if max(size for _, size in pts) >= threshold}
    for qname, pts in data.items():
        times, sizes = zip(*pts)
        ax.plot(times, sizes, label=qname)
    ax.set_xlabel("Time (µs)")
    ax.set_ylabel("Queue Size (bytes)")
    ax.set_title(title)
    ax.grid(True, which='both', ls=':', lw=0.5)
    ax.legend(loc='best', fontsize='small', ncol=2)
    plt.tight_layout()
    plt.show()

def main():
    p = argparse.ArgumentParser(description="Plot queue sizes over time")
    p.add_argument("file", help="input trace file")
    args = p.parse_args()
    data = parse_file(args.file)
    plot_data(data, f"Queue Sizes in {args.file}")

if __name__ == "__main__":
    main()
