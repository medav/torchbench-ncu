from dataclasses import dataclass
from functools import singledispatch
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import itertools
import yaml
import glob

from . import parse_ncu
from .chartutils import *

apps = ['bert', 'dlrm', 'gc', 'mgn', 'nerf']
cats = ['Both Low', 'Low SM', 'Low DRAM', 'Neither Low']


colors = [
    '#f6511d',
    '#ffca3a',
    '#ffca3a',
    '#8ac926'
]

# print(type(cmap))
# matplotlib.colors.LinearSegmentedColormap

NBINS = 3
HATCHES = [None, '|||', '\\\\\\', None]

def util_to_bin(util : float): return min(int(util * NBINS), NBINS - 1)
def bin_to_pct(bin : int): return f'{100 * (bin / NBINS):.0f}%'
def bin_lb(bin : int): return bin / NBINS
def bin_ub(bin : int): return (bin + 1) / NBINS

pct_strs = [bin_to_pct(i) for i in range(NBINS + 1)]


def process_data(kerns : list[parse_ncu.Kernel]):
    data = np.zeros((NBINS, NBINS))
    for k in kerns:
        data[util_to_bin(k.dram_util), util_to_bin(k.sm_util)] += k.ncu_lat_ns

    return data / np.sum(data)

def data_to_bins(data : np.ndarray):
    assert data.shape == (NBINS, NBINS)

    return np.array([
        data[0, 0],
        data[1, 0] + data[2, 0],
        data[0, 1] + data[0, 2],
        data[1, 1] + data[2, 1] + data[1, 2] + data[2, 2]
    ])

def name_of(mode, app_name):
    return parse_ncu.shortstr(f'{mode} {app_name}', maxlen=20)

apps = []
for f in glob.glob('results/ncu.*.out'):
    [_, name, mode, _] = f.split('.')

    try:
        parse_ncu.parse_ncu_file(f)
        apps.append((mode, name))
    except: pass

with figure(width=8, height=4, nrows=1, ncols=1, sharey=True, sharex=True) as (fig, ax):
    bins = np.zeros((len(apps), len(cats)))

    for i, (mode, name) in enumerate(apps):
        kerns : list[parse_ncu.Kernel]
        kerns = parse_ncu.parse_ncu_file(f'results/ncu.{name}.{mode}.out')
        bins[i, :] = data_to_bins(process_data(kerns))

    names = [name_of(mode, app_name) for mode, app_name in apps]
    x_pos = np.arange(len(names))
    bottom = np.zeros(len(names))

    for cat_idx, cat in enumerate(cats):
        ax.bar(
            x_pos,
            bins[:, cat_idx],
            bottom=bottom,
            hatch=HATCHES[cat_idx],
            color=colors[cat_idx],
            edgecolor='black',
            width=0.6,
            label=cat)

        bottom += bins[:, cat_idx]

    # axs[ax_idx].set_xlabel(title, fontsize=8)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(names, fontsize=8, rotation=90)
    ax.tick_params(which='both', labelsize=8)
    ax.set_ylabel(f'Normalized GPU Time', fontsize=8)

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, 0.0), ncol=4, fontsize=8, frameon=False)

    plt.tight_layout(rect=[0, 0.16, 1, 1], pad=0.15)
    plt.subplots_adjust(hspace=0.2)

