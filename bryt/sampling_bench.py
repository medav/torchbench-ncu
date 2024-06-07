import subprocess
import sys
import os
import random
from scipy.stats.mstats import gmean

from . import parse_ncu


metrics = ','.join([
    'gpu__dram_throughput.avg.pct_of_peak_sustained_elapsed'
])


def run_and_parse_output(cmdline):
    print(' '.join(cmdline))
    stdout = subprocess.check_output(cmdline).decode('utf-8')
    num_kerns = 0
    for line in stdout.split('\n'):
        # print(line)
        if 'Runtime' in line:
            runtime = float(line.split()[-1])

        elif line.startswith('==PROF== Profiling'):
            num_kerns += 1

    return runtime, num_kerns

def count_kernels_nsys(prog_args):
    cmdline = [
        'nsys', 'profile', '--stats=true',
        '-o', 'report',
        '-f', 'true',
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
        # '--clock-control', 'none',
        '--cache-control', 'none',
        '--target-processes', 'all',
        # '--profile-from-start', 'no',
        '--metrics', metrics,
        '--kernel-id', '::Kernel:111111111111',
        *prog_cmdline
    ]

def ncu_sampled_cmdline(prog_cmdline, samp):

    if isinstance(samp, int):
        samp_str = {
            1: '',
            10: '.*0|1',
            100: '.*00|1',
            1000: '.*000|1',
            10000: '.*0000|1',
            100000: '.*00000|1',
        }[samp]
    elif isinstance(samp, str):
        samp_str = samp

    return [
        'ncu',
        # '--clock-control', 'none',
        '--cache-control', 'none',
        '--target-processes', 'all',
        # '--profile-from-start', 'no',
        '--metrics', metrics,
        '--kill', 'no',
        '--kernel-id', f'::Kernel:{samp_str}',
        *prog_cmdline
    ]


nk1 = count_kernels_nsys(make_prog_cmdline(mode, model, 1))
nk10 = count_kernels_nsys(make_prog_cmdline(mode, model, 10))

slope = (nk10 - nk1) / 9
intercept = nk1 - slope

TARGET_NUM_KERNELS = 10000

num_iters = int((TARGET_NUM_KERNELS - intercept) / slope)
prog_cmdline = make_prog_cmdline(mode, model, num_iters)

_, ns = run_and_parse_output(ncu_sampled_cmdline(prog_cmdline, 1))
assert ns > 0

actual_num_kerns = count_kernels_nsys(prog_cmdline)
print(f'Actual number of kernels: {actual_num_kerns}')
print(f'# Instances of "Kernel": {ns}')

no_ncu, _ = run_and_parse_output(prog_cmdline)
ncu_baseline, should_be_zero = \
    run_and_parse_output(ncu_baseline_cmdline(prog_cmdline))
assert should_be_zero == 0

if ns < 100:
    samp_100_ids = '|'.join(map(str, list(range(1, ns + 1))))
else:
    samp_100_ids = '|'.join(map(str, sorted(random.sample(list(range(1, ns + 1))), 100)))

if ns < 10:
    samp_1000_ids = '|'.join(map(str, list(range(1, ns + 1))))
else:
    samp_1000_ids = '|'.join(map(str, sorted(random.sample(list(range(1, ns + 1))), 10)))


samp_10000_ids = '|'.join(map(str, sorted(random.sample(list(range(1, ns + 1))), 1)))

ncu_100, act_samp_100 = \
    run_and_parse_output(ncu_sampled_cmdline(prog_cmdline, samp_100_ids))

ncu_1000, act_samp_1000 = \
    run_and_parse_output(ncu_sampled_cmdline(prog_cmdline, samp_1000_ids))

ncu_10000, act_samp_10000 = \
    run_and_parse_output(ncu_sampled_cmdline(prog_cmdline, samp_10000_ids))

print(f'Runtimes: {no_ncu:.2f} {ncu_baseline:.2f} {ncu_100:.2f} {ncu_1000:.2f}')
print(f'Slowdown for 1/100 (Actual: {act_samp_100}/{actual_num_kerns}): {ncu_100 / no_ncu:.2f}x {ncu_100 / ncu_baseline:.2f}x')
print(f'Slowdown for 1/1000 (Actual: {act_samp_1000}/{actual_num_kerns}): {ncu_1000 / no_ncu:.2f}x {ncu_1000 / ncu_baseline:.2f}x')
print(f'Slowdown for 1/10000 (Actual: {act_samp_10000}/{actual_num_kerns}): {ncu_10000 / no_ncu:.2f}x {ncu_10000 / ncu_baseline:.2f}x')

print(f'{model},{mode},{app_kerns},{actual_num_kerns},{no_ncu:.2f},{ncu_baseline:.2f},{ncu_100:.2f},{ncu_1000:.2f}')
