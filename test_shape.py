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
        self.inp.hullSurfaceDensity = 0.1
        self.inp.hullDensity = 1
        self.inp.gapThickness = 0.01
        self.inp.interiorMassPerPower = 0.2
        self.inp.airPressure = 1

    def test_cylinder_shape(self):
        self.inp.shapeType = ShapeType.Cylinder
        self.inp.cylinderLengthToRotRadius = 0.5
        shape = Shape(self.inp, self.common_habPower)
        self.assertAlmostEqual(shape.rotationalRadius, 4, 1)
        self.assertAlmostEqual(shape.hullSurface, 150, 0)
        self.assertAlmostEqual(shape.crossSection, 50, 0)

        self.assertAlmostEqual(shape.hullMass, 15, 0)
        self.assertAlmostEqual(shape.hullVolume, 17, 0)
        self.assertAlmostEqual(shape.interiorMass, 20, 0)
        self.assertAlmostEqual(shape.airMass, 120, 0)

    def test_tube_shape(self):
        self.inp.shapeType = ShapeType.Tube
        self.inp.tubeRadiusToRotRadius = 0.2
        shape = Shape(self.inp, self.common_habPower)
        self.assertAlmostEqual(shape.rotationalRadius, 7.4, 1)
        self.assertAlmostEqual(shape.hullSurface, 150, 0)
        self.assertAlmostEqual(shape.crossSection, 43, 0)

    def test_oblate_shape(self):
        self.inp.shapeType = ShapeType.Oblate
        self.inp.oblateMinorToRotRadius = 0.5
        shape = Shape(self.inp, self.common_habPower)
        self.assertAlmostEqual(shape.rotationalRadius, 3.6, 1)
        self.assertAlmostEqual(shape.hullSurface, 108, 0)
        self.assertAlmostEqual(shape.crossSection, 41, 0)

    def test_torus_shape(self):
        self.inp.shapeType = ShapeType.Torus
        self.inp.torusHabToRotRadius = 0.25
        shape = Shape(self.inp, self.common_habPower)
        self.assertAlmostEqual(shape.rotationalRadius, 4.8, 1)
        self.assertAlmostEqual(shape.hullSurface, 168, 0)
        self.assertAlmostEqual(shape.crossSection, 53, 0)

    def test_symmetric_dumbbell_shape(self):
        self.inp.shapeType = ShapeType.Dumbbell
        self.inp.dumbbellMinorToRotRadius = 0.25
        self.inp.dumbbellMajorToMinorRadius = 1
        shape = Shape(self.inp, self.common_habPower)
        self.assertAlmostEqual(shape.rotationalRadius, 9.1, 1)
        self.assertAlmostEqual(shape.hullSurface, 131, 0)
        self.assertAlmostEqual(shape.crossSection, 32.8, 1)

    def test_asymmetric_dumbbell_shape(self):
        self.inp.shapeType = ShapeType.Dumbbell
        self.inp.dumbbellMinorToRotRadius = 0.25
        self.inp.dumbbellMajorToMinorRadius = 2
        shape = Shape(self.inp, self.common_habPower)
        self.assertAlmostEqual(shape.rotationalRadius, 5.5, 1)
        self.assertAlmostEqual(shape.hullSurface, 120, 0)
        self.assertAlmostEqual(shape.crossSection, 30, 0)

    def test_dumbbell_tube_shape(self):
        self.inp.shapeType = ShapeType.DumbbellTube
        self.inp.dumbbellMinorToRotRadius = 0.25
        self.inp.dumbbellMajorToMinorRadius = 1.2
        self.inp.tubeRadiusToRotRadius = 0.1
        shape = Shape(self.inp, self.common_habPower)
        self.assertAlmostEqual(shape.rotationalRadius, 7.9, 1)
        self.assertAlmostEqual(shape.tubeLengthToRotRadius, 2/3, 1)
        self.assertAlmostEqual(shape.hullSurface, 143, 0)
        self.assertAlmostEqual(shape.crossSection, 38.6, 1)

    def test_exception_handling(self):
        with self.assertRaises(ValueError):
            self.inp.shapeType = 'unknown'
            habPower = 100
            Shape(self.inp, habPower)


if __name__ == '__main__':
    unittest.main()
