from helpers import ShapeType
from input import Input
import math


class Shape:
    def __init__(self, inp: Input, habPower):
        self.habVolume = habPower / inp.powerPerVolume

        if inp.shapeType == ShapeType.Cylinder:
            self.rotationalRadius = (self.habVolume / inp.cylinderLengthToRotRadius / math.pi) ** (1 / 3)
            self.hullSurface = 2 * math.pi * self.rotationalRadius ** 2 * (1 + inp.cylinderLengthToRotRadius)
            self.crossSection = math.pi * self.rotationalRadius ** 2

        elif inp.shapeType == ShapeType.Tube:
            self.rotationalRadius = (self.habVolume / 2 / math.pi / inp.tubeRadiusToRotRadius ** 2) ** (1 / 3)
            self.hullSurface = 2 * math.pi * self.rotationalRadius ** 2 * (inp.tubeRadiusToRotRadius ** 2 + 2 * inp.tubeRadiusToRotRadius)
            self.crossSection = 4 * inp.tubeRadiusToRotRadius * self.rotationalRadius ** 2

        elif inp.shapeType == ShapeType.Oblate:
            self.rotationalRadius = (self.habVolume / inp.oblateMinorToRotRadius * 3 / 4 / math.pi) ** (1 / 3)
            aspectFactor = (1 - inp.oblateMinorToRotRadius) ** .5
            self.hullSurface = math.pi * self.rotationalRadius ** 2 * (2 + inp.oblateMinorToRotRadius ** 2 / aspectFactor * math.log((1 + aspectFactor) / (1 - aspectFactor)))
            self.crossSection = math.pi * self.rotationalRadius ** 2

        elif inp.shapeType == ShapeType.Torus:
            self.rotationalRadius = (self.habVolume / inp.torusHabToRotRadius ** 2 / (1 - inp.torusHabToRotRadius) / 2 / math.pi ** 2) ** (1 / 3)
            self.hullSurface = 4 * math.pi ** 2 * self.rotationalRadius ** 2 * inp.torusHabToRotRadius * (1 - inp.torusHabToRotRadius ** 2)
            self.crossSection = math.pi * self.rotationalRadius ** 2 * (1 - (1 - 2 * inp.torusHabToRotRadius) ** 2)

        elif (inp.shapeType == ShapeType.Dumbbell) or (inp.shapeType == ShapeType.DumbbellTube):
            self.rotationalRadius = 1 / inp.dumbbellMinorToRotRadius * (self.habVolume * 3 / 4
                                                    / math.pi / (1 + inp.dumbbellMajorToMinorRadius ** 3)) ** (1 / 3)
            self.massRatio = (inp.hullSurfaceDensity + inp.interiorMassPerPower * inp.powerPerVolume / 3 * inp.dumbbellMinorToRotRadius * self.rotationalRadius) \
                / (inp.hullSurfaceDensity * inp.dumbbellMajorToMinorRadius ** 2 + inp.interiorMassPerPower * inp.powerPerVolume / 3
                * inp.dumbbellMajorToMinorRadius ** 3 * inp.dumbbellMinorToRotRadius * self.rotationalRadius)

            if inp.shapeType == ShapeType.Dumbbell:
                self.otherRotationalRadius = (inp.dumbbellMajorToMinorRadius * inp.dumbbellMinorToRotRadius + self.massRatio * (
                        1 - inp.dumbbellMinorToRotRadius)) * self.rotationalRadius
                self.hullSurface = 4 * math.pi * self.rotationalRadius ** 2 * inp.dumbbellMinorToRotRadius ** 2 * (1 + inp.dumbbellMajorToMinorRadius ** 2)
                self.crossSection = self.hullSurface / 4

            elif inp.shapeType == ShapeType.DumbbellTube:
                self.tubeLengthToRotRadius = 1 + self.massRatio - inp.dumbbellMinorToRotRadius * (2 + inp.dumbbellMajorToMinorRadius + self.massRatio)
                denominator = 4 * math.pi / 3 * (1 + inp.dumbbellMajorToMinorRadius ** 3) * inp.dumbbellMinorToRotRadius ** 3 \
                    + math.pi * inp.tubeRadiusToRotRadius ** 2 * self.tubeLengthToRotRadius
                self.rotationalRadius = (self.habVolume / denominator) ** (1 / 3)
                self.otherRotationalRadius = (inp.dumbbellMajorToMinorRadius * inp.dumbbellMinorToRotRadius + self.massRatio * (
                            1 - inp.dumbbellMinorToRotRadius)) * self.rotationalRadius
                self.hullSurface = 2 * math.pi * self.rotationalRadius ** 2 * ( 2 * inp.dumbbellMinorToRotRadius ** 2 * (1 + inp.dumbbellMajorToMinorRadius ** 2)
                                + inp.tubeRadiusToRotRadius * self.tubeLengthToRotRadius - inp.tubeRadiusToRotRadius ** 2)
                self.crossSection = self.rotationalRadius ** 2 * (math.pi * inp.dumbbellMinorToRotRadius ** 2 * (1 + inp.dumbbellMajorToMinorRadius ** 2)
                    + 2 * inp.tubeRadiusToRotRadius * self.tubeLengthToRotRadius)
        else:
            raise ValueError()

        self.hullMass = self.hullSurface * inp.hullSurfaceDensity
        self.hullVolume = self.hullSurface * (inp.hullSurfaceDensity / inp.hullDensity + inp.gapThickness)
        self.interiorMass = habPower * inp.interiorMassPerPower
        self.airMass = self.habVolume * inp.airPressure * 1.2
