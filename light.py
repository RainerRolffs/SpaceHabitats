from input import Input
import math


class LightCollection:
    def __init__(self, inp: Input, lightPower, habRadius, crossSection):
        self.maxAngularDeviation = inp.concentrationFactor ** .5 * 7 / 1.5e3 / inp.solarDistance
        self.lightChannelSurface = lightPower / inp.surfaceIntensity
        self.lightAbsPower = self.lightChannelSurface * (1 - inp.innerReflectivity) \
                             * inp.getIrradiation() * (inp.solarDistance * 1.5e11) ** 2 / (3 * 7e8 ** 2) * inp.outerReflectivity \
                             * (1 - inp.windowReflectivity - inp.windowAbsorptivity) * self.maxAngularDeviation ** 3
        self.windowPower = (lightPower + self.lightAbsPower) \
                           / (1 - inp.windowReflectivity - inp.windowAbsorptivity)
        self.lightCollectionArea = self.windowPower / inp.outerReflectivity / inp.getIrradiation()
        self.windowArea = self.lightCollectionArea / inp.concentrationFactor
        self.lightMass = (self.lightCollectionArea + self.lightChannelSurface) * inp.lightSurfaceDensity
        self.windowTemperature = min(inp.maxWindowTemperature, (1 / 2 * (inp.windowAbsorptivity * self.windowPower
                                                                         / (self.windowArea * inp.emissivity * 5.67e-8) + inp.skyTemp ** 4 + inp.maxHabTemp ** 4)) ** .25)
        if self.windowTemperature < inp.maxWindowTemperature:
            self.windowCoolingPower = 0
        else:
            self.windowCoolingPower = inp.windowAbsorptivity * self.windowPower - self.windowArea * inp.emissivity \
                                      * 5.67e-8 * (2 * self.windowTemperature ** 4 - inp.skyTemp ** 4 - inp.maxHabTemp ** 4)
        self.windowToHabPower = self.windowArea * inp.emissivity * 5.67e-8 * (self.windowTemperature ** 4 - inp.maxHabTemp ** 4)
        self.lightVolume = (lightPower + self.lightAbsPower) \
                           / (3 * inp.outerReflectivity * (1 - inp.windowReflectivity - inp.windowAbsorptivity)
                              * inp.concentrationFactor * inp.getIrradiation()) * habRadius
        self.isUnconcentratedLightingPossible = (self.lightCollectionArea < crossSection)
