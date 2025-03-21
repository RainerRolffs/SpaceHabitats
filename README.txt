A Physical Model of Energy Flow and Rotation in Space Habitats by Rainer Rolffs

Accompanying paper published in the NSS Space Settlement Journal, https://space.nss.org/wp-content/uploads/NSS-JOURNAL-Energy-Flow-in-Space-Habitats.pdf

Code available in https://github.com/RainerRolffs/SpaceHabitats

Requires python 3.8 or newer, with matplotlib, os, math, enum, argparse

Usage:

- input.py defines the input parameters. Multiple habitat sizes and runs with different parameters can be specified.

- main.py runs the program. Alternatively to the input.py, a single size can be specified by command-line arguments
    "--population" for the habitat population
	"--volume" for the habitat volume in m³ and/or 
	"--power" for the habitat power in W

- The type of output depends on the number of runs and sizes, and can be adapted in output.py.