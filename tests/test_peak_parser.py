import os
from unittest import TestCase, skipIf

import scipy.stats as scits
import numpy.testing as npt

from peak_parser import *


class TestFileReader(TestCase):
    def test_simple_file(self):
        res = read_file('./tests/data/peak_data.csv')

        self.assertEqual(
            sorted(res.keys()), sorted([
                ('educt', 'c1'), ('educt', 'c2'),
                ('product', ('c1', 'r1', 'c3')),
                ('product', ('c2', 'r2', 'c1'))
            ]))

        self.assertEqual(res[('educt', 'c1')],
            [[1,2,3], [4,5,2], [10,20,30]])
        self.assertEqual(res[('educt', 'c2')],
            [[10,20,30]])
        self.assertEqual(res[('product', ('c1', 'r1', 'c3'))],
            [[2,1,3]])
        self.assertEqual(res[('product', ('c2', 'r2', 'c1'))],
            [[300,20,1]])

class TestNetworkDiscovery(TestCase):
    def setUp(self):
        self.data = read_file('./tests/data/peak_data.csv')

    def test_find_3_node_networks(self):
        motifs = find_3_node_networks(self.data)

        self.assertEqual(len(motifs), 1)
        self.assertEqual(motifs[0], (
            ('c2', 'r2', 'c1'),
            ([[10,20,30]], [[300,20,1]], [[1,2,3], [4,5,2], [10,20,30]])
        ))

    def test_get_complete_network(self):
        graph = get_complete_network(self.data, plot=False)

        self.assertEqual(sorted(graph.nodes()), sorted(['c2','c2, r2, c1','c1']))
        self.assertEqual(sorted(graph.edges()),
            sorted([('c2','c2, r2, c1'), ('c1','c2, r2, c1')]))

    def test_get_complete_network_nonstrict(self):
        graph = get_complete_network(self.data, strict=False, plot=False)

        self.assertEqual(sorted(graph.nodes()),
            sorted(['c2','c2, r2, c1','c1, r1, c3','c1','c3']))
        self.assertEqual(sorted(graph.edges()),
            sorted([
                ('c2','c2, r2, c1'), ('c1','c2, r2, c1'),
                ('c1','c1, r1, c3'), ('c3','c1, r1, c3')]))

class TestStatistics(TestCase):
    def setUp(self):
        data = read_file('./tests/data/peak_data.csv')
        self.motifs = find_3_node_networks(data)

    @skipIf('TRAVIS' in os.environ and os.environ['TRAVIS'] == 'true', 'Skip on Travis CI.')
    def test_compute_correlation_pairs(self):
        res = compute_correlation_pairs(self.motifs)
        corr1 = scits.pearsonr([300,20,1], [1,2,3])[0]
        corr2 = scits.pearsonr([300,20,1], [4,5,2])[0]
        corr3 = scits.pearsonr([300,20,1], [10,20,30])[0]
        corr4 = scits.pearsonr([10,20,30], [4,5,2])[0]

        self.assertEqual(len(res), 3)
        self.assertEqual(res[0], [1, corr4, 1])
        npt.assert_allclose(res[1], [corr1])
        npt.assert_allclose(res[2], [corr1, corr2, corr3])

        res2 = compute_overview_histogram(res)
        npt.assert_allclose(res2,
            [1, corr4, 1, corr1, corr1, corr2, corr3])
