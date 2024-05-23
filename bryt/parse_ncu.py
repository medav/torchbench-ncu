from dataclasses import dataclass
import functools
import pandas as pd

@dataclass
class Kernel:
    kid : int
    name : str
    grid : tuple
    block : tuple
    metrics : dict

    @functools.cached_property
    def sanitized_name(self):
        sn = self.name \
            .replace('void ', '') \
            .replace('at::native::', '') \
            .replace('<unnamed>::', '') \
            .replace('cutlass::', '')

        if '<' in sn: sn = sn[:sn.index('<')]
        if '(' in sn: sn = sn[:sn.index('(')]
        return sn

    @property
    def ncu_lat_ns(self): return self.metrics['gpu__time_duration.sum']

    @property
    def dram_util(self): return self.metrics['gpu__dram_throughput.avg.pct_of_peak_sustained_elapsed'] / 100

    @property
    def sm_util(self): return self.metrics['sm__throughput.avg.pct_of_peak_sustained_elapsed'] / 100

    @property
    def tensor_util(self): return self.metrics['sm__pipe_tensor_cycles_active.avg.pct_of_peak_sustained_elapsed'] / 100


class Reader(object):
    def __init__(self, g):
        self.g = g
    def read(self, n=0):
        try: return next(self.g)
        except StopIteration: return ''

def shortstr(s : str, maxlen : int = 20):
    if len(s) <= maxlen: return s
    return s[:maxlen - 3] + '...'

def read_ncu_output(output):
    it = iter(output.split('\n'))
    line = ''
    while not line.startswith('"ID","Process ID","Process Name",'):
        line = next(it)
    yield line + '\n'
    for line in it: yield line + '\n'

def parse_int_tuple(s):
    return tuple(map(int, s.strip('()').split(',')))

def parse_ncu_file(outfile):
    with open(outfile, 'r') as f:
        df = pd.read_csv(Reader(read_ncu_output(f.read())))

    ids = [None]
    names = dict()
    grids = dict()
    blocks = dict()
    metrics = dict()

    for row in df.iterrows():
        row = row[1]
        if ids[-1] != row['ID']: ids.append(row['ID'])
        names[row['ID']] = row['Kernel Name']
        grids[row['ID']] = parse_int_tuple(row['Grid Size'])
        blocks[row['ID']] = parse_int_tuple(row['Block Size'])
        if row['ID'] not in metrics: metrics[row['ID']] = dict()
        metrics[row['ID']][row['Metric Name']] = row['Metric Value']

    return [Kernel(i, names[i], grids[i], blocks[i], metrics[i]) for i in ids[1:]]


if __name__ == '__main__':
    import sys
    outfile = sys.argv[1]
    kerns = parse_ncu_file(outfile)
    print(f'{"Kernel".ljust(50)}  {"Latency".rjust(10)} {"SM".rjust(6)} {"Tensor".rjust(6)} {"DRAM".rjust(6)}')
    k : Kernel
    for k in kerns:
        print(f'{shortstr(k.sanitized_name, maxlen=50).ljust(50)}: {k.ncu_lat_ns:10.0f} {k.sm_util:6.2f} {k.tensor_util:6.2f} {k.dram_util:6.2f}')
