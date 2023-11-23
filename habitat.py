import math

from absorption import Absorption
from connection import Connection
from emission import Emission
from hullTransfer import HullTransfer
from input import Input
from light import LightCollection
from shape import Shape


class Habitat:

    def __init__(self, inp: Input, habPower, absFriction, conFriction, emFriction, hullPowerPerSurface=None):
        self.iRun = inp.iRun
        self.habPower = habPower
        self.absFriction = absFriction
        self.conFriction = conFriction
        self.emFriction = emFriction

        if hullPowerPerSurface is not None:
            self.hullPowerPerSurface = hullPowerPerSurface
        else:
            self.hullPowerPerSurface = HullTransfer(inp).powerPerSurface

        self.shape = Shape(inp, habPower)

        # Light
        self.electricFraction = inp.electricFraction
        self.lightPower = self.habPower * (1 - self.electricFraction)
        self.lightCollection = LightCollection(inp,
                                               self.lightPower,
                                               self.shape.habRadius)
        self.isCompleteLighting = (self.lightCollection.lightVolume < inp.maxLightVolumeFraction * self.shape.habVolume) \
            and (self.lightCollection.windowArea < self.shape.hullSurface)
        if not self.isCompleteLighting:
            self.electricFraction = 1 - (1 - inp.electricFraction) * min(
                (inp.maxLightVolumeFraction * self.shape.habVolume) / self.lightCollection.lightVolume,
                self.shape.hullSurface / self.lightCollection.windowArea)
            self.lightPower = self.habPower * (1 - self.electricFraction)
            self.lightCollection = LightCollection(inp,
                                                   self.lightPower,
                                                   self.shape.habRadius)

        self.outsidePower = (1 - inp.insidePowerFraction) * self.habPower
        self.insidePower = self.habPower - self.outsidePower + self.lightCollection.lightAbsPower + self.lightCollection.windowToHabPower
        self.hullPower = min(self.insidePower, self.hullPowerPerSurface * (self.shape.hullSurface - self.lightCollection.windowArea) )
        self.coolingPower = self.insidePower - self.hullPower + self.lightCollection.windowCoolingPower

        self.absorption = Absorption(inp, self.coolingPower, absFriction, conFriction, emFriction, self.shape.habRadius, self.shape.habVolume)
        self.absFriction = self.absorption.absorptionFrictionPower / max(1e-10, self.coolingPower)

        self.emission = Emission(inp, self.coolingPower, self.absFriction, conFriction, emFriction, self.absorption.massFlow, self.outsidePower, self.shape.habRadius)

        self.connection = Connection(inp, self.shape.habRadius, self.emission.emissionSurface, self.emission.emissionRadius,
                                     self.absorption.massFlow, self.absorption.absorptionVolume, self.shape.habVolume, self.emission.connectionFrictionPower)

        self.isCoolingPossible = self.absorption.isCoolingPossible and self.connection.isCoolingPossible

        self.electricCoolingPower = ((1 + self.absFriction) * (1 + self.conFriction) * (1 + self.emFriction) - 1) \
            * self.coolingPower
        self.electricMassPerPower = inp.electricSurfaceDensity / inp.getIrradiation() / inp.electricEfficiency
        self.electricCoolingMass = self.electricMassPerPower * self.electricCoolingPower
        self.electricPower = self.habPower * self.electricFraction + self.electricCoolingPower
        self.electricArea = self.electricPower / inp.getIrradiation() / inp.electricEfficiency
        self.electricMass = self.electricArea * inp.electricSurfaceDensity

        self.collectionRadius = ((self.electricArea + self.lightCollection.lightCollectionArea) / math.pi) ** .5
        self.lightRadius = (self.lightCollection.lightCollectionArea / math.pi) ** .5

        self.totalCoolingMass = self.absorption.absorptionCoolantMass + self.connection.connectionCoolantMass + self.emission.emissionCoolantMass \
            + self.absorption.absorptionSurfaceMass + self.connection.connectionSurfaceMass + self.emission.emissionSurfaceMass + self.electricCoolingMass
        x = 0
