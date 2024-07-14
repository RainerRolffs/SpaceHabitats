import unittest
from structure import Structure
from input import Input


class TestStructure(unittest.TestCase):
    def setUp(self):
        self.inp = Input()
        self.inp.maxGravity = 9.81
        self.inp.distanceBetweenVerticalCables = 0

    def test_radiator(self):
        structure = Structure(self.inp, rotationalRadius=10, radiatorMass=1, radiatorRadius=100)
        self.assertAlmostEqual(structure.radiatorStructuralMass, .033, 3)

        structure = Structure(self.inp, N=1, rotationalRadius=10, radiatorMass=1, radiatorRadius=100)
        self.assertAlmostEqual(structure.radiatorStructuralMass, .033, 3)

        self.assertAlmostEqual(structure.ComputeStructuralFractionWithoutSelfWeight(100), .098, 3)
        self.assertAlmostEqual(structure.ComputeVerticalStructuralFraction(100), .101, 3)
        self.assertAlmostEqual(structure.ComputeHorizontalStructuralFraction(100), .109, 3)

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
        frac = structure.ComputeVerticalStructuralFraction(structure.coRotationalRadius)
        self.assertAlmostEqual(frac, 1.411, 3)

        frac = structure.ComputeVerticalStructuralFraction(40*structure.coRotationalRadius)
        self.assertAlmostEqual(frac, 1e200, 3)  # no overflow error

    def test_bridge(self):
        structure = Structure(self.inp, rotationalRadius=10)
        self.inp.distanceBetweenVerticalCables = 10
        self.inp.bridgeThickness = 1
        frac = structure.ComputeVerticalStructuralFraction(structure.coRotationalRadius)
        self.assertAlmostEqual(frac, 1.549, 3)

        frac = structure.ComputeVerticalStructuralFraction(0.1 * structure.coRotationalRadius)
        self.assertAlmostEqual(frac, 0.016, 3)

        self.inp.bridgeThickness = 5
        frac = structure.ComputeVerticalStructuralFraction(0.1 * structure.coRotationalRadius)
        self.assertAlmostEqual(frac, 0.0116, 3)

        frac = structure.ComputeVerticalStructuralFraction(structure.coRotationalRadius)
        self.assertAlmostEqual(frac, 1.448, 3)

    def test_horizontal_fraction(self):
        structure = Structure(self.inp, rotationalRadius=10)
        frac = structure.ComputeHorizontalStructuralFraction(structure.coRotationalRadius / 2)
        self.assertAlmostEqual(frac, 1/3, 3)

        frac = structure.ComputeHorizontalStructuralFraction(0.9 * structure.coRotationalRadius)
        self.assertAlmostEqual(frac, 4.26, 2)

        frac = structure.ComputeHorizontalStructuralFraction(0.1 * structure.coRotationalRadius)
        self.assertAlmostEqual(frac, 0.0101, 4)

    def test_noselfweight_fraction(self):
        structure = Structure(self.inp, rotationalRadius=10)
        frac = structure.ComputeStructuralFractionWithoutSelfWeight(structure.coRotationalRadius)
        self.assertAlmostEqual(frac, 1, 3)

        frac = structure.ComputeStructuralFractionWithoutSelfWeight(0.1 * structure.coRotationalRadius)
        self.assertAlmostEqual(frac, 0.01, 3)

    def test_chooose_method(self):
        self.inp.distanceBetweenVerticalCables = 10
        self.inp.bridgeThickness = 1

        structure = Structure(self.inp, rotationalRadius=10)
        distr = {i * structure.coRotationalRadius: 1 for i in [0, 0.1, 0.5, 0.9, 1, 2]}
        frac = structure.ComputeStructuralMass(distr, isHorizontalPossible=True) / sum(distr.values())
        self.assertAlmostEqual(frac, 3.811, 3)




