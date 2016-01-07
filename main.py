"""
Reproduce figure 6 from Steuer et al., (2003)
"""

import numpy as np
from tqdm import tqdm

from setup import generate_systems
from solver import solve_system, get_steady_state
from utils import compute_correlation_matrix, cache_data
from plotter import plot_system_overview, plot_ss_scatter


def analyze_system(system, repetition_num=100, filter_trivial_ss=True):
    """ Generate steady states for given system
    """
    ss_data = []
    for _ in range(repetition_num):
        sol = solve_system(system)

        ss = get_steady_state(sol)
        if not filter_trivial_ss or not any(ss <= 1e-10):
            ss_data.append(ss)
        else:
            return None

    plot_ss_scatter(np.array(ss_data))
    corr_mat = compute_correlation_matrix(np.array(ss_data))

    return corr_mat, sol

def cluster_data(data):
    """ Order data according to correlation matrices
    """
    return sorted(data, key=lambda e: np.sum(e[1]))

def main():
    """ Main interface
    """
    systems = generate_systems()

    data = []
    for syst in tqdm(systems):
        res = analyze_system(syst)
        if not res is None:
            cmat, sol = res
            data.append((syst, cmat, sol))

    cache_data(data)
    data = cluster_data(data)
    plot_system_overview(data)


if __name__ == '__main__':
    main()
