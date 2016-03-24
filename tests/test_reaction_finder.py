from unittest import TestCase

from reaction_finder import *


class TestMatcher(TestCase):
    def test_simple_match(self):
        cgroups = {'foo': 3, 'bar': 1}
        rspec = {'foo': 2, 'bar': 1}

        self.assertTrue(match(cgroups, rspec))

    def test_simple_mismatch(self):
        cgroups = {'foo': 1, 'bar': 1}
        rspec = {'foo': 2, 'bar': 1}

        self.assertFalse(match(cgroups, rspec))

class TestPairFinder(TestCase):
    def test_simple_finder(self):
        cdata = {
            'fooC': {'H': 3, 'O': 2},
            'barC': {'H': 4, 'O': 1},
            'bazC': {'H': 0, 'O': 3}
        }
        rdata = {
            'rea1': {
                'c1': {'H': 3, 'O': 2},
                'c2': {'H': 4, 'O': 0},
                'res': {'H': -1, 'O': 2}
            },
            'rea2': {
                'c1': {'H': 0, 'O': 1},
                'c2': {'H': 1, 'O': 1},
                'res': {'H': 1, 'O': 0}
            }
        }

        res = check_pair('fooC', 'barC', cdata, rdata)
        self.assertEqual(sorted(res), ['rea1', 'rea2'])

        res = check_pair('barC', 'fooC', cdata, rdata)
        self.assertEqual(res, ['rea2'])

        res = check_pair('fooC', 'bazC', cdata, rdata)
        self.assertEqual(sorted(res), [])

        res = check_pair('bazC', 'fooC', cdata, rdata)
        self.assertEqual(sorted(res), ['rea2'])

        res = check_pair('barC', 'bazC', cdata, rdata)
        self.assertEqual(res, [])

        res = check_pair('bazC', 'barC', cdata, rdata)
        self.assertEqual(res, ['rea2'])

class TestCompoundGuesser(TestCase):
    def test_simple_generation(self):
        cdata = {
            'fooC': {'H': 3, 'O': 2},
            'barC': {'H': 4, 'O': 1},
            'bazC': {'H': 0, 'O': 3}
        }
        rdata = {
            'rea1': {
                'c1': {'H': 3, 'O': 2},
                'c2': {'H': 4, 'O': 0},
                'res': {'H': -1, 'O': 2}
            },
            'rea2': {
                'c1': {'H': 0, 'O': 1},
                'c2': {'H': 1, 'O': 1},
                'res': {'H': 1, 'O': 0}
            }
        }
        combs = {
            'rea1': [('fooC', 'barC')]
        }

        res = guess_new_compounds(combs, cdata, rdata)

        self.assertTrue(len(res), 1)
        self.assertEqual(res['(fooC) rea1 (barC)'], {'H': 6, 'O': 5})

class TestFileInput(TestCase):
    def test_reaction_reader(self):
        data = read_reactions_file('./tests/data/reactions.csv')

        self.assertEqual(len(data), 3)
        self.assertEqual(
            data['rea1'], {
                'c1': {'-H': 3, '-O': 2},
                'c2': {'-H': 4, '-O': 0},
                'res': {'-H': -1, '-O': 2}
            })
        self.assertEqual(
            data['rea2'], {
                'c1': {'-H': 0, '-O': 1},
                'c2': {'-H': 1, '-O': 1},
                'res': {'-H': 1, '-O': 0}
            })
        self.assertEqual(
            data['rea3'], {
                'c1': {'-H': 2, '-O': 3},
                'c2': None,
                'res': {'-H': -2, '-O': -1}
            })
