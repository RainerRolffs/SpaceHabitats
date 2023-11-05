from input import Input


class HullTransfer:
    def __init__(self, inp: Input, crossSectionToHullSurface: float):
        hullResistance = inp.hullSurfaceDensity / inp.hullDensity / inp.hullConductivity
        lastPowerPerSurface = 0
        newPowerPerSurface = 100
        dampening = 1 / 5
        while abs(newPowerPerSurface - lastPowerPerSurface) > 0.1:
            self.powerPerSurface = lastPowerPerSurface + (newPowerPerSurface - lastPowerPerSurface) * dampening
            lastPowerPerSurface = self.powerPerSurface

            innerHullTemp = inp.minHabTemp - self.powerPerSurface / inp.absorptionTransferCoeff

            innerGapTemp = innerHullTemp - self.powerPerSurface * inp.gapLocation * hullResistance

            if inp.gapThickness > 0:
                # radiative heat transfer [W/m**2K] (if outerGapTemp 1K lower than innerGapTemp)
                radiativeResistance, effectiveEmissivity, numberReflections = \
                    self.gapRadiation(innerGapTemp, innerGapTemp - 1, inp.innerGapEmissivity, inp.outerGapEmissivity)
                outerGapTemp = innerGapTemp - self.powerPerSurface \
                               / (inp.gapTransferCoeff / 2 + inp.gapConductivity / inp.gapThickness + 1 / radiativeResistance)
            else:
                outerGapTemp = innerGapTemp

            surfaceTemp = max(inp.skyTemp, outerGapTemp - self.powerPerSurface * (1 - inp.gapLocation) * hullResistance)

            newPowerPerSurface = max(0, 5.67e-8 * inp.emissivity * surfaceTemp ** 4
                                     - inp.emissivity * 5.67e-8 * inp.skyTemp ** 4
                                     - inp.getIrradiation() * inp.hullSurfaceAbsorptivity * crossSectionToHullSurface)
        # return powerPerSurface  # transmitted power per surface [W/m**2]

    def gapRadiation(self, T1, T2, e1, e2):
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
