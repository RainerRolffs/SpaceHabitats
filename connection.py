import math

import helpers
from input import Input


class Connection:
    def __init__(self, inp: Input, habRadius, emissionSurface, emissionRadius, massFlow, absorptionVolume, habVolume, connectionFrictionPower):
        self.inp = inp
        self.massFlow = massFlow
        self.connectionFrictionPower = connectionFrictionPower
        coolingHelper = helpers.CoolingHelper(inp)

        self.connectionLength = inp.hullSurfaceDensity / inp.hullDensity
        self.absorptionLength = inp.aspectRatio * habRadius / 2
        self.emissionLength = emissionSurface / 8 / max(1e-10, emissionRadius)
        self.effectiveLength = self.connectionLength + 2 / 3 * (self.absorptionLength + self.emissionLength)
        self.totalLength = 2 * (self.absorptionLength + self.connectionLength + self.emissionLength)
    
        self.connectionVelocity = self.computeConnectionVelocity(coolingHelper.viscosity, coolingHelper.coolantDensity)
    
        self.connectionSurface = 4 * self.effectiveLength * (2 * math.pi * massFlow
                                                             / coolingHelper.coolantDensity / max(1e-10, self.connectionVelocity)) ** .5
        self.connectionSurfaceMass = self.connectionSurface * inp.emissionSurfaceDensity
    
        connectionReynolds = 2 / coolingHelper.viscosity * max(1e-10, coolingHelper.coolantDensity * massFlow
                                                      * self.connectionVelocity / 2 / math.pi) ** .5
        self.connectionPipeDiameter = connectionReynolds * coolingHelper.viscosity / coolingHelper.coolantDensity / max(1e-10, self.connectionVelocity)
        self.connectionCrossSection = massFlow / coolingHelper.coolantDensity / max(1e-10, self.connectionVelocity)
    
        if inp.coolantType == helpers.CoolantType.Vapor:
            self.connectionCrossSection /= 2
            liquidConnectionVelocity = self.computeConnectionVelocity(1e-3, inp.liquidDensity)
            self.connectionCoolantMass = massFlow * (self.connectionLength + self.absorptionLength / 2 + self.emissionLength / 2) \
                                         * (1 / max(1e-10, self.connectionVelocity) + 1 / max(1e-10, liquidConnectionVelocity))
            self.connectionVolume = massFlow * (self.connectionLength + self.absorptionLength / 2 + self.emissionLength / 2) \
                                    * (1 / max(1e-10, self.connectionVelocity * coolingHelper.coolantDensity) + 1 / max(1e-10, liquidConnectionVelocity * inp.liquidDensity))
        else:
            self.connectionCoolantMass = 2 * massFlow * (self.connectionLength
                                                              + self.absorptionLength / 2 + self.emissionLength / 2) / max(1e-10, self.connectionVelocity)
            self.connectionVolume = self.connectionCoolantMass / coolingHelper.coolantDensity
    
        self.outerConnectionCoolantMass = self.emissionLength / (2 * self.connectionLength + self.absorptionLength + self.emissionLength) * self.connectionCoolantMass
        interiorConnectionVolume = self.absorptionLength / (2 * self.connectionLength + self.absorptionLength + self.emissionLength) * self.connectionVolume
        self.coolantVolumeFraction = (absorptionVolume + interiorConnectionVolume) / habVolume
        self.connectionAreaFraction = self.connectionCrossSection / math.pi / habRadius ** 2
        self.isCoolingPossible = True
        if self.connectionAreaFraction > 1 or (inp.coolantType != helpers.CoolantType.Air and
                                               self.coolantVolumeFraction > inp.maxCoolantVolumeFraction):
            self.isCoolingPossible = False
    
    def computeConnectionVelocity(self, viscosity, density):
        isConFrictionFactorMin = (self.connectionFrictionPower > 3.918e-10 / self.inp.minFrictionFactor ** 19 * viscosity ** 5
                                  * self.effectiveLength / self.inp.pumpEfficiency / max(1e-10, self.massFlow * density) ** 2)
        if isConFrictionFactorMin:
            self.connectionExponent = 2 / 5
            return (0.798 / self.inp.minFrictionFactor * self.inp.pumpEfficiency * self.connectionFrictionPower
                    / self.effectiveLength / max(1e-10, density * self.massFlow) ** .5) ** self.connectionExponent
        else:
            self.connectionExponent = 8 / 19
            return (2.383 * self.inp.pumpEfficiency * self.connectionFrictionPower / self.effectiveLength
                    / max(1e-10, density * self.massFlow) ** (3 / 8) / viscosity ** (1 / 4)) ** self.connectionExponent
