# the mass required for cooling can be approximately minimized here (optimizing the power to overcome friction)

import helpers
from habitat import Habitat
from input import Input
from result import Result


def getOptimizedResult(inp: Input, power, hullPowerPerSurface):
    # computation with start values:
    res = Habitat(inp, power, inp.absorptionFrictionFraction, inp.connectionFrictionFraction, inp.emissionFrictionFraction, hullPowerPerSurface)
    if res.coolingPower == 0:
        return Habitat(power, 0, 0, 0)

    # new friction fractions:
    linearMass = res.connection.outerConnectionCoolantMass + res.emission.emissionSurfaceMass \
                 + res.electricMassPerPower * (1 + res.absFriction) * (1 + res.conFriction) * (1 + res.emFriction) * res.coolingPower

    if inp.coolantType == helpers.CoolantType.Air:
        absFriction = res.absFriction  # no optimization for airflow absorption
    else:
        absFriction = ((1 + res.absFriction) * res.absFriction ** (1 / 3) * res.absorption.absorptionCoolantMass / 3
            / ( res.absorption.absorptionCoolantMass + res.connection.connectionCoolantMass + res.emission.emissionCoolantMass + linearMass)) ** (3 / 4)

    conFriction = ( res.connection.connectionExponent * (1 + res.conFriction) * res.conFriction ** res.connection.connectionExponent
        * res.connection.connectionCoolantMass / linearMass) ** (1 / (res.connection.connectionExponent + 1))

    emFriction = ((1 + res.emFriction) * res.emFriction ** (1 / 3) * res.emission.emissionCoolantMass / 3
        / linearMass) ** (3 / 4)

    scaling = inp.maxFrictionFraction / (absFriction + conFriction + emFriction)
    if scaling < 1:
        absFriction *= scaling
        conFriction *= scaling
        emFriction *= scaling

    # computation with optimized friction:
    return Habitat(inp, power, absFriction, conFriction, emFriction)
