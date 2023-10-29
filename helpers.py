# a few helper functions are defined here

import enum
import math


class ShapeType(enum.Enum):
    Oblate = 0
    Prolate = 1
    Cylinder = 2
    Torus = 3
    Dumbbell = 4


class CoolantType(enum.Enum):
    Liquid = 0
    Vapor = 1
    Air = 2


class CoolingHelper:
    def __init__(self, inp):
        if inp.coolantType == CoolantType.Air:
            self.outgoingTemp = inp.maxHabTemp
            self.incomingTemp = inp.minHabTemp
        else:
            if inp.maxHabTemp - inp.minHabTemp < inp.tempDiffFlow:
                self.outgoingTemp = inp.maxHabTemp - inp.minTempDiffHabCoolant
                self.incomingTemp = self.outgoingTemp - inp.tempDiffFlow
            else:
                self.incomingTemp = inp.minHabTemp - inp.minTempDiffHabCoolant
                self.outgoingTemp = inp.incomingTemp + inp.tempDiffFlow
        self.outgoingDewPoint = 1 / (1 / self.outgoingTemp - math.log(inp.outgoingRelativeHumidity) / 5321)
        if inp.coolantType == CoolantType.Liquid:
            self.coolantDensity = inp.liquidDensity
            self.heatCapacity = inp.liquidHeatCapacity
            self.viscosity = 1e-3
        elif inp.coolantType == CoolantType.Vapor:
            self.coolantDensity = 611 / 461 / self.incomingTemp * math.exp(5321 * (1 / 273 - 1 / self.incomingTemp))
            self.heatCapacity = 1900
            self.viscosity = 8e-6
        else:  # Air
            self.coolantDensity = 1.2 * inp.airPressure
            self.heatCapacity = 1000
            self.viscosity = 1.8e-5
        self.internalEnergyChange = self.heatCapacity * (self.outgoingTemp - self.incomingTemp)
        if inp.coolantType == CoolantType.Vapor:
            self.internalEnergyChange += inp.vaporLatentHeat
        elif inp.coolantType == CoolantType.Air:
            self.internalEnergyChange += 2.453e6 * 18 / 30 * 611 / inp.airPressure / 1e5 \
                                        * (inp.outgoingRelativeHumidity * math.exp(5321 * (1 / 273 - 1 / self.outgoingTemp))
                                           - math.exp(5321 * (1 / 273 - 1 / self.incomingTemp)))
        if inp.coolantType == CoolantType.Air:
            self.absorptionSurfacePerPower = inp.innerSurfacePerPower
        else:
            maxTempDiffHabCoolant = max(inp.maxHabTemp - self.outgoingTemp, inp.minHabTemp - self.incomingTemp)
            if maxTempDiffHabCoolant > inp.minTempDiffHabCoolant:
                self.absorptionSurfacePerPower = 1 / inp.absorptionTransferCoeff / (maxTempDiffHabCoolant - inp.minTempDiffHabCoolant) \
                                                * math.log(maxTempDiffHabCoolant / inp.minTempDiffHabCoolant)
            else:
                self.absorptionSurfacePerPower = 1 / inp.absorptionTransferCoeff / maxTempDiffHabCoolant
    

def LogRange(numberOfModels, minPower, maxPower):
    if numberOfModels == 1:
        return [minPower]
    dLog = (math.log(maxPower) - math.log(minPower)) / (numberOfModels - 1)
    logPower = math.log(minPower)
    powers = []
    for i in range(numberOfModels):
        powers.append(math.exp(logPower))
        logPower += dLog
    return powers


def frictionFactor(reynolds, minFrictionFactor):
    if reynolds == 0:
        return 1e-10
    elif reynolds < 2300:
        return 64 / reynolds
    else:
        return max(minFrictionFactor, 0.3164 * reynolds ** (-1 / 4))



