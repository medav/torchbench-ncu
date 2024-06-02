import subprocess
import sys
import os
import random
from scipy.stats.mstats import gmean

from . import parse_ncu


metrics = ','.join([
    'gpu__dram_throughput.avg.pct_of_peak_sustained_elapsed'
])


def get_runtime(cmdline, ignore_no_kernels=False):
    # print(' '.join(cmdline))
    stdout = subprocess.check_output(cmdline).decode('utf-8')
    for line in stdout.split('\n'):
        if 'No kernels were profiled' in line and not ignore_no_kernels:
            print('No kernels were profiled:', ' '.join(cmdline))
            print(stdout)
            raise RuntimeError('No kernels were profiled')

        if 'Runtime' in line:
            runtime = float(line.split()[-1])

    return runtime

def count_kernels_nsys(prog_args):
    cmdline = [
        'nsys', 'profile', '--stats=true',
        *prog_args
    ]

    stdout = subprocess.check_output(cmdline, stderr=subprocess.DEVNULL).decode('utf-8')
    for line in stdout.split('\n'):
        if 'cudaLaunchKernel' in line:
            return int(line.split()[2])


def ceildiv(n, d):
    return (n + d - 1) // d

result_dir = os.environ.get('RESULTS', './results/')

mode = sys.argv[1]
model = sys.argv[2]

ncu_file = f'{result_dir}/ncu.{model}.{mode}.out'
app_kerns = len(parse_ncu.parse_ncu_file(ncu_file))


def make_prog_cmdline(mode, model, num_iters):
    return [
        'python',
        'bryt/run_wrapper.py',
        mode,
        model,
        str(num_iters),
    ]

def ncu_baseline_cmdline(prog_cmdline):
    return [
        'ncu',
        '--clock-control', 'none',
        '--cache-control', 'none',
        '--target-processes', 'all',
        # '--profile-from-start', 'no',
        '--metrics', metrics,
        '--kernel-id', ':::111111111111',
        *prog_cmdline
    ]

def ncu_sampled_cmdline(prog_cmdline, kid):
    return [
        'ncu',
        '--clock-control', 'none',
        '--cache-control', 'none',
        '--target-processes', 'all',
        # '--profile-from-start', 'no',
        '--metrics', metrics,
        '--kill', 'no',
        '-c', '1',
        '-s', str(kid),
        *prog_cmdline
    ]


# nk1 = count_kernels_nsys(make_prog_cmdline(mode, model, 1))
# nk10 = count_kernels_nsys(make_prog_cmdline(mode, model, 10))

# slope = (nk10 - nk1) / 9
# intercept = nk1 - slope
# print(f'Kernel count: {nk1} {nk10} {slope} {intercept}')


for samp in [1000, 10000, 100000]:
    print(f'Sampling: {samp} kernels')
    num_iters = ceildiv(samp, app_kerns)
    prog_cmdline = make_prog_cmdline(mode, model, num_iters)

    actual_num_kerns = count_kernels_nsys(prog_cmdline)
    print(f'    + Actual number of kernels: {actual_num_kerns}')

    no_ncu = get_runtime(prog_cmdline)
    ncu_baseline = get_runtime(ncu_baseline_cmdline(prog_cmdline), ignore_no_kernels=True)
    ncu_sampled = get_runtime(ncu_sampled_cmdline(prog_cmdline, actual_num_kerns - 1))

    print(f'    + Runtimes: {no_ncu:.2f} {ncu_baseline:.2f} {ncu_sampled:.2f}')
    print(f'    + Slowdown for 1/{samp}: {ncu_sampled / no_ncu:.2f}x {ncu_sampled / ncu_baseline:.2f}x')

