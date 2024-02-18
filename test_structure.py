import unittest
from structure import Structure
from input import Input


class TestStructure(unittest.TestCase):
    def setUp(self):
        self.inp = Input()
        self.inp.maxGravity = 9.81
        self.inp.horizontalSupport = False

    def test_radiator(self):
        structure = Structure(self.inp, rotationalRadius=10, radiatorMass=1, radiatorRadius=100)
        self.assertAlmostEqual(structure.radiatorStructuralMass, .033, 3)

        structure = Structure(self.inp, N=1, rotationalRadius=10, radiatorMass=1, radiatorRadius=100)
        self.assertAlmostEqual(structure.radiatorStructuralMass, .033, 3)

        self.assertAlmostEqual(structure.ComputeStructuralFractionWithoutSelfWeight(100), .098, 3)
        self.assertAlmostEqual(structure.ComputeStructuralFraction(100, horizontalSupport=False), .101, 3)
        self.assertAlmostEqual(structure.ComputeStructuralFraction(100, horizontalSupport=True), .109, 3)

    def test_energyCollection(self):
        structure = Structure(self.inp, N=100, rotationalRadius=10, lightMass=1, lightRadius=100, electricMass=1, electricRadius=200)
        self.assertAlmostEqual(structure.lightStructuralMass, .05, 3)
        self.assertAlmostEqual(structure.electricStructuralMass, .269, 3)

        structure = Structure(self.inp, N=1, rotationalRadius=10, lightMass=1, lightRadius=100, electricMass=1, electricRadius=200)
        self.assertAlmostEqual(structure.lightStructuralMass, .05, 3)
        self.assertAlmostEqual(structure.electricStructuralMass, .266, 3)

        self.inp.maxCollectionToCoRotRadius = 1
        structure = Structure(self.inp, N=100, rotationalRadius=10, lightMass=1, lightRadius=100, electricMass=1, electricRadius=400)
        self.assertAlmostEqual(structure.electricStructuralMass, 0.42, 2)

    def test_given_distribution(self):
        distr = {i: i for i in range(100)}
        structure = Structure(self.inp, rotationalRadius=10, groundDistribution=distr)
        self.assertAlmostEqual(structure.interiorStructuralMass / sum(distr.values()), 0.05, 3)

        distr = {i: i**2 for i in range(100)}
        structure = Structure(self.inp, rotationalRadius=10, hullDistribution=distr)
        self.assertAlmostEqual(structure.hullStructuralMass / sum(distr.values()), 0.06, 3)

    def test_vertical_fraction(self):
        structure = Structure(self.inp, rotationalRadius=10)
        frac = structure.ComputeStructuralFraction(structure.coRotationalRadius, horizontalSupport=False)
        self.assertAlmostEqual(frac, 1.411, 3)

        frac = structure.ComputeStructuralFraction(40*structure.coRotationalRadius, horizontalSupport=False)
        self.assertAlmostEqual(frac, 1e200, 3)  # no overflow error

    def test_horizontal_fraction(self):
        structure = Structure(self.inp, rotationalRadius=10)
        frac = structure.ComputeStructuralFraction(structure.coRotationalRadius / 2, horizontalSupport=True)
        self.assertAlmostEqual(frac, 1/3, 3)

        frac = structure.ComputeStructuralFraction(0.9 * structure.coRotationalRadius, horizontalSupport=True)
        self.assertAlmostEqual(frac, 4.26, 2)

    def test_noselfweight_fraction(self):
        structure = Structure(self.inp, rotationalRadius=10)
        frac = structure.ComputeStructuralFractionWithoutSelfWeight(structure.coRotationalRadius)
        self.assertAlmostEqual(frac, 1, 3)
