import random
import time
import glob

from . import parse_ncu

def simulate_client(app_num_kerns : int, app_lat : float, load : float, tot_time : float, samp_len : int, offset : int):
    # Calculate the number of iterations based on the app latency and load
    total_iterations = int(tot_time / app_lat)
    load_iterations = int(total_iterations * load)

    kids = set()
    for _ in range(load_iterations):
        for i in range(offset, app_num_kerns, samp_len):
            kids.add(i)

    return kids

def get_coverage(app_run_offsets, app_kerns):
    coverage = []
    for app_index, offsets in app_run_offsets.items():
        unique_offsets = set(offsets)
        c_i = len(unique_offsets) / app_kerns[app_index]
        coverage.append(c_i)

    avg_coverage = sum(coverage) / len(coverage)
    return coverage, avg_coverage

def main():
    num_clients = 1000
    samp_len = 1000
    num_kerns = []
    lats = []
    num_apps = 20

    for i, f in enumerate(glob.glob('results/ncu.*.out')):
        [_, name, mode, _] = f.split('.')

        try:
            kerns = parse_ncu.parse_ncu_file(f)
            num_kerns.append(len(kerns))
            lats.append(sum(k.ncu_lat_ns for k in kerns) / 1e9)

            print(f"Reading {name} ({mode}): {num_kerns[-1]} kernels, {lats[-1]:.2f} s")
        except: pass

        if num_apps is not None and i > num_apps: break

    num_intervals = 12 * 6  # Time interval in hours
    interval_time = 600  # Time interval in seconds
    l = 0.1  # Load (% of time)

    app_run_offsets = {app_i: set() for app_i in range(len(num_kerns))}

    client_app_index = {
        i: random.randint(0, len(num_kerns) - 1)
        for i in range(num_clients)
    }


    for h in range(num_intervals):
        print(f"Interval {h + 1}/{num_intervals}")

        client_offsets = {
            i: random.randint(0, samp_len - 1)
            for i in range(num_clients)
        }

        for i in range(num_clients):
            app_index = client_app_index[i]
            app_num_kerns = num_kerns[app_index]
            app_lat = lats[app_index]
            app_run_offsets[app_index].update(
                simulate_client(
                    app_num_kerns, app_lat, l, interval_time, samp_len, client_offsets[i]))

        coverage, avg_coverage = get_coverage(app_run_offsets, num_kerns)
        print(f"Average coverage: {avg_coverage:.2f}")

    coverage, avg_coverage = get_coverage(app_run_offsets, num_kerns)
    for app_index, c_i in enumerate(coverage):
        print(f"Coverage of app {app_index}: {c_i:.2f}")

    print(f"Average coverage: {avg_coverage:.2f}")

if __name__ == "__main__":
    main()

