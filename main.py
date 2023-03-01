# computations are started here

import input
import output
from result import Result
import optimizer


def computePowers():
    Result.computeGeneral()
    results = []
    for power in input.powers:
        if input.isFrictionOptimized:
            results.append( optimizer.getOptimizedResult(power))
        else:
            results.append( Result(power,
                input.absorptionFrictionFraction, input.connectionFrictionFraction, input.emissionFrictionFraction) )
    return results


if __name__ == '__main__':
    runResults = []
    for iRun in range(input.numberRuns):
        input.changeParameters(input, iRun)
        runResults.append( computePowers() )
    output.writeResults(runResults)
