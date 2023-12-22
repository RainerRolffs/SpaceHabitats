import math

from helpers import ShapeType
from input import Input


class Structure:
    def __init__(self, inp: Input, N: int = 10,
                 rotationalRadius: float = 0, habVolume: float = 0,  # [m], [m³]
                 groundDistribution: {float: float} = {},  # {radius: mass} [m]: [kg]
                 hullDistribution: {float: float} = {},
                 radiatorMass=0, radiatorRadius=0,
                 lightMass=0, lightRadius=0,
                 electricMass=0, electricRadius=0):
        self.inp = inp
        self.rotationRate = (inp.maxGravity / rotationalRadius) ** .5  # [1/s]
        self.rotationRate_rpm = self.rotationRate * 30 / math.pi  # [rounds per minute]
        self.coRotationalRadius = (inp.stressPerDensity * rotationalRadius / inp.maxGravity) ** .5
        self.structuralAirMass = 2 * inp.airPressure / inp.stressPerDensity * habVolume

        horizontal = self.inp.horizontalSupport and self.inp.shapeType in [ShapeType.Cylinder, ShapeType.Oblate, ShapeType.Torus]
        self.structuralInteriorMass = self.ComputeStructuralMass(groundDistribution, horizontalSupport=horizontal)
        if len(groundDistribution) > 0:
            self.interiorFraction = self.structuralInteriorMass / sum(groundDistribution)
        self.structuralHullMass = self.ComputeStructuralMass(hullDistribution, horizontalSupport=horizontal)
        if len(hullDistribution) > 0:
            self.hullFraction = self.structuralHullMass / sum(hullDistribution)

        radiatorDistribution = {self.LinearEffectiveRadius(i, N, radiatorRadius): radiatorMass / N for i in range(N)}
        self.structuralRadiatorMass = self.ComputeStructuralMass(radiatorDistribution, horizontalSupport=False)
        if radiatorMass > 0:
            self.radiatorFraction = self.structuralRadiatorMass / radiatorMass

        lightDistribution = {self.CircularEffectiveRadius(i, N, minRadius=0, maxRadius=lightRadius): lightMass / N for i in range(N)}
        self.structuralLightMass = self.ComputeStructuralMass(lightDistribution, horizontalSupport=False)
        if lightMass > 0:
            self.lightFraction = self.structuralLightMass / lightMass

        electricDistribution = {self.CircularEffectiveRadius(i, N, minRadius=lightRadius, maxRadius=electricRadius): electricMass / N for i in range(N)}
        self.structuralElectricMass = self.ComputeStructuralMass(electricDistribution, horizontalSupport=False)
        if electricMass > 0:
            self.electricFraction = self.structuralElectricMass / electricMass

        self.totalStructuralMass = self.structuralAirMass + self.structuralInteriorMass + self.structuralHullMass \
                                   + self.structuralRadiatorMass + self.structuralLightMass + self.structuralElectricMass

    @staticmethod
    def CircularEffectiveRadius(i, N, minRadius, maxRadius):
        return (minRadius ** 2 + (i + .5) * (maxRadius ** 2 - minRadius ** 2) / N) ** .5

    @staticmethod
    def LinearEffectiveRadius(i, N, maxRadius):
        return maxRadius / N * (((i+1) ** 3 - i ** 3) / 3) ** .5  # (i + .5) / N * maxRadius

    def ComputeStructuralMass(self, massdistribution: {float, float}, horizontalSupport: bool):
        structuralMass = 0
        for radius in massdistribution.keys():
            structuralFraction = self.ComputeStructuralFraction(radius, horizontalSupport)
            structuralMass += structuralFraction * massdistribution[radius]
        return structuralMass

    def ComputeStructuralFraction(self, radius: float, horizontalSupport: bool):
        if radius == 0:  # no support needed
            return 0
        elif radius > self.inp.maxCoRotation * self.coRotationalRadius:  # no co-rotation
            return 0
        elif horizontalSupport and radius < self.coRotationalRadius:  # horizontal support
            return 1 / (self.inp.stressPerDensity / (self.rotationRate * radius) ** 2 - 1 )
        else:  # vertical support
            C = self.rotationRate ** 2 / 2 / self.inp.stressPerDensity
            return radius * (math.pi * C) ** .5 * math.exp(C * radius ** 2) * math.erf(C ** .5 * radius)

    def ComputeStructuralFractionWithoutSelfWeight(self, radius: float):
        if radius == 0:  # no support needed
            return 0
        else:
            return (self.rotationRate * radius) ** 2 / self.inp.stressPerDensity
