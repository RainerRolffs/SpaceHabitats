# computations are started here
from hullTransfer import HullTransfer
from input import Input
import output
from habitat import Habitat
import optimizer


def computePowers():
    hullPowerPerSurface = HullTransfer(inp).powerPerSurface
    results = []
    for power in inp.powers:
        if inp.isFrictionOptimized:
            results.append( optimizer.getOptimizedResult(inp, power, hullPowerPerSurface))
        else:
            results.append( Habitat(inp, power,
                inp.absorptionFrictionFraction, inp.connectionFrictionFraction, inp.emissionFrictionFraction, hullPowerPerSurface) )
    return results


if __name__ == '__main__':
    runResults = []
    inp = Input()
    for iRun in range(inp.numberRuns):
        inp.changeParameters(iRun)
        runResults.append( computePowers() )
    output.writeResults(inp, runResults)
