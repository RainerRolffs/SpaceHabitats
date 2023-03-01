A Physical Model of the Energy Flow in Space Habitats
by Rainer Rolffs

Accompanying paper published in the NSS Space Settlement Journal (https://space.nss.org/national-space-society-space-settlement-journal/)
under https://space.nss.org/wp-content/uploads/NSS-JOURNAL-Energy-Flow-in-Space-Habitats.pdf

Requires python 3.8 or newer, with matplotlib, os, math, enum

Usage:

- main.py runs the program

- input.py defines the input parameters. Multiple habitat powers and runs with different parameters can be specified.


Further files:

- result.py computes the model. The class method computeGeneral is valid for all powers, while each instance requires 
a specific habitat power as well as friction powers in heat absorption, connection, and emission. 
The equations are derived in the paper (EnergyFlow.pdf).

- optimizer.py performs an approximate analytical mass minimization of the cooling friction powers 
if the input paramter isFrictionOptimized is true.

- output.py produces plots and text.

- helpers.py contains enum and function definitions