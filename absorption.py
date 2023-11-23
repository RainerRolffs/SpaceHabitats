import math

import helpers
from input import Input


class Absorption:
    def __init__(self, inp: Input, coolingPower, absFriction, conFriction, emFriction, habRadius, habVolume):
        coolingHelper = helpers.CoolingHelper(inp)
        self.absorptionFrictionPower = absFriction * coolingPower
        self.massFlow = (coolingPower + self.absorptionFrictionPower) / coolingHelper.internalEnergyChange
        self.absorptionSurface = coolingHelper.absorptionSurfacePerPower * coolingPower
        self.absorptionSurfaceMass = self.absorptionSurface * inp.absorptionSurfaceDensity

        self.isCoolingPossible = True  # initialisation
        if inp.coolantType == helpers.CoolantType.Air and self.massFlow > 0:
            lastMassFlow = 2 * self.massFlow  # only for iteration criterium
            while abs(self.massFlow - lastMassFlow) / lastMassFlow > 0.01:
                lastMassFlow = self.massFlow
                self.absorptionVelocity = 2 * habRadius * self.massFlow \
                                          / (coolingHelper.coolantDensity * inp.windyVolumeFraction * habVolume)
                self.absorptionReynolds = 8 * habRadius * self.massFlow / max(1e-10, self.absorptionSurface) / coolingHelper.viscosity
                self.absorptionFrictionPower = helpers.frictionFactor(self.absorptionReynolds, inp.minFrictionFactor) * coolingHelper.coolantDensity / 8 \
                                               / inp.pumpEfficiency * self.absorptionSurface * self.absorptionVelocity ** 3
                self.massFlow = (coolingPower + self.absorptionFrictionPower) / coolingHelper.internalEnergyChange
                if self.absorptionFrictionPower > (inp.maxFrictionFraction - conFriction - emFriction) * coolingPower:
                    self.isCoolingPossible = False
                    break
        else:
            self.absorptionReynolds = 8 * habRadius * self.massFlow / max(1e-10, self.absorptionSurface) / coolingHelper.viscosity
            self.absorptionVelocity = (8 * inp.pumpEfficiency * self.absorptionFrictionPower
                / helpers.frictionFactor(self.absorptionReynolds, inp.minFrictionFactor) / coolingHelper.coolantDensity / max(1e-10, self.absorptionSurface)) ** ( 1 / 3)

        self.absorptionCrossSection = self.massFlow / coolingHelper.coolantDensity / max(1e-10, self.absorptionVelocity)
        self.absorptionPipeDiameter = 8 * habRadius * self.absorptionCrossSection * self.absorptionSurface
        self.absorptionPipeNumber = self.absorptionSurface / math.pi / max(1e-10, self.absorptionPipeDiameter) / 2 / habRadius
        if inp.coolantType == helpers.CoolantType.Air:
            self.absorptionSurfaceMass = 0
            self.absorptionCoolantMass = 0
            self.absorptionVolume = inp.windyVolumeFraction * habVolume
        elif inp.coolantType == helpers.CoolantType.Vapor:
            liquidAbsorptionReynolds = 8 * habRadius * self.massFlow / max(1e-10, self.absorptionSurface) / 1e-3
            liquidAbsorptionVelocity = (8 * inp.pumpEfficiency * self.absorptionFrictionPower
                                     / helpers.frictionFactor(liquidAbsorptionReynolds, inp.minFrictionFactor) / inp.liquidDensity / max(1e-10, self.absorptionSurface)) ** (1 / 3)
            self.absorptionCoolantMass = self.massFlow * habRadius * (1 / max(1e-10, self.absorptionVelocity) + 1 / max(1e-10, liquidAbsorptionVelocity))
            self.absorptionVolume = self.massFlow * habRadius * (1 / max(1e-10, self.absorptionVelocity * coolingHelper.coolantDensity)
                                                                      + 1 / max(1e-10, liquidAbsorptionVelocity * inp.liquidDensity))
        else:  # Liquid
            self.absorptionCoolantMass = 2 * self.massFlow * habRadius / max(1e-10, self.absorptionVelocity)
            self.absorptionVolume = self.absorptionCoolantMass / coolingHelper.coolantDensity
