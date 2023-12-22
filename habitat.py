import math

from absorption import Absorption
from connection import Connection
from emission import Emission
from gravity import Gravity
from helpers import ShapeType
from hullTransfer import HullTransfer
from input import Input
from light import LightCollection
from shape import Shape
from structure import Structure


class Habitat:

    def __init__(self, inp: Input, habPower, absFriction, conFriction, emFriction, hullPowerPerSurface=None):
        self.iRun = inp.iRun
        self.habPower = habPower
        self.absFriction = absFriction
        self.conFriction = conFriction
        self.emFriction = emFriction

        self.shape = Shape(inp, habPower)

        self.effectiveHabRadius = (self.shape.crossSection / math.pi) ** .5
        self.effectiveHabLength = self.shape.habVolume / self.shape.crossSection

        if hullPowerPerSurface is not None:
            self.hullPowerPerSurface = hullPowerPerSurface
        else:
            self.hullPowerPerSurface = HullTransfer(inp, self.shape.crossSection / self.shape.hullSurface).powerPerSurface

        # Light
        self.electricFraction = inp.electricFraction
        self.lightPower = self.habPower * (1 - self.electricFraction)
        self.lightCollection = LightCollection(inp,
                                               self.lightPower,
                                               self.effectiveHabRadius,
                                               self.shape.crossSection)
        self.isCompleteLighting = (self.lightCollection.lightVolume < inp.maxLightVolumeFraction * self.shape.habVolume) \
            and (self.lightCollection.windowArea < self.shape.hullSurface)
        if not self.isCompleteLighting:
            self.electricFraction = 1 - (1 - inp.electricFraction) * min(
                (inp.maxLightVolumeFraction * self.shape.habVolume) / self.lightCollection.lightVolume,
                self.shape.hullSurface / self.lightCollection.windowArea)
            self.lightPower = self.habPower * (1 - self.electricFraction)
            self.lightCollection = LightCollection(inp,
                                                   self.lightPower,
                                                   self.effectiveHabRadius,
                                                   self.shape.crossSection)

        self.outsidePower = (1 - inp.insidePowerFraction) * self.habPower
        self.insidePower = self.habPower - self.outsidePower + self.lightCollection.lightAbsPower + self.lightCollection.windowToHabPower
        self.hullPower = min(self.insidePower, self.hullPowerPerSurface * (self.shape.hullSurface - self.lightCollection.windowArea) )
        self.coolingPower = self.insidePower - self.hullPower + self.lightCollection.windowCoolingPower

        self.absorption = Absorption(inp, self.coolingPower, absFriction, conFriction, emFriction, self.effectiveHabRadius, self.shape.habVolume)
        self.absFriction = self.absorption.absorptionFrictionPower / max(1e-10, self.coolingPower)

        coRotRadius = (inp.stressPerDensity * self.shape.rotationalRadius / inp.maxGravity) ** .5
        self.emission = Emission(inp, self.coolingPower, self.absFriction, conFriction, emFriction, self.absorption.massFlow,
                                 self.outsidePower, rotRadius=self.shape.rotationalRadius, coRotRadius=coRotRadius)

        self.connection = Connection(inp, self.effectiveHabRadius, self.effectiveHabLength, self.emission.emissionSurface, self.emission.emissionRadius,
                                     self.absorption.massFlow, self.absorption.absorptionVolume, self.shape.habVolume, self.emission.connectionFrictionPower)

        self.isCoolingPossible = self.absorption.isCoolingPossible and self.connection.isCoolingPossible

        self.electricCoolingPower = ((1 + self.absFriction) * (1 + self.conFriction) * (1 + self.emFriction) - 1) \
            * self.coolingPower
        self.electricMassPerPower = inp.electricSurfaceDensity / inp.getIrradiation() / inp.electricEfficiency
        self.electricCoolingMass = self.electricMassPerPower * self.electricCoolingPower
        self.electricHabMass = self.electricMassPerPower * self.habPower * self.electricFraction
        self.electricPower = self.habPower * self.electricFraction + self.electricCoolingPower
        self.electricArea = self.electricPower / inp.getIrradiation() / inp.electricEfficiency
        self.electricMass = self.electricArea * inp.electricSurfaceDensity

        self.collectionRadius = ((self.electricArea + self.lightCollection.lightCollectionArea) / math.pi) ** .5
        self.lightRadius = (self.lightCollection.lightCollectionArea / math.pi) ** .5

        self.totalCoolingMass = self.absorption.absorptionCoolantMass + self.connection.connectionCoolantMass + self.emission.emissionCoolantMass \
            + self.absorption.absorptionSurfaceMass + self.connection.connectionSurfaceMass + self.emission.emissionSurfaceMass + self.electricCoolingMass

        if inp.shapeType in [ShapeType.Dumbbell, ShapeType.DumbbellTube]:
            self.gravity = Gravity(inp, self.shape.rotationalRadius, self.shape.otherRotationalRadius)
        else:
            self.gravity = Gravity(inp, self.shape.rotationalRadius)
        totalGround = sum(self.gravity.groundAreas)
        totalInnerMass = self.shape.interiorMass + self.shape.airMass + self.absorption.absorptionSurfaceMass + self.absorption.absorptionCoolantMass
        groundDistribution = {self.gravity.groundRadii[i]: self.gravity.groundAreas[i] / totalGround * totalInnerMass for i in range(len(self.gravity.groundRadii)) }
        totalHull = sum(self.gravity.hullAreas)
        hullDistribution = {self.gravity.floorRadii[i]: self.gravity.hullAreas[i] / totalHull * self.shape.hullMass for i in range(len(self.gravity.groundRadii)) }
        self.structure = Structure(inp, rotationalRadius=self.shape.rotationalRadius, habVolume=self.shape.habVolume,
                                        groundDistribution=groundDistribution, hullDistribution=hullDistribution,
                                        radiatorRadius=self.emission.emissionRadius, lightRadius=self.lightRadius, electricRadius=self.collectionRadius,
                                        radiatorMass=self.emission.emissionCoolantMass + self.emission.emissionSurfaceMass,
                                        lightMass=self.lightCollection.lightMass, electricMass=self.electricMass)

        self.totalMass = self.shape.interiorMass + self.shape.airMass + self.shape.hullMass + self.lightCollection.lightMass \
                         + self.electricHabMass + self.totalCoolingMass + self.structure.totalStructuralMass
