import unittest
import core
import json
from copy import deepcopy


class MergeTestCase(unittest.TestCase):

    def setUp(self):
        with open('./lists/test_list.txt') as f:
            self.lsts = json.loads(f.read())
        self.merged = self.merge_func(deepcopy(self.lsts))

    def test_disjoint(self):
        """Check disjoint-ness of merged results"""
        from itertools import combinations
        for a,b in combinations(self.merged, 2):
            self.assertTrue(a.isdisjoint(b))

    def test_coverage(self):    # Credit to katrielalex
        """Check coverage original data"""
        merged_flat = set()
        for s in self.merged:
            merged_flat |= s

        original_flat = set()
        for lst in self.lsts:
            original_flat |= set(lst)

        self.assertTrue(merged_flat == original_flat)

    def test_subset(self):      # Credit to WolframH
        """Check that every original data is a subset"""
        for lst in self.lsts:
            self.assertTrue(any(set(lst) <= e for e in self.merged))


def get_TestCase(merge_function):
    def merge_func(self, *args, **kwargs):
        return merge_function(*args, **kwargs)
    setattr(MergeTestCase, 'merge_func', merge_func)
    return MergeTestCase


if __name__ == '__main__':
    for name,value in vars(core).items():
        if name.endswith('_merge'):
            print('\n  -- Going to test: {} --\n'.format(value.__doc__))
            Custom_TestCase = get_TestCase(value)
            suite = unittest.TestLoader().loadTestsFromTestCase(Custom_TestCase)
            unittest.TextTestRunner(verbosity=2).run(suite)
            input('Press Enter to continue')


