from input import Input
import math


class Shape:
    def __init__(self, inp: Input, habPower):
        self.habVolume = habPower / inp.powerPerVolume
        self.habRadius = (self.habVolume / inp.aspectRatio / math.pi) ** (1 / 3)
        self.hullSurface = (2 + 2 * inp.aspectRatio) * math.pi * self.habRadius ** 2
        self.hullMass = self.hullSurface * inp.hullSurfaceDensity
        self.hullVolume = self.hullSurface * (inp.hullSurfaceDensity / inp.hullDensity + inp.gapThickness)
        self.interiorMass = habPower * inp.interiorMassPerPower

