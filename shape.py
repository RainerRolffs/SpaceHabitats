from helpers import ShapeType
from input import Input
import math


class Shape:
    def __init__(self, inp: Input, habPower):
        self.habVolume = habPower / inp.powerPerVolume
        if inp.shapeType == ShapeType.Cylinder:
            self.rotationalRadius = (self.habVolume / inp.aspectRatio / math.pi) ** (1 / 3)
            self.hullSurface = (2 + 2 * inp.aspectRatio) * math.pi * self.rotationalRadius ** 2
            self.crossSection = math.pi * self.rotationalRadius ** 2
        elif inp.shapeType == ShapeType.Oblate:
            self.rotationalRadius = (self.habVolume / inp.aspectRatio * 3 / 4 / math.pi) ** (1 / 3)
            aspectFactor = (1 - inp.aspectRatio) ** .5
            self.hullSurface = math.pi * self.rotationalRadius ** 2 * (2 + inp.aspectRatio ** 2 / aspectFactor * math.log((1 + aspectFactor) / (1 - aspectFactor)))
            self.crossSection = math.pi * self.rotationalRadius ** 2
        elif inp.shapeType == ShapeType.Prolate:
            self.rotationalRadius = (self.habVolume / inp.aspectRatio ** 2 * 3 / 4 / math.pi) ** (1 / 3)
            aspectFactor = (1 - inp.aspectRatio) ** .5
            self.hullSurface = 2 * math.pi * self.rotationalRadius ** 2 * inp.aspectRatio * (inp.aspectRatio + math.asin(aspectFactor) / aspectFactor)
            self.crossSection = math.pi * self.rotationalRadius ** 2 * inp.aspectRatio
        elif inp.shapeType == ShapeType.Torus:
            self.rotationalRadius = (self.habVolume / inp.aspectRatio ** 2 / (1 - inp.aspectRatio) / 2 / math.pi ** 2) ** (1 / 3)
            self.hullSurface = 4 * math.pi ** 2 * self.rotationalRadius ** 2 * (inp.aspectRatio - inp.aspectRatio ** 2)
            self.crossSection = math.pi * self.rotationalRadius ** 2 * (1 - (1 - 2 * inp.aspectRatio) ** 2)
        elif inp.shapeType == ShapeType.Dumbbell:
            self.rotationalRadius = 1 / inp.aspectRatio * (self.habVolume * (1 - inp.dumbbellTubeFraction) * 3 / 4
                                                    / math.pi / (1 + inp.dumbbellRadiiRatio ** 3)) ** (1 / 3)
            self.tubeLength = self.rotationalRadius * (1 + inp.dumbbellRadiiRatio ** -3 - inp.aspectRatio * (2 + inp.dumbbellRadiiRatio + inp.dumbbellRadiiRatio ** -3))
            self.tubeRadius = (inp.dumbbellTubeFraction * self.habVolume / math.pi / self.tubeLength) ** .5
            self.hullSurface = 4 * math.pi * self.rotationalRadius ** 2 * inp.aspectRatio ** 2 * (1 + inp.dumbbellRadiiRatio ** 2)
            self.crossSection = self.hullSurface / 4
        else:
            raise ValueError()
        self.rotationRate = (inp.maxGravity / self.rotationalRadius) ** .5 * 30 / math.pi
        self.hullMass = self.hullSurface * inp.hullSurfaceDensity
        self.hullVolume = self.hullSurface * (inp.hullSurfaceDensity / inp.hullDensity + inp.gapThickness)
        self.interiorMass = habPower * inp.interiorMassPerPower
        self.airMass = self.habVolume * inp.airPressure * 1.2

