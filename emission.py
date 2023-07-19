import math
import helpers
from input import Input


class Emission:
    def __init__(self, inp: Input, coolingPower, absFriction, conFriction, emFriction, massFlow, outsidePower, habRadius):
        coolingHelper = helpers.CoolingHelper(inp)
        self.absorptionFrictionPower = absFriction * coolingPower
        self.connectionFrictionPower = conFriction * (coolingPower + self.absorptionFrictionPower)
        self.emissionFrictionPower = emFriction * (coolingPower + self.absorptionFrictionPower
                                                        + self.connectionFrictionPower)
        self.radiatorPower = (1 + absFriction) * (1 + conFriction) * (1 + emFriction) * coolingPower

        connectionTempIncrease = self.connectionFrictionPower / (2 * coolingHelper.heatCapacity * max(1e-10, massFlow))
        if inp.coolantType == helpers.CoolantType.Vapor:
            basicEmissionSurface = (coolingPower + self.absorptionFrictionPower + self.connectionFrictionPower) \
                                   / (inp.emissivity * 5.67e-8 * coolingHelper.incomingTemp ** 4)
        else:  # Liquid and Air
            basicEmissionSurface = massFlow * coolingHelper.heatCapacity / (3 * inp.emissivity * 5.67e-8) \
                                   * ((coolingHelper.incomingTemp - connectionTempIncrease) ** -3 - (coolingHelper.outgoingTemp + connectionTempIncrease) ** -3)
        if inp.coolantType == helpers.CoolantType.Air:
            def humidityToT4(T):
                return 18 / 30 * 611 / inp.airPressure / 1e5 * math.exp(5321 * (1 / 273 - 1 / T)) * T ** -4

            Tav = (coolingHelper.outgoingDewPoint + coolingHelper.incomingTemp - connectionTempIncrease) / 2
            basicEmissionSurface += massFlow * 2.45e6 / (inp.emissivity * 5.67e-8) \
                                    * (humidityToT4(coolingHelper.outgoingDewPoint) - humidityToT4(coolingHelper.incomingTemp - connectionTempIncrease)
                                       + 4 * humidityToT4(Tav) * (coolingHelper.outgoingDewPoint - coolingHelper.incomingTemp + connectionTempIncrease) / Tav)

        self.effectiveTemp = ((coolingPower + self.absorptionFrictionPower + self.connectionFrictionPower)
                              / (inp.emissivity * 5.67e-8 * max(1e-10, basicEmissionSurface))) ** (1 / 4)
        self.emissionSurface = (1 + emFriction + outsidePower / max(1e-10, coolingPower)) \
                               * self.effectiveTemp ** 4 / (self.effectiveTemp ** 4 - inp.skyTemp ** 4) * basicEmissionSurface
        self.emissionSurfaceMass = self.emissionSurface * inp.emissionSurfaceDensity
        self.emissionRadius = min(inp.maxRadiatorToHabRadius * habRadius, self.emissionSurface ** .5 / 4)

        self.emissionReynolds = 8 * self.emissionRadius * massFlow / max(1e-10, self.emissionSurface) / coolingHelper.viscosity
        self.emissionVelocity = (8 * inp.pumpEfficiency * self.emissionFrictionPower
                                 / helpers.frictionFactor(self.emissionReynolds, inp.minFrictionFactor) / coolingHelper.coolantDensity / max(1e-10, self.emissionSurface)) ** (1 / 3)

        self.emissionCrossSection = massFlow / coolingHelper.coolantDensity / max(1e-10, self.emissionVelocity)
        self.emissionPipeDiameter = 8 * self.emissionRadius * self.emissionCrossSection / max(1e-10, self.emissionSurface)
        self.emissionPipeNumber = self.emissionSurface / math.pi / max(1e-10, self.emissionPipeDiameter) / 2 / self.emissionRadius

        if inp.coolantType == helpers.CoolantType.Vapor:
            liquidEmissionReynolds = 8 * self.emissionRadius * massFlow / max(1e-10, self.emissionSurface) / 1e-3
            liquidEmissionVelocity = (8 * inp.pumpEfficiency * self.emissionFrictionPower
                                      / helpers.frictionFactor(liquidEmissionReynolds, inp.minFrictionFactor) / inp.liquidDensity / max(1e-10, self.emissionSurface)) ** (1 / 3)
            self.emissionCoolantMass = massFlow * self.emissionRadius * (1 / max(1e-10, self.emissionVelocity) + 1 / max(1e-10, liquidEmissionVelocity))
            self.emissionVolume = massFlow * self.emissionRadius * (1 / max(1e-10, self.emissionVelocity * coolingHelper.coolantDensity)
                                                                         + 1 / max(1e-10, liquidEmissionVelocity * inp.liquidDensity))
        else:
            self.emissionCoolantMass = 2 * massFlow * self.emissionRadius / max(1e-10, self.emissionVelocity)
            self.emissionVolume = self.emissionCoolantMass / coolingHelper.coolantDensity
