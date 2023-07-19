# the model is computed here (first for all powers in class method computeGeneral, then instances for specific power)

import math

import helpers
from input import Input


class Result:

    def __init__(self, inp: Input, habPower, absFriction, conFriction, emFriction):
        self.inp = inp
        self.computeGeneral()

        self.habPower = habPower
        self.absFriction = absFriction
        self.conFriction = conFriction
        self.emFriction = emFriction

        self.habVolume = self.habPower / self.inp.powerPerVolume
        self.habRadius = (self.habVolume / self.inp.aspectRatio / math.pi) ** (1 / 3)
        self.hullSurface = (2 + 2 * self.inp.aspectRatio) * math.pi * self.habRadius ** 2
        self.hullMass = self.hullSurface * self.inp.hullSurfaceDensity
        self.hullVolume = self.hullSurface * (self.inp.hullSurfaceDensity / self.inp.hullDensity + self.inp.gapThickness)
        self.interiorMass = self.habPower * self.inp.interiorMassPerPower

        self.electricFraction = self.inp.electricFraction
        self.computeLightCollection()
        self.isCompleteLighting = (self.lightVolume < self.inp.maxLightVolumeFraction * self.habVolume) \
            and (self.windowArea < self.hullSurface)
        if not self.isCompleteLighting:
            self.electricFraction = 1 - (1 - self.inp.electricFraction) * min(
                (self.inp.maxLightVolumeFraction * self.habVolume) / self.lightVolume,
                self.hullSurface / self.windowArea)
            self.computeLightCollection()

        self.outsidePower = (1 - self.inp.insidePowerFraction) * self.habPower
        self.insidePower = self.habPower - self.outsidePower + self.lightAbsPower + self.windowToHabPower
        self.hullPower = min(self.insidePower, self.hullTransfer * (self.hullSurface - self.windowArea) )
        self.coolingPower = self.insidePower - self.hullPower + self.windowCoolingPower
        self.isCoolingPossible = True  # initialisation

        self.computeAbsorption()

        self.computeEmission()

        self.computeConnection()

        self.electricCoolingPower = ((1 + self.absFriction) * (1 + self.conFriction) * (1 + self.emFriction) - 1) \
            * self.coolingPower
        self.electricCoolingMass = self.electricMassPerPower * self.electricCoolingPower
        self.electricPower = self.habPower * self.electricFraction + self.electricCoolingPower
        self.electricArea = self.electricPower / self.irradiation / self.inp.electricEfficiency
        self.electricMass = self.electricArea * self.inp.electricSurfaceDensity

        self.collectionRadius = ((self.electricArea + self.lightCollectionArea) / math.pi) ** .5
        self.lightRadius = (self.lightCollectionArea / math.pi) ** .5

        self.totalCoolingMass = self.absorptionCoolantMass + self.connectionCoolantMass + self.emissionCoolantMass \
            + self.absorptionSurfaceMass + self.connectionSurfaceMass + self.emissionSurfaceMass + self.electricCoolingMass
        x = 0

    # noinspection PyAttributeOutsideInit
    def computeLightCollection(self):
        self.maxAngularDeviation = self.inp.concentrationFactor ** .5 * 7 / 1.5e3 / self.inp.solarDistance
        self.lightPower = (1 - self.electricFraction) * self.habPower
        self.lightChannelSurface = self.lightPower / self.inp.surfaceIntensity
        self.lightAbsPower = self.lightChannelSurface * (1 - self.inp.innerReflectivity) \
            * self.irradiation * (self.inp.solarDistance * 1.5e11) ** 2 / (3 * 7e8 ** 2) * self.inp.outerReflectivity \
            * (1 - self.inp.windowReflectivity - self.inp.windowAbsorptivity) * self.maxAngularDeviation ** 3
        self.windowPower = (self.lightPower + self.lightAbsPower) \
            / (1 - self.inp.windowReflectivity - self.inp.windowAbsorptivity)
        self.lightCollectionArea = self.windowPower / self.inp.outerReflectivity / self.irradiation
        self.windowArea = self.lightCollectionArea / self.inp.concentrationFactor
        self.lightMass = (self.lightCollectionArea + self.lightChannelSurface) * self.inp.lightSurfaceDensity
        self.windowTemperature = min(self.inp.maxWindowTemperature, (1 / 2 * (self.inp.windowAbsorptivity * self.windowPower
            / (self.windowArea * self.inp.emissivity * 5.67e-8) + self.inp.skyTemp ** 4 + self.inp.maxHabTemp ** 4)) ** .25)
        if self.windowTemperature < self.inp.maxWindowTemperature:
            self.windowCoolingPower = 0
        else:
            self.windowCoolingPower = self.inp.windowAbsorptivity * self.windowPower - self.windowArea * self.inp.emissivity \
                * 5.67e-8 * (2 * self.windowTemperature ** 4 - self.inp.skyTemp ** 4 - self.inp.maxHabTemp ** 4)
        self.windowToHabPower = self.windowArea * self.inp.emissivity * 5.67e-8 * (self.windowTemperature ** 4 - self.inp.maxHabTemp ** 4)
        self.lightVolume = (self.lightPower + self.lightAbsPower) \
            / (3 * self.inp.outerReflectivity * (1 - self.inp.windowReflectivity - self.inp.windowAbsorptivity)
            * self.inp.concentrationFactor * self.irradiation) * self.habRadius
        self.isUnconcentratedLightingPossible = (self.lightCollectionArea < math.pi * self.habRadius ** 2)

    # noinspection PyAttributeOutsideInit
    def computeAbsorption(self):
        self.absorptionFrictionPower = self.absFriction * self.coolingPower
        self.massFlow = (self.coolingPower + self.absorptionFrictionPower) / self.internalEnergyChange
        self.absorptionSurface = self.absorptionSurfacePerPower * self.coolingPower
        self.absorptionSurfaceMass = self.absorptionSurface * self.inp.absorptionSurfaceDensity

        if self.inp.coolantType == helpers.CoolantType.Air and self.massFlow > 0:
            # assuming 2*habitatRadius is a typical length, although radiator-plane incoming pipes, radial distribution, ring-like backflow while absorbing heat, concentration in radiator plane
            lastMassFlow = 2 * self.massFlow  # only for iteration criterium
            while abs(self.massFlow - lastMassFlow) / lastMassFlow > 0.01:
                lastMassFlow = self.massFlow
                self.absorptionVelocity = 2 * self.habRadius * self.massFlow \
                                          / (self.coolantDensity * self.inp.windyVolumeFraction * self.habVolume)
                self.absorptionReynolds = 8 * self.habRadius * self.massFlow / max(1e-10, self.absorptionSurface) / self.viscosity
                self.absorptionFrictionPower = self.frictionFactor(self.absorptionReynolds) * self.coolantDensity / 8 \
                                               / self.inp.pumpEfficiency * self.absorptionSurface * self.absorptionVelocity ** 3
                self.massFlow = (self.coolingPower + self.absorptionFrictionPower) / self.internalEnergyChange
                if self.absorptionFrictionPower > (self.inp.maxFrictionFraction - self.conFriction - self.emFriction) * self.coolingPower:
                    self.isCoolingPossible = False
                    break
            self.absFriction = self.absorptionFrictionPower / max(1e-10, self.coolingPower)
        else:
            self.absorptionReynolds = 8 * self.habRadius * self.massFlow / max(1e-10, self.absorptionSurface) / self.viscosity
            self.absorptionVelocity = (8 * self.inp.pumpEfficiency * self.absorptionFrictionPower
                / self.frictionFactor(self.absorptionReynolds) / self.coolantDensity / max(1e-10, self.absorptionSurface)) ** ( 1 / 3)

        self.absorptionCrossSection = self.massFlow / self.coolantDensity / max(1e-10, self.absorptionVelocity)
        self.absorptionPipeDiameter = 8 * self.habRadius * self.absorptionCrossSection * self.absorptionSurface
        self.absorptionPipeNumber = self.absorptionSurface / math.pi / max(1e-10, self.absorptionPipeDiameter) / 2 / self.habRadius
        if self.inp.coolantType == helpers.CoolantType.Air:
            self.absorptionSurfaceMass = 0
            self.absorptionCoolantMass = 0
            self.absorptionVolume = self.inp.windyVolumeFraction * self.habVolume
        elif self.inp.coolantType == helpers.CoolantType.Vapor:
            liquidAbsorptionReynolds = 8 * self.habRadius * self.massFlow / max(1e-10, self.absorptionSurface) / 1e-3
            liquidAbsorptionVelocity = (8 * self.inp.pumpEfficiency * self.absorptionFrictionPower
                                     / self.frictionFactor(liquidAbsorptionReynolds) / self.inp.liquidDensity / max(1e-10, self.absorptionSurface)) ** (1 / 3)
            self.absorptionCoolantMass = self.massFlow * self.habRadius * (1 / max(1e-10, self.absorptionVelocity) + 1 / max(1e-10, liquidAbsorptionVelocity))
            self.absorptionVolume = self.massFlow * self.habRadius * (1 / max(1e-10, self.absorptionVelocity * self.coolantDensity)
                                                                      + 1 / max(1e-10, liquidAbsorptionVelocity * self.inp.liquidDensity))
        else:  # Liquid
            self.absorptionCoolantMass = 2 * self.massFlow * self.habRadius / max(1e-10, self.absorptionVelocity)
            self.absorptionVolume = self.absorptionCoolantMass / self.coolantDensity

    # noinspection PyAttributeOutsideInit
    def computeEmission(self):
        self.connectionFrictionPower = self.conFriction * (self.coolingPower + self.absorptionFrictionPower)
        self.emissionFrictionPower = self.emFriction * (self.coolingPower + self.absorptionFrictionPower
                                                        + self.connectionFrictionPower)
        self.radiatorPower = (1 + self.absFriction) * (1 + self.conFriction) * (1 + self.emFriction) * self.coolingPower

        connectionTempIncrease = self.connectionFrictionPower / (2 * self.heatCapacity * max(1e-10, self.massFlow))
        if self.inp.coolantType == helpers.CoolantType.Vapor:
            basicEmissionSurface = (self.coolingPower + self.absorptionFrictionPower + self.connectionFrictionPower) \
                                   / (self.inp.emissivity * 5.67e-8 * self.incomingTemp ** 4)
        else:  # Liquid and Air
            basicEmissionSurface = self.massFlow * self.heatCapacity / (3 * self.inp.emissivity * 5.67e-8) \
                * ((self.incomingTemp - connectionTempIncrease) ** -3 - (self.outgoingTemp + connectionTempIncrease) ** -3)
        if self.inp.coolantType == helpers.CoolantType.Air:
            def humidityToT4(T):
                return 18 / 30 * 611 / self.inp.airPressure / 1e5 * math.exp(5321 * (1 / 273 - 1 / T)) * T ** -4
            Tav = (self.outgoingDewPoint + self.incomingTemp - connectionTempIncrease) / 2
            basicEmissionSurface += self.massFlow * 2.45e6 / (self.inp.emissivity * 5.67e-8) \
                * (humidityToT4(self.outgoingDewPoint) - humidityToT4(self.incomingTemp - connectionTempIncrease)
                + 4 * humidityToT4(Tav) * (self.outgoingDewPoint - self.incomingTemp + connectionTempIncrease) / Tav)

        self.effectiveTemp = ((self.coolingPower + self.absorptionFrictionPower + self.connectionFrictionPower)
                              / (self.inp.emissivity * 5.67e-8 * max(1e-10, basicEmissionSurface))) ** (1 / 4)
        self.emissionSurface = (1 + self.emFriction + self.outsidePower / max(1e-10, self.coolingPower)) \
            * self.effectiveTemp ** 4 / (self.effectiveTemp ** 4 - self.inp.skyTemp ** 4) * basicEmissionSurface
        self.emissionSurfaceMass = self.emissionSurface * self.inp.emissionSurfaceDensity
        self.emissionRadius = min(self.inp.maxRadiatorToHabRadius * self.habRadius, self.emissionSurface ** .5 / 4)

        self.emissionReynolds = 8 * self.emissionRadius * self.massFlow / max(1e-10, self.emissionSurface) / self.viscosity
        self.emissionVelocity = (8 * self.inp.pumpEfficiency * self.emissionFrictionPower
            / self.frictionFactor(self.emissionReynolds) / self.coolantDensity / max(1e-10, self.emissionSurface)) ** ( 1 / 3)

        self.emissionCrossSection = self.massFlow / self.coolantDensity / max(1e-10, self.emissionVelocity)
        self.emissionPipeDiameter = 8 * self.emissionRadius * self.emissionCrossSection / max(1e-10, self.emissionSurface)
        self.emissionPipeNumber = self.emissionSurface / math.pi / max(1e-10, self.emissionPipeDiameter) / 2 / self.emissionRadius

        if self.inp.coolantType == helpers.CoolantType.Vapor:
            liquidEmissionReynolds = 8 * self.emissionRadius * self.massFlow / max(1e-10, self.emissionSurface) / 1e-3
            liquidEmissionVelocity = (8 * self.inp.pumpEfficiency * self.emissionFrictionPower
                                     / self.frictionFactor(liquidEmissionReynolds) / self.inp.liquidDensity / max(1e-10, self.emissionSurface)) ** (1 / 3)
            self.emissionCoolantMass = self.massFlow * self.emissionRadius * (1 / max(1e-10, self.emissionVelocity) + 1 / max(1e-10, liquidEmissionVelocity))
            self.emissionVolume = self.massFlow * self.emissionRadius * (1 / max(1e-10, self.emissionVelocity * self.coolantDensity)
                                                                         + 1 / max(1e-10, liquidEmissionVelocity * self.inp.liquidDensity))
        else:
            self.emissionCoolantMass = 2 * self.massFlow * self.emissionRadius / max(1e-10, self.emissionVelocity)
            self.emissionVolume = self.emissionCoolantMass / self.coolantDensity

    # noinspection PyAttributeOutsideInit
    def computeConnection(self):
        self.connectionLength = self.inp.hullSurfaceDensity / self.inp.hullDensity
        self.absorptionLength = self.inp.aspectRatio * self.habRadius / 2
        self.emissionLength = self.emissionSurface / 8 / max(1e-10, self.emissionRadius)
        self.effectiveLength = self.connectionLength + 2 / 3 * (self.absorptionLength + self.emissionLength)
        self.totalLength = 2 * (self.absorptionLength + self.connectionLength + self.emissionLength)

        self.connectionVelocity = self.computeConnectionVelocity(self.viscosity, self.coolantDensity)

        self.connectionSurface = 4 * self.effectiveLength * (2 * math.pi * self.massFlow
            / self.coolantDensity / max(1e-10, self.connectionVelocity)) ** .5
        self.connectionSurfaceMass = self.connectionSurface * self.inp.emissionSurfaceDensity

        connectionReynolds = 2 / self.viscosity * max(1e-10, self.coolantDensity * self.massFlow
                                                        * self.connectionVelocity / 2 / math.pi) ** .5
        self.connectionPipeDiameter = connectionReynolds * self.viscosity / self.coolantDensity / max(1e-10, self.connectionVelocity)
        self.connectionCrossSection = self.massFlow / self.coolantDensity / max(1e-10, self.connectionVelocity)

        if self.inp.coolantType == helpers.CoolantType.Vapor:
            self.connectionCrossSection /= 2
            liquidConnectionVelocity = self.computeConnectionVelocity(1e-3, self.inp.liquidDensity)
            self.connectionCoolantMass = self.massFlow * (self.connectionLength + self.absorptionLength / 2 + self.emissionLength / 2)\
                                         * ( 1 / max(1e-10, self.connectionVelocity) + 1 / max(1e-10, liquidConnectionVelocity))
            self.connectionVolume = self.massFlow * (self.connectionLength + self.absorptionLength / 2 + self.emissionLength / 2)\
                * ( 1 / max(1e-10, self.connectionVelocity * self.coolantDensity) + 1 / max(1e-10, liquidConnectionVelocity * self.inp.liquidDensity))
        else:
            self.connectionCoolantMass = 2 * self.massFlow * (self.connectionLength
                + self.absorptionLength / 2 + self.emissionLength / 2) / max(1e-10, self.connectionVelocity)
            self.connectionVolume = self.connectionCoolantMass / self.coolantDensity

        self.outerConnectionCoolantMass = self.emissionLength / (2 * self.connectionLength + self.absorptionLength + self.emissionLength) * self.connectionCoolantMass
        interiorConnectionVolume = self.absorptionLength / (2 * self.connectionLength + self.absorptionLength + self.emissionLength) * self.connectionVolume
        self.coolantVolumeFraction = (self.absorptionVolume + interiorConnectionVolume) / self.habVolume
        self.connectionAreaFraction = self.connectionCrossSection / math.pi / self.habRadius ** 2
        if self.connectionAreaFraction > 1 or (self.inp.coolantType != helpers.CoolantType.Air and
                                               self.coolantVolumeFraction > self.inp.maxCoolantVolumeFraction):
            self.isCoolingPossible = False

    def computeConnectionVelocity(self, viscosity, density):
        isConFrictionFactorMin = (self.connectionFrictionPower > 3.918e-10 / self.inp.minFrictionFactor ** 19 * viscosity ** 5
                                       * self.effectiveLength / self.inp.pumpEfficiency / max(1e-10, self.massFlow * density) ** 2)
        if isConFrictionFactorMin:
            self.connectionExponent = 2 / 5
            return (0.798 / self.inp.minFrictionFactor * self.inp.pumpEfficiency * self.connectionFrictionPower
                / self.effectiveLength / max(1e-10, density * self.massFlow) ** .5 ) ** self.connectionExponent
        else:
            self.connectionExponent = 8 / 19
            return (2.383 * self.inp.pumpEfficiency * self.connectionFrictionPower / self.effectiveLength
                / max(1e-10, density * self.massFlow) ** (3 / 8) / viscosity ** (1 / 4) ) ** self.connectionExponent


    def computeGeneral(self):

        self.irradiation = 1360 / self.inp.solarDistance ** 2 * (1 - self.inp.shadedFraction)

        self.hullTransfer = self.computeHullTransfer()

        self.electricMassPerPower = self.inp.electricSurfaceDensity / self.irradiation / self.inp.electricEfficiency

        if self.inp.coolantType == helpers.CoolantType.Air:
            self.outgoingTemp = self.inp.maxHabTemp
            self.incomingTemp = self.inp.minHabTemp
        else:
            if self.inp.maxHabTemp - self.inp.minHabTemp < self.inp.tempDiffFlow:
                self.outgoingTemp = self.inp.maxHabTemp - self.inp.minTempDiffHabCoolant
                self.incomingTemp = self.outgoingTemp - self.inp.tempDiffFlow
            else:
                self.incomingTemp = self.inp.minHabTemp - self.inp.minTempDiffHabCoolant
                self.outgoingTemp = self.inp.incomingTemp + self.inp.tempDiffFlow
        self.outgoingDewPoint = 1 / (1 / self.outgoingTemp - math.log(self.inp.outgoingRelativeHumidity) / 5321)
        if self.inp.coolantType == helpers.CoolantType.Liquid:
            self.coolantDensity = self.inp.liquidDensity
            self.heatCapacity = self.inp.liquidHeatCapacity
            self.viscosity = 1e-3
        elif self.inp.coolantType == helpers.CoolantType.Vapor:
            self.coolantDensity = 611 / 461 / self.incomingTemp * math.exp(5321 * (1 / 273 - 1 / self.incomingTemp))
            self.heatCapacity = 1900
            self.viscosity = 8e-6
        else:  # Air
            self.coolantDensity = 1.2 * self.inp.airPressure
            self.heatCapacity = 1000
            self.viscosity = 1.8e-5
        self.internalEnergyChange = self.heatCapacity * (self.outgoingTemp - self.incomingTemp)
        if self.inp.coolantType == helpers.CoolantType.Vapor:
            self.internalEnergyChange += self.inp.vaporLatentHeat
        elif self.inp.coolantType == helpers.CoolantType.Air:
            self.internalEnergyChange += 2.453e6 * 18 / 30 * 611 / self.inp.airPressure / 1e5 \
                                         * (self.inp.outgoingRelativeHumidity * math.exp(5321 * (1 / 273 - 1 / self.outgoingTemp))
                                            - math.exp(5321 * (1 / 273 - 1 / self.incomingTemp)))
        if self.inp.coolantType == helpers.CoolantType.Air:
            self.absorptionSurfacePerPower = self.inp.innerSurfacePerPower
        else:
            maxTempDiffHabCoolant = max(self.inp.maxHabTemp - self.outgoingTemp, self.inp.minHabTemp - self.incomingTemp)
            if maxTempDiffHabCoolant > self.inp.minTempDiffHabCoolant:
                self.absorptionSurfacePerPower = 1 / self.inp.absorptionTransferCoeff / (maxTempDiffHabCoolant - self.inp.minTempDiffHabCoolant) \
                                                 * math.log(maxTempDiffHabCoolant / self.inp.minTempDiffHabCoolant)
            else:
                self.absorptionSurfacePerPower = 1 / self.inp.absorptionTransferCoeff / maxTempDiffHabCoolant

    def frictionFactor(self, reynolds):
        if reynolds == 0:
            return 1e-10
        elif reynolds < 2300:
            return 64 / reynolds
        else:
            return max(self.inp.minFrictionFactor, 0.3164 * reynolds ** (-1 / 4))

    def computeHullTransfer(self):
        hullResistance = self.inp.hullSurfaceDensity / self.inp.hullDensity / self.inp.hullConductivity
        lastPowerPerSurface = 0
        newPowerPerSurface = 100
        dampening = 1 / 5
        while abs(newPowerPerSurface - lastPowerPerSurface) > 0.1:
            powerPerSurface = lastPowerPerSurface + (newPowerPerSurface - lastPowerPerSurface) * dampening
            lastPowerPerSurface = powerPerSurface

            innerHullTemp = self.inp.minHabTemp - powerPerSurface / self.inp.absorptionTransferCoeff

            innerGapTemp = innerHullTemp - powerPerSurface * self.inp.gapLocation * hullResistance

            if self.inp.gapThickness > 0:
                # radiative heat transfer [W/m**2K] (if outerGapTemp 1K lower than innerGapTemp)
                radiativeResistance, effectiveEmissivity, numberReflections = \
                    self.gapRadiation(innerGapTemp, innerGapTemp - 1, self.inp.innerGapEmissivity, self.inp.outerGapEmissivity)
                outerGapTemp = innerGapTemp - powerPerSurface \
                    / (self.inp.gapTransferCoeff / 2 + self.inp.gapConductivity / self.inp.gapThickness + 1 / radiativeResistance)
            else:
                outerGapTemp = innerGapTemp

            surfaceTemp = max(self.inp.skyTemp, outerGapTemp - powerPerSurface * (1 - self.inp.gapLocation) * hullResistance)

            newPowerPerSurface = max(0, 5.67e-8 * self.inp.emissivity * surfaceTemp ** 4
                                     - self.inp.emissivity * 5.67e-8 * self.inp.skyTemp ** 4
                                     - self.irradiation * self.inp.hullSurfaceAbsorptivity / (2 + 2 * self.inp.aspectRatio))

        return powerPerSurface  # transmitted power per surface [W/m**2]

    @staticmethod
    def gapRadiation(T1, T2, e1, e2):
        r1, r2 = 1 - e1, 1 - e2
        i1 = e1 * 5.67e-8 * T1 ** 4
        i2 = -e2 * 5.67e-8 * T2 ** 4
        p = i1 + i2
        nReflections = 0
        lastp = p * 2
        while abs((p - lastp) / lastp) > 0.01:
            lastp = p
            nReflections += 1
            if nReflections % 2 == 1:
                i1 *= -r2
                i2 *= -r1
            else:
                i1 *= -r1
                i2 *= -r2
            p += i1 + i2
        # return resistance, effective emissivity, required number of reflections
        return (T1 - T2) / p, p / 5.67e-8 / (T1 ** 4 - T2 ** 4), nReflections
