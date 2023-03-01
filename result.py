# the model is computed here (first for all powers in class method computeGeneral, then instances for specific power)

import math

import helpers
import input


class Result:

    def __init__(self, habPower, absFriction, conFriction, emFriction):
        self.habPower = habPower
        self.absFriction = absFriction
        self.conFriction = conFriction
        self.emFriction = emFriction

        self.habVolume = self.habPower / input.powerPerVolume
        self.habRadius = (self.habVolume / input.aspectRatio / math.pi) ** (1 / 3)
        self.hullSurface = (2 + 2 * input.aspectRatio) * math.pi * self.habRadius ** 2
        self.hullMass = self.hullSurface * input.hullSurfaceDensity
        self.hullVolume = self.hullSurface * (input.hullSurfaceDensity / input.hullDensity + input.gapThickness)
        self.interiorMass = self.habPower * input.interiorMassPerPower

        self.electricFraction = input.electricFraction
        self.computeLightCollection()
        self.isCompleteLighting = (self.lightVolume < input.maxLightVolumeFraction * self.habVolume) \
            and (self.windowArea < self.hullSurface)
        if not self.isCompleteLighting:
            self.electricFraction = 1 - (1 - input.electricFraction) * min(
                (input.maxLightVolumeFraction * self.habVolume) / self.lightVolume,
                self.hullSurface / self.windowArea)
            self.computeLightCollection()

        self.outsidePower = (1 - input.insidePowerFraction) * self.habPower
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
        self.electricArea = self.electricPower / self.irradiation / input.electricEfficiency
        self.electricMass = self.electricArea * input.electricSurfaceDensity

        self.collectionRadius = ((self.electricArea + self.lightCollectionArea) / math.pi) ** .5
        self.lightRadius = (self.lightCollectionArea / math.pi) ** .5

        self.totalCoolingMass = self.absorptionCoolantMass + self.connectionCoolantMass + self.emissionCoolantMass \
            + self.absorptionSurfaceMass + self.connectionSurfaceMass + self.emissionSurfaceMass + self.electricCoolingMass
        x = 0

    # noinspection PyAttributeOutsideInit
    def computeLightCollection(self):
        self.maxAngularDeviation = input.concentrationFactor ** .5 * 7 / 1.5e3 / input.solarDistance
        self.lightPower = (1 - self.electricFraction) * self.habPower
        self.lightChannelSurface = self.lightPower / input.surfaceIntensity
        self.lightAbsPower = self.lightChannelSurface * (1 - input.innerReflectivity) \
            * self.irradiation * (input.solarDistance * 1.5e11) ** 2 / (3 * 7e8 ** 2) * input.outerReflectivity \
            * (1 - input.windowReflectivity - input.windowAbsorptivity) * self.maxAngularDeviation ** 3
        self.windowPower = (self.lightPower + self.lightAbsPower) \
            / (1 - input.windowReflectivity - input.windowAbsorptivity)
        self.lightCollectionArea = self.windowPower / input.outerReflectivity / self.irradiation
        self.windowArea = self.lightCollectionArea / input.concentrationFactor
        self.lightMass = (self.lightCollectionArea + self.lightChannelSurface) * input.lightSurfaceDensity
        self.windowTemperature = min(input.maxWindowTemperature, (1 / 2 * (input.windowAbsorptivity * self.windowPower
            / (self.windowArea * input.emissivity * 5.67e-8) + input.skyTemp ** 4 + input.maxHabTemp ** 4)) ** .25)
        if self.windowTemperature < input.maxWindowTemperature:
            self.windowCoolingPower = 0
        else:
            self.windowCoolingPower = input.windowAbsorptivity * self.windowPower - self.windowArea * input.emissivity \
                * 5.67e-8 * (2 * self.windowTemperature ** 4 - input.skyTemp ** 4 - input.maxHabTemp ** 4)
        self.windowToHabPower = self.windowArea * input.emissivity * 5.67e-8 * (self.windowTemperature ** 4 - input.maxHabTemp ** 4)
        self.lightVolume = (self.lightPower + self.lightAbsPower) \
            / (3 * input.outerReflectivity * (1 - input.windowReflectivity - input.windowAbsorptivity)
            * input.concentrationFactor * self.irradiation) * self.habRadius
        self.isUnconcentratedLightingPossible = (self.lightCollectionArea < math.pi * self.habRadius ** 2)

    # noinspection PyAttributeOutsideInit
    def computeAbsorption(self):
        self.absorptionFrictionPower = self.absFriction * self.coolingPower
        self.massFlow = (self.coolingPower + self.absorptionFrictionPower) / self.internalEnergyChange
        self.absorptionSurface = self.absorptionSurfacePerPower * self.coolingPower
        self.absorptionSurfaceMass = self.absorptionSurface * input.absorptionSurfaceDensity

        if input.coolantType == helpers.CoolantType.Air and self.massFlow > 0:
            # assuming 2*habitatRadius is a typical length, although radiator-plane incoming pipes, radial distribution, ring-like backflow while absorbing heat, concentration in radiator plane
            lastMassFlow = 2 * self.massFlow  # only for iteration criterium
            while abs(self.massFlow - lastMassFlow) / lastMassFlow > 0.01:
                lastMassFlow = self.massFlow
                self.absorptionVelocity = 2 * self.habRadius * self.massFlow \
                                          / (self.coolantDensity * input.windyVolumeFraction * self.habVolume)
                self.absorptionReynolds = 8 * self.habRadius * self.massFlow / max(1e-10, self.absorptionSurface) / self.viscosity
                self.absorptionFrictionPower = self.frictionFactor(self.absorptionReynolds) * self.coolantDensity / 8 \
                                               / input.pumpEfficiency * self.absorptionSurface * self.absorptionVelocity ** 3
                self.massFlow = (self.coolingPower + self.absorptionFrictionPower) / self.internalEnergyChange
                if self.absorptionFrictionPower > (input.maxFrictionFraction - self.conFriction - self.emFriction) * self.coolingPower:
                    self.isCoolingPossible = False
                    break
            self.absFriction = self.absorptionFrictionPower / max(1e-10, self.coolingPower)
        else:
            self.absorptionReynolds = 8 * self.habRadius * self.massFlow / max(1e-10, self.absorptionSurface) / self.viscosity
            self.absorptionVelocity = (8 * input.pumpEfficiency * self.absorptionFrictionPower
                / self.frictionFactor(self.absorptionReynolds) / self.coolantDensity / max(1e-10, self.absorptionSurface)) ** ( 1 / 3)

        self.absorptionCrossSection = self.massFlow / self.coolantDensity / max(1e-10, self.absorptionVelocity)
        self.absorptionPipeDiameter = 8 * self.habRadius * self.absorptionCrossSection * self.absorptionSurface
        self.absorptionPipeNumber = self.absorptionSurface / math.pi / max(1e-10, self.absorptionPipeDiameter) / 2 / self.habRadius
        if input.coolantType == helpers.CoolantType.Air:
            self.absorptionSurfaceMass = 0
            self.absorptionCoolantMass = 0
            self.absorptionVolume = input.windyVolumeFraction * self.habVolume
        elif input.coolantType == helpers.CoolantType.Vapor:
            liquidAbsorptionReynolds = 8 * self.habRadius * self.massFlow / max(1e-10, self.absorptionSurface) / 1e-3
            liquidAbsorptionVelocity = (8 * input.pumpEfficiency * self.absorptionFrictionPower
                                     / self.frictionFactor(liquidAbsorptionReynolds) / input.liquidDensity / max(1e-10, self.absorptionSurface)) ** (1 / 3)
            self.absorptionCoolantMass = self.massFlow * self.habRadius * (1 / max(1e-10, self.absorptionVelocity) + 1 / max(1e-10, liquidAbsorptionVelocity))
            self.absorptionVolume = self.massFlow * self.habRadius * (1 / max(1e-10, self.absorptionVelocity * self.coolantDensity)
                                                                      + 1 / max(1e-10, liquidAbsorptionVelocity * input.liquidDensity))
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
        if input.coolantType == helpers.CoolantType.Vapor:
            basicEmissionSurface = (self.coolingPower + self.absorptionFrictionPower + self.connectionFrictionPower) \
                                   / (input.emissivity * 5.67e-8 * self.incomingTemp ** 4)
        else:  # Liquid and Air
            basicEmissionSurface = self.massFlow * self.heatCapacity / (3 * input.emissivity * 5.67e-8) \
                * ((self.incomingTemp - connectionTempIncrease) ** -3 - (self.outgoingTemp + connectionTempIncrease) ** -3)
        if input.coolantType == helpers.CoolantType.Air:
            def humidityToT4(T):
                return 18 / 30 * 611 / input.airPressure / 1e5 * math.exp(5321 * (1 / 273 - 1 / T)) * T ** -4
            Tav = (self.outgoingDewPoint + self.incomingTemp - connectionTempIncrease) / 2
            basicEmissionSurface += self.massFlow * 2.45e6 / (input.emissivity * 5.67e-8) \
                * (humidityToT4(self.outgoingDewPoint) - humidityToT4(self.incomingTemp - connectionTempIncrease)
                + 4 * humidityToT4(Tav) * (self.outgoingDewPoint - self.incomingTemp + connectionTempIncrease) / Tav)

        self.effectiveTemp = ((self.coolingPower + self.absorptionFrictionPower + self.connectionFrictionPower)
                              / (input.emissivity * 5.67e-8 * max(1e-10, basicEmissionSurface))) ** (1 / 4)
        self.emissionSurface = (1 + self.emFriction + self.outsidePower / max(1e-10, self.coolingPower)) \
            * self.effectiveTemp ** 4 / (self.effectiveTemp ** 4 - input.skyTemp ** 4) * basicEmissionSurface
        self.emissionSurfaceMass = self.emissionSurface * input.emissionSurfaceDensity
        self.emissionRadius = min(input.maxRadiatorToHabRadius * self.habRadius, self.emissionSurface ** .5 / 4)

        self.emissionReynolds = 8 * self.emissionRadius * self.massFlow / max(1e-10, self.emissionSurface) / self.viscosity
        self.emissionVelocity = (8 * input.pumpEfficiency * self.emissionFrictionPower
            / self.frictionFactor(self.emissionReynolds) / self.coolantDensity / max(1e-10, self.emissionSurface)) ** ( 1 / 3)

        self.emissionCrossSection = self.massFlow / self.coolantDensity / max(1e-10, self.emissionVelocity)
        self.emissionPipeDiameter = 8 * self.emissionRadius * self.emissionCrossSection / max(1e-10, self.emissionSurface)
        self.emissionPipeNumber = self.emissionSurface / math.pi / max(1e-10, self.emissionPipeDiameter) / 2 / self.emissionRadius

        if input.coolantType == helpers.CoolantType.Vapor:
            liquidEmissionReynolds = 8 * self.emissionRadius * self.massFlow / max(1e-10, self.emissionSurface) / 1e-3
            liquidEmissionVelocity = (8 * input.pumpEfficiency * self.emissionFrictionPower
                                     / self.frictionFactor(liquidEmissionReynolds) / input.liquidDensity / max(1e-10, self.emissionSurface)) ** (1 / 3)
            self.emissionCoolantMass = self.massFlow * self.emissionRadius * (1 / max(1e-10, self.emissionVelocity) + 1 / max(1e-10, liquidEmissionVelocity))
            self.emissionVolume = self.massFlow * self.emissionRadius * (1 / max(1e-10, self.emissionVelocity * self.coolantDensity)
                                                                         + 1 / max(1e-10, liquidEmissionVelocity * input.liquidDensity))
        else:
            self.emissionCoolantMass = 2 * self.massFlow * self.emissionRadius / max(1e-10, self.emissionVelocity)
            self.emissionVolume = self.emissionCoolantMass / self.coolantDensity

    # noinspection PyAttributeOutsideInit
    def computeConnection(self):
        self.connectionLength = input.hullSurfaceDensity / input.hullDensity
        self.absorptionLength = input.aspectRatio * self.habRadius / 2
        self.emissionLength = self.emissionSurface / 8 / max(1e-10, self.emissionRadius)
        self.effectiveLength = self.connectionLength + 2 / 3 * (self.absorptionLength + self.emissionLength)
        self.totalLength = 2 * (self.absorptionLength + self.connectionLength + self.emissionLength)

        self.connectionVelocity = self.computeConnectionVelocity(self.viscosity, self.coolantDensity)

        self.connectionSurface = 4 * self.effectiveLength * (2 * math.pi * self.massFlow
            / self.coolantDensity / max(1e-10, self.connectionVelocity)) ** .5
        self.connectionSurfaceMass = self.connectionSurface * input.emissionSurfaceDensity

        connectionReynolds = 2 / self.viscosity * max(1e-10, self.coolantDensity * self.massFlow
                                                        * self.connectionVelocity / 2 / math.pi) ** .5
        self.connectionPipeDiameter = connectionReynolds * self.viscosity / self.coolantDensity / max(1e-10, self.connectionVelocity)
        self.connectionCrossSection = self.massFlow / self.coolantDensity / max(1e-10, self.connectionVelocity)

        if input.coolantType == helpers.CoolantType.Vapor:
            self.connectionCrossSection /= 2
            liquidConnectionVelocity = self.computeConnectionVelocity(1e-3, input.liquidDensity)
            self.connectionCoolantMass = self.massFlow * (self.connectionLength + self.absorptionLength / 2 + self.emissionLength / 2)\
                                         * ( 1 / max(1e-10, self.connectionVelocity) + 1 / max(1e-10, liquidConnectionVelocity))
            self.connectionVolume = self.massFlow * (self.connectionLength + self.absorptionLength / 2 + self.emissionLength / 2)\
                * ( 1 / max(1e-10, self.connectionVelocity * self.coolantDensity) + 1 / max(1e-10, liquidConnectionVelocity * input.liquidDensity))
        else:
            self.connectionCoolantMass = 2 * self.massFlow * (self.connectionLength
                + self.absorptionLength / 2 + self.emissionLength / 2) / max(1e-10, self.connectionVelocity)
            self.connectionVolume = self.connectionCoolantMass / self.coolantDensity

        self.outerConnectionCoolantMass = self.emissionLength / (2 * self.connectionLength + self.absorptionLength + self.emissionLength) * self.connectionCoolantMass
        interiorConnectionVolume = self.absorptionLength / (2 * self.connectionLength + self.absorptionLength + self.emissionLength) * self.connectionVolume
        self.coolantVolumeFraction = (self.absorptionVolume + interiorConnectionVolume) / self.habVolume
        self.connectionAreaFraction = self.connectionCrossSection / math.pi / self.habRadius ** 2
        if self.connectionAreaFraction > 1 or (input.coolantType != helpers.CoolantType.Air and
                                               self.coolantVolumeFraction > input.maxCoolantVolumeFraction):
            self.isCoolingPossible = False

    def computeConnectionVelocity(self, viscosity, density):
        isConFrictionFactorMin = (self.connectionFrictionPower > 3.918e-10 / input.minFrictionFactor ** 19 * viscosity ** 5
                                       * self.effectiveLength / input.pumpEfficiency / max(1e-10, self.massFlow * density) ** 2)
        if isConFrictionFactorMin:
            self.connectionExponent = 2 / 5
            return (0.798 / input.minFrictionFactor * input.pumpEfficiency * self.connectionFrictionPower
                / self.effectiveLength / max(1e-10, density * self.massFlow) ** .5 ) ** self.connectionExponent
        else:
            self.connectionExponent = 8 / 19
            return (2.383 * input.pumpEfficiency * self.connectionFrictionPower / self.effectiveLength
                / max(1e-10, density * self.massFlow) ** (3 / 8) / viscosity ** (1 / 4) ) ** self.connectionExponent


    @classmethod
    def computeGeneral(cls):

        cls.irradiation = 1360 / input.solarDistance ** 2 * (1 - input.shadedFraction)

        cls.hullTransfer = cls.computeHullTransfer()

        cls.electricMassPerPower = input.electricSurfaceDensity / cls.irradiation / input.electricEfficiency

        if input.coolantType == helpers.CoolantType.Air:
            cls.outgoingTemp = input.maxHabTemp
            cls.incomingTemp = input.minHabTemp
        else:
            if input.maxHabTemp - input.minHabTemp < input.tempDiffFlow:
                cls.outgoingTemp = input.maxHabTemp - input.minTempDiffHabCoolant
                cls.incomingTemp = cls.outgoingTemp - input.tempDiffFlow
            else:
                cls.incomingTemp = input.minHabTemp - input.minTempDiffHabCoolant
                cls.outgoingTemp = input.incomingTemp + input.tempDiffFlow
        cls.outgoingDewPoint = 1 / (1 / cls.outgoingTemp - math.log(input.outgoingRelativeHumidity) / 5321)
        if input.coolantType == helpers.CoolantType.Liquid:
            cls.coolantDensity = input.liquidDensity
            cls.heatCapacity = input.liquidHeatCapacity
            cls.viscosity = 1e-3
        elif input.coolantType == helpers.CoolantType.Vapor:
            cls.coolantDensity = 611 / 461 / cls.incomingTemp * math.exp(5321 * (1 / 273 - 1 / cls.incomingTemp))
            cls.heatCapacity = 1900
            cls.viscosity = 8e-6
        else:  # Air
            cls.coolantDensity = 1.2 * input.airPressure
            cls.heatCapacity = 1000
            cls.viscosity = 1.8e-5
        cls.internalEnergyChange = cls.heatCapacity * (cls.outgoingTemp - cls.incomingTemp)
        if input.coolantType == helpers.CoolantType.Vapor:
            cls.internalEnergyChange += input.vaporLatentHeat
        elif input.coolantType == helpers.CoolantType.Air:
            cls.internalEnergyChange += 2.453e6 * 18 / 30 * 611 / input.airPressure / 1e5 \
                                    * (input.outgoingRelativeHumidity * math.exp(5321 * (1 / 273 - 1 / cls.outgoingTemp))
                                       - math.exp(5321 * (1 / 273 - 1 / cls.incomingTemp)))
        if input.coolantType == helpers.CoolantType.Air:
            cls.absorptionSurfacePerPower = input.innerSurfacePerPower
        else:
            maxTempDiffHabCoolant = max(input.maxHabTemp - cls.outgoingTemp, input.minHabTemp - cls.incomingTemp)
            if maxTempDiffHabCoolant > input.minTempDiffHabCoolant:
                cls.absorptionSurfacePerPower = 1 / input.absorptionTransferCoeff / (maxTempDiffHabCoolant - input.minTempDiffHabCoolant) \
                * math.log(maxTempDiffHabCoolant / input.minTempDiffHabCoolant)
            else:
                cls.absorptionSurfacePerPower = 1 / input.absorptionTransferCoeff / maxTempDiffHabCoolant

    @staticmethod
    def frictionFactor(reynolds):
        if reynolds == 0:
            return 1e-10
        elif reynolds < 2300:
            return 64 / reynolds
        else:
            return max(input.minFrictionFactor, 0.3164 * reynolds ** (-1 / 4))

    @classmethod
    def computeHullTransfer(cls):
        hullResistance = input.hullSurfaceDensity / input.hullDensity / input.hullConductivity
        lastPowerPerSurface = 0
        newPowerPerSurface = 100
        dampening = 1 / 5
        while abs(newPowerPerSurface - lastPowerPerSurface) > 0.1:
            powerPerSurface = lastPowerPerSurface + (newPowerPerSurface - lastPowerPerSurface) * dampening
            lastPowerPerSurface = powerPerSurface

            innerHullTemp = input.minHabTemp - powerPerSurface / input.absorptionTransferCoeff

            innerGapTemp = innerHullTemp - powerPerSurface * input.gapLocation * hullResistance

            if input.gapThickness > 0:
                # radiative heat transfer [W/m**2K] (if outerGapTemp 1K lower than innerGapTemp)
                radiativeResistance, effectiveEmissivity, numberReflections = \
                    cls.gapRadiation(innerGapTemp, innerGapTemp - 1, input.innerGapEmissivity, input.outerGapEmissivity)
                outerGapTemp = innerGapTemp - powerPerSurface \
                    / (input.gapTransferCoeff / 2 + input.gapConductivity / input.gapThickness + 1 / radiativeResistance)
            else:
                outerGapTemp = innerGapTemp

            surfaceTemp = max(input.skyTemp, outerGapTemp - powerPerSurface * (1 - input.gapLocation) * hullResistance)

            newPowerPerSurface = max(0, 5.67e-8 * input.emissivity * surfaceTemp ** 4
                              - input.emissivity * 5.67e-8 * input.skyTemp ** 4
                              - cls.irradiation * input.hullSurfaceAbsorptivity / (2 + 2 * input.aspectRatio) )

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
