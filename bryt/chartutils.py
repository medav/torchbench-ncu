import os
import sys
import numpy as np
import dataclasses
from matplotlib import pyplot as plt
from scipy.stats.mstats import gmean
from contextlib import contextmanager
from matplotlib.ticker import MaxNLocator
import pickle
import functools


colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
COL_WIDTH = (8.5 - 1.5 - 0.25) / 2
TEXT_WIDTH = 8.5 - 1.5

@contextmanager
def figure(width, height, nrows, ncols, name=None, **kwargs):
    name = name if name is not None else \
        os.path.basename(sys.argv[0]).replace('.py', '')

    fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=(width, height), **kwargs)
    yield fig, axs
    print(f'Saving {name}.pdf')
    os.makedirs('charts', exist_ok=True)
    plt.savefig(f'charts/{name}.pdf')

def sanitize(s):
    return s.replace('/', '_').replace('.', '_')

def cache_pickle(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        argss = '_'.join(str(arg) for arg in args) + \
            '_' + '_'.join(f'{k}={v}' for k, v in kwargs.items())
        filename = f'.chartcache/{func.__name__}.{sanitize(argss)}.cache.pkl'
        if os.path.exists(filename):
            # print(f'Loading {func.__name__} from cache')
            with open(filename, 'rb') as f:
                return pickle.load(f)
        else:
            print(f'Regenerating {func.__name__}...')
            ret = func(*args, **kwargs)

            os.makedirs('.chartcache', exist_ok=True)
            with open(filename, 'wb') as f:
                pickle.dump(ret, f)

            return ret

    return wrapper

