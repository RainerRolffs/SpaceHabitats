import unittest
from shape import Shape
from input import Input
from helpers import ShapeType
import math


class TestShape(unittest.TestCase):
    def setUp(self):
        # Common setup logic
        self.common_habPower = 100
        self.inp = Input()
        self.inp.powerPerVolume = 1
        self.inp.aspectRatio = 0.5
        self.inp.hullSurfaceDensity = 0.1
        self.inp.hullDensity = 1
        self.inp.gapThickness = 0.01
        self.inp.interiorMassPerPower = 0.2
        self.inp.airPressure = 1
        self.inp.maxGravity = 9.81

    def test_cylinder_shape(self):
        self.inp.shapeType = ShapeType.Cylinder
        shape = Shape(self.inp, self.common_habPower)
        self.assertAlmostEqual(shape.rotationalRadius, 4, 1)
        self.assertAlmostEqual(shape.hullSurface, 150, 0)
        self.assertAlmostEqual(shape.crossSection, 50, 0)

        self.assertAlmostEqual(shape.rotationRate, 15, 0)
        self.assertAlmostEqual(shape.hullMass, 15, 0)
        self.assertAlmostEqual(shape.hullVolume, 17, 0)
        self.assertAlmostEqual(shape.interiorMass, 20, 0)
        self.assertAlmostEqual(shape.airMass, 120, 0)

    def test_oblate_shape(self):
        self.inp.shapeType = ShapeType.Oblate
        shape = Shape(self.inp, self.common_habPower)
        self.assertAlmostEqual(shape.rotationalRadius, 3.6, 1)
        self.assertAlmostEqual(shape.hullSurface, 108, 0)
        self.assertAlmostEqual(shape.crossSection, 41, 0)

    def test_prolate_shape(self):
        self.inp.shapeType = ShapeType.Prolate
        shape = Shape(self.inp, self.common_habPower)
        self.assertAlmostEqual(shape.rotationalRadius, 4.6, 1)
        self.assertAlmostEqual(shape.hullSurface, 106, 0)
        self.assertAlmostEqual(shape.crossSection, 33, 0)

    def test_torus_shape(self):
        self.inp.shapeType = ShapeType.Torus
        self.inp.aspectRatio = 0.25
        shape = Shape(self.inp, self.common_habPower)
        self.assertAlmostEqual(shape.rotationalRadius, 4.8, 1)
        self.assertAlmostEqual(shape.hullSurface, 168, 0)
        self.assertAlmostEqual(shape.crossSection, 53, 0)

    def test_asymmetric_dumbbell_shape(self):
        self.inp.shapeType = ShapeType.Dumbbell
        self.inp.aspectRatio = 0.25
        self.inp.dumbbellTubeFraction = 0.1
        self.inp.dumbbellRadiiRatio = 2
        shape = Shape(self.inp, self.common_habPower)
        self.assertAlmostEqual(shape.rotationalRadius, 5.3, 1)
        self.assertAlmostEqual(shape.tubeLength, .5, 1)
        self.assertAlmostEqual(shape.tubeRadius, 2.5, 1)
        self.assertAlmostEqual(shape.hullSurface, 112, 0)
        self.assertAlmostEqual(shape.crossSection, 28, 0)

    def test_symmetric_dumbbell_shape(self):
        self.inp.shapeType = ShapeType.Dumbbell
        self.inp.aspectRatio = 0.25
        self.inp.dumbbellTubeFraction = 0.1
        self.inp.dumbbellRadiiRatio = 1
        shape = Shape(self.inp, self.common_habPower)
        self.assertAlmostEqual(shape.rotationalRadius, 8.8, 1)
        self.assertAlmostEqual(shape.tubeLength, 8.8, 1)
        self.assertAlmostEqual(shape.tubeRadius, .6, 1)
        self.assertAlmostEqual(shape.hullSurface, 122, 0)
        self.assertAlmostEqual(shape.crossSection, 31, 0)

    def test_exception_handling(self):
        with self.assertRaises(ValueError):
            self.inp.shapeType = 'unknown'
            habPower = 100
            Shape(self.inp, habPower)


if __name__ == '__main__':
    unittest.main()
