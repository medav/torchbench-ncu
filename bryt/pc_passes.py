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


all_metrics = list(read_metrics('bryt/all_metrics.txt'))

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

with open('bryt/num_passes.txt', 'w') as f:
    for metric in all_metrics:
        num_passes[metric] = get_num_passes([metric])
        print(f'{shortstr(metric, 50).ljust(50)}: {num_passes[metric]}')

        if num_passes[metric] > 0:
            print(f'{metric} : {num_passes[metric]}', file=f)


