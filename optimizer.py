# the mass required for cooling can be approximately minimized here (optimizing the power to overcome friction)

import helpers
import input
from result import Result


def getOptimizedResult(power):
    # computation with start values:
    res = Result(power, input.absorptionFrictionFraction, input.connectionFrictionFraction, input.emissionFrictionFraction)
    if res.coolingPower == 0:
        return Result(power, 0, 0, 0)

    # new friction fractions:
    linearMass = res.outerConnectionCoolantMass + res.emissionSurfaceMass \
                 + res.electricMassPerPower * (1 + res.absFriction) * (1 + res.conFriction) * (1 + res.emFriction) * res.coolingPower

    if input.coolantType == helpers.CoolantType.Air:
        absFriction = res.absFriction  # no optimization for airflow absorption
    else:
        absFriction = ((1 + res.absFriction) * res.absFriction ** (1 / 3) * res.absorptionCoolantMass / 3
            / ( res.absorptionCoolantMass + res.connectionCoolantMass + res.emissionCoolantMass + linearMass)) ** (3 / 4)

    conFriction = ( res.connectionExponent * (1 + res.conFriction) * res.conFriction ** res.connectionExponent
        * res.connectionCoolantMass / linearMass) ** (1 / (res.connectionExponent + 1))

    emFriction = ((1 + res.emFriction) * res.emFriction ** (1 / 3) * res.emissionCoolantMass / 3
        / linearMass) ** (3 / 4)

    scaling = input.maxFrictionFraction / (absFriction + conFriction + emFriction)
    if scaling < 1:
        absFriction *= scaling
        conFriction *= scaling
        emFriction *= scaling

    # computation with optimized friction:
    return Result(power, absFriction, conFriction, emFriction)
