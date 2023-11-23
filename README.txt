A Physical Model of the Energy Flow in Space Habitats by Rainer Rolffs

Accompanying paper published in the NSS Space Settlement Journal, https://space.nss.org/wp-content/uploads/NSS-JOURNAL-Energy-Flow-in-Space-Habitats.pdf

Code available in https://github.com/RainerRolffs/SpaceHabitats

Requires python 3.8 or newer, with matplotlib, os, math, enum, argparse

Usage:

- input.py defines the input parameters. Multiple habitat powers and runs with different parameters can be specified.

- main.py runs the program. It accepts command-line arguments
	"--volume" for the habitat volume in m³ and/or 
	"--power" for the habitat power in W
They override the powers variable in input.py. If both are set, also the powerPerVolume is adapted.

- The output differs between 
	a single habitat size (such as when using the command-line arguments),
		where some physical properties of the habitat are listed, and
	multiple sizes (when specifying a list of powers in input.py),
		where figures are produced in addition to text.
