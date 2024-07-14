import math

from helpers import ShapeType
from input import Input


class Structure:
    def __init__(self, inp: Input, N: int = 10,  # number of shells for computation of energy system support
                 rotationalRadius: float = 0, pressuredVolume: float = 0, pressuredMass: float = 0,  # [m], [m³], [kg]
                 groundDistribution: {float: float} = {},  # {radius: mass} [m]: [kg]
                 hullDistribution: {float: float} = {},
                 radiatorMass=0, radiatorRadius=0,
                 lightMass=0, lightRadius=0,
                 electricMass=0, electricRadius=0):
        self.inp = inp
        self.rotationalRadius = rotationalRadius
        self.rotationRate = (inp.maxGravity / rotationalRadius) ** .5  # [1/s]
        self.rotationRate_rpm = self.rotationRate * 30 / math.pi  # [rounds per minute]
        self.coRotationalRadius = (inp.stressPerDensity * rotationalRadius / inp.maxGravity) ** .5
        self.pressureReferenceMass = pressuredMass
        self.pressureStructuralMass = 2 * inp.airPressure * 1e5 / inp.stressPerDensity * pressuredVolume

        closedCircle = self.inp.shapeType in [ShapeType.Cylinder, ShapeType.Oblate, ShapeType.Torus]

        self.interiorReferenceMass = sum(groundDistribution.values())
        self.interiorStructuralMass = self.ComputeStructuralMass(groundDistribution, isHorizontalPossible=closedCircle)
        if len(groundDistribution) > 0:
            self.interiorFraction = self.interiorStructuralMass / self.interiorReferenceMass

        self.hullReferenceMass = sum(hullDistribution.values())
        self.hullStructuralMass = self.ComputeStructuralMass(hullDistribution, isHorizontalPossible=closedCircle)
        if len(hullDistribution) > 0:
            self.hullFraction = self.hullStructuralMass / self.hullReferenceMass

        self.radiatorReferenceMass = radiatorMass
        radiatorDistribution = {self.LinearEffectiveRadius(i, N, radiatorRadius): self.radiatorReferenceMass / N for i in range(N)}
        self.radiatorStructuralMass = self.ComputeStructuralMass(radiatorDistribution, isHorizontalPossible=False, withBridges=False)
        if self.radiatorReferenceMass > 0:
            self.radiatorFraction = self.radiatorStructuralMass / self.radiatorReferenceMass

        if lightRadius > self.inp.maxCollectionToCoRotRadius * self.coRotationalRadius:  # reduced co-rotation
            maxRadius = self.inp.maxCollectionToCoRotRadius * self.coRotationalRadius
            self.lightReferenceMass = lightMass * (maxRadius / lightRadius) ** 2
        else:
            maxRadius = lightRadius
            self.lightReferenceMass = lightMass
        lightDistribution = {self.CircularEffectiveRadius(i, N, minRadius=0, maxRadius=maxRadius): self.lightReferenceMass / N for i in range(N)}
        self.lightStructuralMass = self.ComputeStructuralMass(lightDistribution, isHorizontalPossible=True)
        if self.lightReferenceMass > 0:
            self.coRotationalLightFraction = self.lightReferenceMass / lightMass
            self.lightFraction = self.lightStructuralMass / self.lightReferenceMass

        if electricRadius > self.inp.maxCollectionToCoRotRadius * self.coRotationalRadius:  # reduced co-rotation
            maxRadius = self.inp.maxCollectionToCoRotRadius * self.coRotationalRadius
            self.electricReferenceMass = electricMass * (maxRadius ** 2 - lightRadius ** 2) / (electricRadius ** 2 - lightRadius ** 2)
        else:
            maxRadius = electricRadius
            self.electricReferenceMass = electricMass
        if self.electricReferenceMass > 0:
            electricDistribution = {self.CircularEffectiveRadius(i, N, minRadius=lightRadius, maxRadius=maxRadius): self.electricReferenceMass / N for i in range(N)}
            self.electricStructuralMass = self.ComputeStructuralMass(electricDistribution, isHorizontalPossible=True)
            self.coRotationalElectricFraction = self.electricReferenceMass / self.electricReferenceMass
            self.electricFraction = self.electricStructuralMass / self.electricReferenceMass
        else:
            self.electricStructuralMass = 0
            self.electricFraction = 0

        self.totalReferenceMass = self.pressureReferenceMass + self.interiorReferenceMass + self.hullReferenceMass \
                                    + self.radiatorReferenceMass + self.lightReferenceMass + self.electricReferenceMass
        self.totalStructuralMass = self.pressureStructuralMass + self.interiorStructuralMass + self.hullStructuralMass \
                                   + self.radiatorStructuralMass + self.lightStructuralMass + self.electricStructuralMass
        if self.totalReferenceMass > 0:
            self.totalFraction = self.totalStructuralMass / self.totalReferenceMass

    @staticmethod
    def CircularEffectiveRadius(i, N, minRadius, maxRadius):
        return (minRadius ** 2 + (i + .5) * (maxRadius ** 2 - minRadius ** 2) / N) ** .5

    @staticmethod
    def LinearEffectiveRadius(i, N, maxRadius):
        return maxRadius / N * (((i+1) ** 3 - i ** 3) / 3) ** .5

    def ComputeStructuralMass(self, massdistribution: {float, float}, isHorizontalPossible: bool, withBridges: bool = True):
        structuralMass = 0
        for radius in massdistribution.keys():
            if isHorizontalPossible and radius < self.coRotationalRadius:
                structuralFraction = self.ComputeHorizontalStructuralFraction(radius)
                if radius > 0.1 * self.coRotationalRadius:
                    verticalStructuralFraction = self.ComputeVerticalStructuralFraction(radius, withBridges)
                    structuralFraction = min(structuralFraction, verticalStructuralFraction)
            else:
                structuralFraction = self.ComputeVerticalStructuralFraction(radius, withBridges)

            structuralMass += structuralFraction * massdistribution[radius]
        return structuralMass

    def ComputeHorizontalStructuralFraction(self, radius: float):  # [m]
        r = radius / self.coRotationalRadius
        if r == 0:  # no support needed
            return 0
        elif r < 1:
            return 1 / (r ** -2 - 1)
        else:
            return 1e200

    def ComputeVerticalStructuralFraction(self, radius: float, withBridges: bool = True):
        r = radius / self.coRotationalRadius
        if r == 0:  # no support needed
            return 0
        elif r > 30:
            return 1e200  # avoid overflow
        else:  # vertical support
            verticalMassFraction = r * (math.pi / 2) ** .5 * math.exp(r ** 2 / 2) * math.erf(2 ** -.5 * r)
            if withBridges:
                gravity = r * self.coRotationalRadius / self.rotationalRadius * self.inp.maxGravity
                bridgeMassFraction = gravity / self.inp.stressPerDensity / 6 * self.inp.distanceBetweenVerticalCables * \
                                     (self.inp.distanceBetweenVerticalCables / self.inp.bridgeThickness + 1)
                return bridgeMassFraction + verticalMassFraction * (1 + bridgeMassFraction)
            else:
                return verticalMassFraction

    def ComputeStructuralFractionWithoutSelfWeight(self, radius: float):
        if radius == 0:  # no support needed
            return 0
        else:
            return (self.rotationRate * radius) ** 2 / self.inp.stressPerDensity
