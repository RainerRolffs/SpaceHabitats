# computations are started here
import argparse
from hullTransfer import HullTransfer
from input import Input
import output, outputSinglePower
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
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="A Physical Model of the Energy Flow in Space Habitats. Edit input.py for the input parameters. The following arguments override the powers parameter and, if both provided, also the powerPerVolume.")
    parser.add_argument("--volume", type=float, help="a single habitat volume in m³", default=None)
    parser.add_argument("--power", type=float, help="a single habitat power in W", default=None)

    s = "Input in input.py"

    # Parse arguments
    args = parser.parse_args()
    # Create Input object and modify it based on passed arguments
    inp = Input()
    if args.power is not None:
        inp.powers = [float(args.power)]
        s += ", modified by setting the habitat power to %.2e W" % inp.powers[0]
        if args.volume is not None:
            inp.powerPerVolume = float(args.power) / float(args.volume)
            s += " and the volume to %.2e m³" % (inp.powers[0] / inp.powerPerVolume)
        else:
            s += " (volume is %.2e m³)" % (inp.powers[0] / inp.powerPerVolume)

    elif args.volume is not None:
        inp.powers = [args.volume * inp.powerPerVolume]
        s += ", modified by setting the volume to %.2e m³ (power is %.2e W)" % ((inp.powers[0] / inp.powerPerVolume), inp.powers[0])

    print(s)

    runResults = []
    for iRun in range(inp.numberRuns):
        inp.changeParameters(iRun)
        runResults.append( computePowers() )

    if len(inp.powers) == 1:
        outputSinglePower.showResults(inp, runResults)
    else:
        output.writeResults(inp, runResults)
