"""
Setup system
"""

import itertools

import numpy as np
import numpy.random as npr


class SDESystem(object):
    """ Bundle import SDE information
    """
    def __init__(self, J, D, E, I):
        self.jacobian = J
        self.fluctuation_vector = D
        self.external_influence = E
        self.initial_state = I

def generate_basic_system(v_in=5, k_m=1, k_23=2, D=1):
    """ Generate system according to paper
    """
    k_12 = k_13 = k_out = k_m

    jacobian = np.array([
        [-(k_12 + k_12),    0,      0],
        [k_12,              -k_23,  0],
        [k_13,              k_23,   -k_out]
    ])
    external_influence = np.array([v_in, 0, 0])
    fluctuation_vector = np.array([D, 0, 0])
    initial_state = np.array([1, 1, 1])

    system = SDESystem(
        jacobian, fluctuation_vector,
        external_influence, initial_state)
    return system

def generate_random_plus(num=5):
    """ Generate randomized versions of initial system plus one node
    """
    res = [generate_basic_system()]
    for _ in range(num-1):
        s = generate_basic_system()

        # extend by fourth node
        s.fluctuation_vector = np.append(s.fluctuation_vector, 0)
        s.external_influence = np.append(s.external_influence, 0)
        s.initial_state = np.append(s.initial_state, 1)

        s.jacobian = npr.choice([0, 1], (4, 4))
        res.append(s)
    return res

def generate_plus():
    """ Generate initial system plus one node
    """
    def with_fourth_node(hs, vs):
        s = generate_basic_system()

        # adjust other vectors
        s.fluctuation_vector = np.append(s.fluctuation_vector, 0)
        s.external_influence = np.append(s.external_influence, 0)
        s.initial_state = np.append(s.initial_state, 1)

        # check validity of input
        dim = s.jacobian.shape[0]
        assert len(hs) == dim, 'Horizontal stack must have length %d' % dim
        assert len(vs) == dim+1, 'Vertical stack must have length %d' % (dim+1)

        # adjust jacobian
        s.jacobian = np.hstack((s.jacobian, np.array(hs).reshape(-1, 1)))
        s.jacobian = np.vstack((s.jacobian, vs))

        return s

    res = [generate_basic_system()]

    res.append(with_fourth_node(
        [0, 0, 0], [0, 0, 0, 0]))
    res.append(with_fourth_node(
        [0, 0, 1], [1, 0, 0, 0]))
    res.append(with_fourth_node(
        [0, 1, 0], [1, 0, 0, 0]))
    res.append(with_fourth_node(
        [1, 0, 0], [1, 0, 0, 0]))

    return res

def generate_varied_parameters(num=5):
    """ Vary parameters of initial system
    """
    res = [generate_basic_system()]
    for _ in range(num-1):
        s = generate_basic_system(
            k_m=npr.uniform(0, 3),
            k_23=npr.uniform(0, 3))
        res.append(s)
    return res

def generate_all(size=3, force_self_inhibition=True):
    """ Generate all networks of given size
    """
    assert size > 0, 'Require positive network size'

    # get all possible edges as node pairs
    all_edges = list(itertools.product(range(size), repeat=2))

    # compute all possible subsets
    def powerset(inp):
        return itertools.chain.from_iterable(
            itertools.combinations(inp, r) for r in range(len(inp)+1))

    all_subgraphs = powerset(all_edges)

    # generate system definitions
    v_in = 5
    D = 1
    k = 1

    res = []
    for graph in all_subgraphs:
        # input only on first node
        external_influence = np.array([v_in] + [0] * (size-1))
        fluctuation_vector = np.array([D] + [0] * (size-1))
        initial_state = np.array([1] * size)

        # create fitting jacobian
        jacobian = np.zeros((size, size))
        for i, j in graph:
            if i == j:
                jacobian[i, j] = -k
            else:
                jacobian[i, j] = k

        if force_self_inhibition:
            if not (np.diagonal(jacobian) < 0).all():
                continue

        # assemble system
        system = SDESystem(
            jacobian, fluctuation_vector,
            external_influence, initial_state)

        res.append(system)

    return res


generate_systems = generate_all
