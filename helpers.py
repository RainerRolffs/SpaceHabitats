# a few helper functions are defined here

import enum
import math


class CoolantType(enum.Enum):
    Liquid = 0
    Vapor = 1
    Air = 2


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

