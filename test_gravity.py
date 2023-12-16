import math
import unittest
from gravity import Gravity
from input import Input
from helpers import ShapeType


class TestGravity(unittest.TestCase):
    def setUp(self):
        self.inp = Input()
        self.inp.maxGravity = 9.81
        self.inp.constantFloorHeight = 5
        self.inp.variableFloorHeight = 2

    def test_cylinder(self):
        self.inp.shapeType = ShapeType.Cylinder
        self.inp.cylinderLengthToRotRadius = 1

        gravity = Gravity(self.inp, 100)
        self.assertAlmostEqual(gravity.rotationRate_rpm, 3, 1)
        self.assertEqual(len(gravity.groundRadii), 11)
        self.assertAlmostEqual(gravity.groundRadii[-1], 14.13, 2)
        self.assertEqual(len(gravity.groundAreas), 11)
        self.assertEqual(len(gravity.hullAreas), 11)
        self.assertAlmostEqual(gravity.averageVolumetricGravity, 6.48, 2)
        self.assertAlmostEqual(gravity.averageGroundGravity, 7.12, 2)
        self.assertAlmostEqual(gravity.averageHullGravity, 7.97, 2)

    def test_tube(self):
        self.inp.shapeType = ShapeType.Tube
        self.inp.tubeRadiusToRotRadius = 0.1

        gravity = Gravity(self.inp, 100)
        self.assertAlmostEqual(gravity.TubeGroundArea(5), 586, 0)
        self.assertAlmostEqual(gravity.TubeGroundArea(10), 987, 0)
        self.assertAlmostEqual(gravity.TubeGroundArea(20), 658, 0)
        self.assertAlmostEqual(gravity.TubeHullLength(5), 64.33, 2)
        self.assertAlmostEqual(gravity.TubeHullLength(10), 165, 0)
        self.assertAlmostEqual(gravity.TubeHullLength(20), 129, 0)
        self.assertAlmostEqual(gravity.averageVolumetricGravity, 4.55, 2)
        self.assertAlmostEqual(gravity.averageGroundGravity, 5.93, 2)
        self.assertAlmostEqual(gravity.averageHullGravity, 5.11, 2)

    def test_oblate(self):
        self.inp.shapeType = ShapeType.Oblate
        self.inp.oblateMinorToRotRadius = .5

        gravity = Gravity(self.inp, 100)
        self.assertAlmostEqual(gravity.GroundArea(5), 3138, 0)
        self.assertAlmostEqual(gravity.GroundArea(50), 27207, 0)
        self.assertAlmostEqual(gravity.HullLength(5), 62.8, 0)
        self.assertAlmostEqual(gravity.HullLength(50), 628, 0)
        self.assertAlmostEqual(gravity.OrientationFactor(90), 1.44, 2)
        self.assertAlmostEqual(gravity.averageVolumetricGravity, 5.73, 2)
        self.assertAlmostEqual(gravity.averageGroundGravity, 6.09, 2)
        self.assertAlmostEqual(gravity.averageHullGravity, 6.95, 2)

    def test_torus(self):
        self.inp.shapeType = ShapeType.Torus
        self.inp.torusHabToRotRadius = 0.25

        gravity = Gravity(self.inp, 100)
        self.assertAlmostEqual(gravity.GroundArea(60), 15080, 0)
        self.assertAlmostEqual(gravity.HullLength(60), 754, 0)
        self.assertAlmostEqual(gravity.OrientationFactor(90), 1.25, 2)
        self.assertAlmostEqual(gravity.averageVolumetricGravity, 7.58, 2)
        self.assertAlmostEqual(gravity.averageGroundGravity, 7.53, 2)
        self.assertAlmostEqual(gravity.averageHullGravity, 7.1, 2)

    def test_dumbbell(self):
        self.inp.shapeType = ShapeType.Dumbbell
        self.inp.dumbbellMinorToRotRadius = 0.1
        self.inp.dumbbellMajorToMinorRadius = 1.3

        gravity = Gravity(self.inp, 100, 80)
        self.assertAlmostEqual(gravity.GroundArea(60), 357, 0)
        self.assertAlmostEqual(gravity.DumbbellHullLength(60, isSmallerSphere=False), 67, 0)
        self.assertAlmostEqual(gravity.DumbbellOrientationFactor(99, isSmallerSphere=True), 2.35, 2)
        self.assertAlmostEqual(gravity.averageVolumetricGravity, 7.3, 2)
        self.assertAlmostEqual(gravity.averageGroundGravity, 7.33, 2)
        self.assertAlmostEqual(gravity.averageHullGravity, 7.48, 2)

    def test_dumbbellTube(self):
        self.inp.shapeType = ShapeType.DumbbellTube
        self.inp.dumbbellMinorToRotRadius = 0.2
        self.inp.dumbbellMajorToMinorRadius = 1.5
        self.inp.tubeRadiusToRotRadius = 0.05

        gravity = Gravity(self.inp, 100, 80)
        self.assertAlmostEqual(gravity.averageVolumetricGravity, 5.61, 2)
        self.assertAlmostEqual(gravity.averageGroundGravity, 5.81, 2)
        self.assertAlmostEqual(gravity.averageHullGravity, 5.31, 2)
