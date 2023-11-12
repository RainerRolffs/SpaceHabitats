from helpers import ShapeType
from input import Input
import math


class Gravity:
    def __init__(self, inp: Input, rotationalRadius, otherRotationalRadius: float):
        self.inp = inp
        self.rotationalRadius = rotationalRadius
        self.otherRotationalRadius = otherRotationalRadius

        self.rotationRate_rpm = (inp.maxGravity / rotationalRadius) ** .5 * 30 / math.pi

        self.volumetricDistribution = []
        volumetricReference = 0
        self.groundDistribution = []
        groundReference = 0
        self.hullDistribution = []
        hullReference = 0
        self.groundRadii = []

        lowerRadius = rotationalRadius
        while lowerRadius > 0:
            height = self.NextFloorHeight(lowerRadius)
            upperRadius = lowerRadius - height
            if upperRadius < 0:
                upperRadius = 0
            floorRadius = (lowerRadius + upperRadius) / 2

            groundArea = self.GroundArea(lowerRadius)
            self.groundDistribution.append(groundArea * lowerRadius * inp.maxGravity / rotationalRadius)
            groundReference += groundArea

            volume = height * self.GroundArea(floorRadius)
            self.volumetricDistribution.append(volume * floorRadius * inp.maxGravity / rotationalRadius)
            volumetricReference += volume

            if lowerRadius == rotationalRadius:
                hullArea = self.ExtraHullArea(lowerRadius)
                self.hullDistribution.append(hullArea * lowerRadius * inp.maxGravity / rotationalRadius)
                hullReference += hullArea
            hullArea = height * self.HullLength(floorRadius) * self.OrientationFactor(floorRadius)
            self.hullDistribution.append(hullArea * floorRadius * inp.maxGravity / rotationalRadius)
            hullReference += hullArea

            self.groundRadii.append(lowerRadius)
            lowerRadius = upperRadius

        self.averageVolumetricGravity = sum(self.volumetricDistribution) / volumetricReference
        self.averageGroundGravity = sum(self.groundDistribution) / groundReference
        self.averageHullGravity = sum(self.hullDistribution) / hullReference

    def NextFloorHeight(self, radius):
        return self.inp.constantFloorHeight + self.inp.variableFloorHeight * self.rotationalRadius / radius

    def GroundArea(self, radius):
        if self.inp.shapeType == ShapeType.Cylinder:
            return 2 * math.pi * radius * self.inp.cylinderLengthToRotRadius * self.rotationalRadius

    def ExtraHullArea(self, radius):
        if (self.inp.shapeType == ShapeType.Cylinder) and (radius == self.rotationalRadius):
            return self.GroundArea(radius)

    def HullLength(self, radius):
        if self.inp.shapeType == ShapeType.Cylinder:
            return 4 * math.pi * radius

    def OrientationFactor(self, radius):
        if self.inp.shapeType == ShapeType.Cylinder:
            return 1
