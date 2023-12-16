import math
import unittest

from habitat import Habitat
from helpers import ShapeType
from input import Input


class TestHabitat(unittest.TestCase):

    def setUp(self):
        self.inp = Input()
        self.inp.constantFloorHeight = 1
        self.inp.variableFloorHeight = 0

    def test_habitat(self):
        res = Habitat(self.inp, 1e10, .01, .01, .01)
        self.assertAlmostEqual(math.log10(res.totalCoolingMass), 8.964883982294, 12)

    def test_shape_gravity(self):
        self.are_shape_gravity_consistent(ShapeType.Cylinder)
        self.are_shape_gravity_consistent(ShapeType.Tube)
        self.are_shape_gravity_consistent(ShapeType.Oblate)
        self.are_shape_gravity_consistent(ShapeType.Torus)
        self.are_shape_gravity_consistent(ShapeType.Dumbbell)
        self.are_shape_gravity_consistent(ShapeType.DumbbellTube)

    def test_asym(self):
        self.inp.dumbbellMajorToMinorRadius = 3
        self.are_shape_gravity_consistent(ShapeType.Dumbbell)
        self.are_shape_gravity_consistent(ShapeType.DumbbellTube)

    def are_shape_gravity_consistent(self, shape_type: ShapeType):
        self.inp.shapeType = shape_type
        hab = Habitat(self.inp, 1e10, .01, .01, .01)
        volumeGravToShapeRatio = sum(hab.gravity.floorVolumes) / hab.shape.habVolume
        hullGravToShapeRatio = sum(hab.gravity.hullAreas) / hab.shape.hullSurface
        self.assertLess(abs(1 - volumeGravToShapeRatio), 0.1)
        self.assertLess(abs(1 - hullGravToShapeRatio), 0.1)

