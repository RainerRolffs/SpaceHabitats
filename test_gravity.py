import unittest
from gravity import Gravity
from input import Input
from helpers import ShapeType
import math


class TestGravity(unittest.TestCase):
    def setUp(self):
        # Common setup logic
        self.common_habPower = 100
        self.inp = Input()
        self.inp.maxGravity = 9.81
        self.inp.constantFloorHeight = 5
        self.inp.variableFloorHeight = 2

    def test_cylinder(self):
        self.inp.shapeType = ShapeType.Cylinder
        self.inp.cylinderLengthToRotRadius = 1

        gravity = Gravity(self.inp, 100, 80)
        self.assertAlmostEqual(gravity.rotationRate_rpm, 3, 1)
        self.assertAlmostEqual(gravity.averageVolumetricGravity, 6.48, 2)
        self.assertAlmostEqual(gravity.averageGroundGravity, 7.12, 2)
        self.assertEqual(len(gravity.groundRadii), 11)
        self.assertEqual(len(gravity.groundDistribution), 11)
        self.assertEqual(len(gravity.hullDistribution), 12)
