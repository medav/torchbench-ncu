import subprocess
import sys
import os
import random
from scipy.stats.mstats import gmean

from . import parse_ncu
from .parse_ncu import shortstr

def read_metrics(metrics_file):
    with open(metrics_file, 'r') as f:
        for line in f:
            if line.startswith(' '): continue
            if len(line.strip()) == 0: continue
            yield line.split()[0].strip()


selected_metrics = list(read_metrics('bryt/selected_metrics.txt'))

def get_num_passes(metrics):
    prog_cmdline = [
        'python',
        'bryt/one_kern.py'
    ]

    cmdline = [
        'ncu',
        '--target-processes', 'all',
        '--profile-from-start', 'no',
        '--metrics', ','.join(metrics),
        '-c', '1',
        '--kill', 'yes',
        *prog_cmdline
    ]

    try:
        stdout = subprocess.check_output(cmdline).decode('utf-8')

    except subprocess.CalledProcessError as e:
        print(e.output.decode('utf-8'))
        return -1

    for line in stdout.split('\n'):
        if 'Profiling "ampere_fp16_s16816gemm' in line:
            [n, p] = line.split()[-2:]

            assert p == 'passes' or p == 'pass'
            return int(n)


num_passes = dict()

with open('bryt/valid_pairs.txt', 'w') as f:
    for i in range(len(selected_metrics)):
        for j in range(i + 1, len(selected_metrics)):
            metrics = (selected_metrics[i], selected_metrics[j])
            num_passes[metrics] = get_num_passes(metrics)

            metric_str = f'{shortstr(metrics[0], 30)} x {shortstr(metrics[1], 30)}'
            print(f'{metric_str.ljust(63)}: {num_passes[metrics]}')

            if num_passes[metrics] == 1:
                print(f'{metrics[0]}, {metrics[1]}', file=f)

