from helpers import ShapeType
from input import Input
import math


class Gravity:
    def __init__(self, inp: Input, rotationalRadius: float, oppositeRotationalRadius: float = 0):
        self.inp = inp
        self.rotationalRadius = rotationalRadius
        self.oppositeRotationalRadius = oppositeRotationalRadius

        self.floorVolumes = []
        self.groundAreas = []
        self.hullAreas = []
        self.groundRadii = []
        self.floorRadii = []

        self.numberFloors = 0
        lowerRadius = rotationalRadius
        while lowerRadius > 0:
            height = self.NextFloorHeight(lowerRadius)
            upperRadius = lowerRadius - height
            if upperRadius < 0:
                upperRadius = 0
            floorRadius = (lowerRadius + upperRadius) / 2

            self.groundRadii.append(lowerRadius)
            self.floorRadii.append(floorRadius)

            groundArea = self.GroundArea(lowerRadius)
            self.groundAreas.append(groundArea)

            volume = height * self.GroundArea(floorRadius)
            self.floorVolumes.append(volume)
            if volume > 0 or groundArea > 0:
                self.numberFloors += 1

            hullArea = height * self.HullOrientedLength(floorRadius)
            self.hullAreas.append(hullArea)

            lowerRadius = upperRadius

        self.floorVolumesTimesGrav = [self.floorVolumes[i] * self.floorRadii[i] / rotationalRadius * inp.maxGravity for i in range(len(self.floorVolumes))]
        if sum(self.floorVolumes) > 0:
            self.averageVolumetricGravity = sum(self.floorVolumesTimesGrav) / sum(self.floorVolumes)
        else:
            self.averageVolumetricGravity = self.floorRadii[0] / rotationalRadius * inp.maxGravity

        self.groundAreasTimesGrav = [self.groundAreas[i] * self.groundRadii[i] / rotationalRadius * inp.maxGravity for i in range(len(self.groundAreas))]
        if sum(self.groundAreas) > 0:
            self.averageGroundGravity = sum(self.groundAreasTimesGrav) / sum(self.groundAreas)
        else:
            self.averageGroundGravity = self.groundRadii[0] / rotationalRadius * inp.maxGravity

        self.extraHullArea = self.GroundArea(rotationalRadius)
        self.hullAreasTimesGrav = [self.hullAreas[i] * self.floorRadii[i] / rotationalRadius * inp.maxGravity for i in range(len(self.hullAreas))]
        self.hullAreasTimesGrav[0] += self.extraHullArea * inp.maxGravity
        if sum(self.hullAreas) + self.extraHullArea > 0:
            self.averageHullGravity = sum(self.hullAreasTimesGrav) / (sum(self.hullAreas) + self.extraHullArea)
        else:
            self.averageHullGravity = self.hullAreas[0] / rotationalRadius * inp.maxGravity

    def NextFloorHeight(self, radius):
        return self.inp.constantFloorHeight + self.inp.variableFloorHeight * self.rotationalRadius / radius

    def GroundArea(self, radius):
        if self.inp.shapeType == ShapeType.Cylinder:
            return 2 * math.pi * radius * self.inp.cylinderLengthToRotRadius * self.rotationalRadius

        elif self.inp.shapeType == ShapeType.Tube:
            return self.TubeGroundArea(radius)

        elif self.inp.shapeType == ShapeType.Oblate:
            return 4 * math.pi * radius * self.inp.oblateMinorToRotRadius * math.sqrt(self.rotationalRadius**2 - radius**2)

        elif self.inp.shapeType == ShapeType.Torus:
            RH = self.inp.torusHabToRotRadius * self.rotationalRadius
            if radius > self.rotationalRadius - 2 * RH:
                return 4 * math.pi * radius * math.sqrt(RH**2 - (radius - self.rotationalRadius + RH)**2)
            else:
                return 0

        elif self.inp.shapeType in [ShapeType.Dumbbell, ShapeType.DumbbellTube]:
            result = self.DumbbellGroundArea(radius, isSmallerSphere=True) + self.DumbbellGroundArea(radius, isSmallerSphere=False)
            if self.inp.shapeType == ShapeType.DumbbellTube:
                result += self.TubeGroundArea(radius)
            return result

    def DumbbellGroundArea(self, radius: float, isSmallerSphere: bool):
        a_parallel, a_perp, a_parMin = self.DumbbellGroundHalfAxes(radius, isSmallerSphere)
        return (math.pi * (a_parallel - a_parMin) + 4 * a_parMin) * a_perp

    def HullOrientedLength(self, radius):
        if self.inp.shapeType in [ShapeType.Dumbbell, ShapeType.DumbbellTube]:
            result = self.DumbbellHullLength(radius, isSmallerSphere=True) * self.DumbbellOrientationFactor(radius, isSmallerSphere=True) \
                + self.DumbbellHullLength(radius, isSmallerSphere=False) * self.DumbbellOrientationFactor(radius, isSmallerSphere=False)
            if self.inp.shapeType == ShapeType.DumbbellTube:
                result += self.TubeHullLength(radius) * 1
            return result
        else:
            return self.HullLength(radius) * self.OrientationFactor(radius)

    def HullLength(self, radius):
        if self.inp.shapeType == ShapeType.Cylinder:
            return 4 * math.pi * radius

        elif self.inp.shapeType == ShapeType.Tube:
            return self.TubeHullLength(radius)

        elif self.inp.shapeType == ShapeType.Oblate:
            return 4 * math.pi * radius  # Same as sphere

        elif self.inp.shapeType == ShapeType.Torus:
            RH = self.inp.torusHabToRotRadius * self.rotationalRadius
            if radius > self.rotationalRadius - 2 * RH:
                return 4 * math.pi * radius
            else:
                return 0

    def DumbbellHullLength(self, radius: float, isSmallerSphere: bool):
        a_parallel, a_perp, a_parMin = self.DumbbellGroundHalfAxes(radius, isSmallerSphere)
        if a_parMin == 0:
            return 2 * math.pi * math.sqrt((a_parallel ** 2 + a_perp ** 2) / 2)
        else:
            return 4 * a_perp * ((a_parallel - a_parMin) ** 2 + (2 * radius) ** 2) ** .5 / (2 * radius)
                    #2 * math.pi * math.sqrt(((a_parallel - a_parMin) ** 2 + a_perp ** 2) / 2)# 4 * a_perp * ((a_parallel - a_parMin) ** 2 + (2 * radius) ** 2) ** .5 / (2 * radius)

    def OrientationFactor(self, radius):
        if self.inp.shapeType == ShapeType.Cylinder:
            return 1

        elif self.inp.shapeType == ShapeType.Tube:
            return 1

        elif self.inp.shapeType == ShapeType.Oblate:
            return math.sqrt(1 + radius ** 2 * self.inp.oblateMinorToRotRadius ** 2 / (self.rotationalRadius ** 2 - radius ** 2))

        elif self.inp.shapeType == ShapeType.Torus:
            RH = self.inp.torusHabToRotRadius * self.rotationalRadius
            if self.rotationalRadius - 2 * RH < radius < self.rotationalRadius:
                return RH / math.sqrt(RH ** 2 - (radius - self.rotationalRadius + RH) ** 2)
            else:
                return 0

    def DumbbellOrientationFactor(self, radius: float, isSmallerSphere: bool):
        RH, RR = self.DumbbellRadii(isSmallerSphere)
        if radius < RR - 2 * RH or radius > RR:
            return 0
        a_parallel, a_perp, a_parMin = self.DumbbellGroundHalfAxes(radius, isSmallerSphere)
        if radius > 2 * RH - RR:
            cos_beta = (radius ** 2 + RH ** 2 - (RR - RH) ** 2) / (2 * radius * RH)
            sin_beta = math.sqrt(1 - cos_beta ** 2)
            a_parEff = RH * sin_beta
            return 2 * RH / (a_parallel + a_parEff)
        else:
            return 2 * RH / (a_parallel + a_parMin)

    def DumbbellRadii(self, isSmallerSphere: bool):
        if isSmallerSphere:
            RH = self.inp.dumbbellMinorToRotRadius * self.rotationalRadius
            RR = self.rotationalRadius
        else:
            RH = self.inp.dumbbellMajorToMinorRadius * self.inp.dumbbellMinorToRotRadius * self.rotationalRadius
            RR = self.oppositeRotationalRadius
        return RH, RR

    def DumbbellGroundHalfAxes(self, radius: float, isSmallerSphere: bool):
        RH, RR = self.DumbbellRadii(isSmallerSphere)
        if radius < RR - 2 * RH or radius >= RR:
            return 0, 0, 0
        a_parallel = math.sqrt(RH ** 2 - (radius - RR + RH) ** 2)
        if radius > 2 * RH - RR:
            cos_alpha = (radius ** 2 + RR ** 2 - 2 * RR * RH) / (2 * radius * (RR - RH))
            a_perp = radius * math.acos(cos_alpha)
            a_parMin = 0
        else:
            a_perp = math.pi * radius
            a_parMin = math.sqrt(RH ** 2 - (radius + RR - RH) ** 2)
        return a_parallel, a_perp, a_parMin

    def TubeGroundArea(self, radius: float):
        RT = self.inp.tubeRadiusToRotRadius * self.rotationalRadius
        result = 0
        for innerRadius, outerRadius in self.TubeMinMaxRadii():
            if innerRadius < radius <= outerRadius:
                if radius < RT:
                    result += math.pi * radius * (RT + math.sqrt(RT ** 2 - radius ** 2))
                else:
                    result += math.pi * radius * RT * math.asin(RT / radius)
        return result

    def TubeHullLength(self, radius: float):
        RT = self.inp.tubeRadiusToRotRadius * self.rotationalRadius
        result = 0
        for innerRadius, outerRadius in self.TubeMinMaxRadii():
            if innerRadius < radius <= outerRadius:
                if radius < RT:
                    result += 2 * math.pi * math.sqrt((radius ** 2 + (RT * math.asin(radius / RT)) ** 2) / 2)
                else:
                    result += 2 * math.pi * math.sqrt((RT ** 2 + (radius * math.asin(RT / radius)) ** 2) / 2)
        return result

    def TubeMinMaxRadii(self):  # [minRadius, maxRadius], [otherMinRadius, otherMaxRadius]
        if self.inp.shapeType == ShapeType.Tube:
            return [0, self.rotationalRadius], [0, self.rotationalRadius]
        else:
            smallerHabRadius = self.inp.dumbbellMinorToRotRadius * self.rotationalRadius
            largerHabRadius = self.inp.dumbbellMajorToMinorRadius * smallerHabRadius
            minRadius = max(0, 2 * largerHabRadius - self.oppositeRotationalRadius)
            maxRadius = self.rotationalRadius - 2 * smallerHabRadius
            otherMaxRadius = self.oppositeRotationalRadius - 2 * largerHabRadius
            return [minRadius, maxRadius], [0, otherMaxRadius]
