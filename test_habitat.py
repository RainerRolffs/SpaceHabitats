import math
import unittest

from habitat import Habitat
from input import Input
from result import Result


class TestHabitat(unittest.TestCase):
    def test_result(self):
        res = Result(Input(), 1e10, .01, .01, .01)
        self.assertAlmostEqual(math.log10(res.totalCoolingMass), 8.964883982294, 12)

    def test_habitat(self):
        res = Habitat(Input(), 1e10, .01, .01, .01)
        self.assertAlmostEqual(math.log10(res.totalCoolingMass), 8.964883982294, 12)

