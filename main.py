# computations are started here
import argparse
import os

from hullTransfer import HullTransfer
from shape import Shape
from input import Input
from output import Output
from habitat import Habitat
import optimizer


def computeSizes():
    pops = inp.population
    if inp.population.__class__ is not list:
        pops = [inp.population]
        print("population %.1e, power %.2e W, volume %.2e m³" % (inp.population, inp.population * inp.powerPerPerson, inp.population * inp.volumePerPerson))

    tempShape = Shape(inp, pops[0] * inp.powerPerPerson)
    hullPowerPerSurface = HullTransfer(inp, tempShape.crossSection / tempShape.hullSurface).powerPerSurface
    results = []
    for pop in pops:
        power = pop * inp.powerPerPerson
        if inp.isFrictionOptimized:
            results.append( optimizer.getOptimizedResult(inp, power, hullPowerPerSurface))
        else:
            results.append( Habitat(inp, power, inp.absorptionFrictionFraction, inp.connectionFrictionFraction,
                                    inp.emissionFrictionFraction, hullPowerPerSurface) )
    return results


if __name__ == '__main__':
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="A Physical Model of Energy Flow and Rotation in Space Habitats. Edit input.py for the input parameters. The following arguments override the powers parameter and, if both provided, also the powerPerVolume.")
    parser.add_argument("--population", type=float, help="a single size, specified by population", default=None)
    parser.add_argument("--volume", type=float, help="a single habitat volume in m³", default=None)
    parser.add_argument("--power", type=float, help="a single habitat power in W", default=None)

    s = "Input in input.py"

    # Parse arguments
    args = parser.parse_args()
    # Create Input object and modify it based on passed arguments
    inp = Input()
    if args.population is not None:
        inp.population = float(args.population)
        s += ", modified by setting the population to %.2e" % inp.population
    elif args.power is not None:
        inp.population = float(args.power) / inp.powerPerPerson
        s += ", modified by setting the habitat power to %.2e W" % inp.population * inp.powerPerPerson
    elif args.volume is not None:
        inp.population = float(args.volume) / inp.volumePerPerson
        s += ", modified by setting the volume to %.2e m³" % inp.population * inp.volumePerPerson

    print(s)
    os.system("mkdir " + inp.project)
    os.system("copy input.py " + inp.project)

    runResults = []
    for iRun in range(inp.numberRuns):
        if inp.numberRuns > 1:
            inp.changeParameters(iRun)
            print("Computing model number %i (%s)..." % (iRun, inp.label[iRun]))
        else:
            print("Computing model " + inp.project+"...")
        runResults.append(computeSizes())

    Output(inp, runResults)
