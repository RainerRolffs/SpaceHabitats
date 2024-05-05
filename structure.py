import math

from helpers import ShapeType
from input import Input


class Structure:
    def __init__(self, inp: Input, N: int = 10,
                 rotationalRadius: float = 0, pressuredVolume: float = 0, pressuredMass: float = 0,  # [m], [m³], [kg]
                 groundDistribution: {float: float} = {},  # {radius: mass} [m]: [kg]
                 hullDistribution: {float: float} = {},
                 radiatorMass=0, radiatorRadius=0,
                 lightMass=0, lightRadius=0,
                 electricMass=0, electricRadius=0):
        self.inp = inp
        self.rotationRate = (inp.maxGravity / rotationalRadius) ** .5  # [1/s]
        self.rotationRate_rpm = self.rotationRate * 30 / math.pi  # [rounds per minute]
        self.coRotationalRadius = (inp.stressPerDensity * rotationalRadius / inp.maxGravity) ** .5
        self.pressureReferenceMass = pressuredMass
        self.pressureStructuralMass = 2 * inp.airPressure * 1e5 / inp.stressPerDensity * pressuredVolume

        horizontal = self.inp.horizontalSupport and self.inp.shapeType in [ShapeType.Cylinder, ShapeType.Oblate, ShapeType.Torus]
        self.interiorReferenceMass = sum(groundDistribution.values())
        self.interiorStructuralMass = self.ComputeStructuralMass(groundDistribution, horizontalSupport=horizontal)
        if len(groundDistribution) > 0:
            self.interiorFraction = self.interiorStructuralMass / self.interiorReferenceMass

        self.hullReferenceMass = sum(hullDistribution.values())
        self.hullStructuralMass = self.ComputeStructuralMass(hullDistribution, horizontalSupport=horizontal)
        if len(hullDistribution) > 0:
            self.hullFraction = self.hullStructuralMass / self.hullReferenceMass

        self.radiatorReferenceMass = radiatorMass
        radiatorDistribution = {self.LinearEffectiveRadius(i, N, radiatorRadius): self.radiatorReferenceMass / N for i in range(N)}
        self.radiatorStructuralMass = self.ComputeStructuralMass(radiatorDistribution, horizontalSupport=False)
        if self.radiatorReferenceMass > 0:
            self.radiatorFraction = self.radiatorStructuralMass / self.radiatorReferenceMass

        if lightRadius > self.inp.maxCollectionToCoRotRadius * self.coRotationalRadius:  # reduced co-rotation
            maxRadius = self.inp.maxCollectionToCoRotRadius * self.coRotationalRadius
            self.lightReferenceMass = lightMass * (maxRadius / lightRadius) ** 2
        else:
            maxRadius = lightRadius
            self.lightReferenceMass = lightMass
        lightDistribution = {self.CircularEffectiveRadius(i, N, minRadius=0, maxRadius=maxRadius): self.lightReferenceMass / N for i in range(N)}
        self.lightStructuralMass = self.ComputeStructuralMass(lightDistribution, horizontalSupport=False)
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
            self.electricStructuralMass = self.ComputeStructuralMass(electricDistribution, horizontalSupport=False)
            self.coRotationalElectricFraction = self.electricReferenceMass / self.electricReferenceMass
            self.electricFraction = self.electricStructuralMass / self.electricReferenceMass
        else:
            self.electricStructuralMass = 0
            self.electricFraction = 0

        self.totalReferenceMass = self.pressureReferenceMass + self.interiorReferenceMass + self.hullReferenceMass \
                                    + self.radiatorReferenceMass + self.lightReferenceMass + self.electricReferenceMass
        self.totalStructuralMass = self.pressureStructuralMass + self.interiorStructuralMass + self.hullStructuralMass \
                                   + self.radiatorStructuralMass + self.lightStructuralMass + self.electricStructuralMass
        self.totalFraction = self.totalStructuralMass / self.totalReferenceMass

    @staticmethod
    def CircularEffectiveRadius(i, N, minRadius, maxRadius):
        return (minRadius ** 2 + (i + .5) * (maxRadius ** 2 - minRadius ** 2) / N) ** .5

    @staticmethod
    def LinearEffectiveRadius(i, N, maxRadius):
        return maxRadius / N * (((i+1) ** 3 - i ** 3) / 3) ** .5

    def ComputeStructuralMass(self, massdistribution: {float, float}, horizontalSupport: bool):
        structuralMass = 0
        for radius in massdistribution.keys():
            structuralFraction = self.ComputeStructuralFraction(radius, horizontalSupport)
            structuralMass += structuralFraction * massdistribution[radius]
        return structuralMass

    def ComputeStructuralFraction(self, radius: float, horizontalSupport: bool):
        r = radius / self.coRotationalRadius
        if radius == 0:  # no support needed
            return 0
        elif horizontalSupport and r < .99:  # horizontal support
            return 1 / (r ** -2 - 1 )
        elif r > 30:
            return 1e200  # avoid overflow
        else:  # vertical support
            return r * (math.pi / 2) ** .5 * math.exp(r ** 2 / 2) * math.erf(2 ** -.5 * r)

    def ComputeStructuralFractionWithoutSelfWeight(self, radius: float):
        if radius == 0:  # no support needed
            return 0
        else:
            return (self.rotationRate * radius) ** 2 / self.inp.stressPerDensity
