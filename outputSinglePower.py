# model results are printed here

from habitat import Habitat
from input import Input
from sketch import Sketch
import matplotlib.pyplot as plt


def showResults(inp: Input, runResults: [[Habitat]]):
    for res in runResults:
        hab = res[0]
        print("\nModel run #" + str(hab.iRun) + " " + inp.label[hab.iRun] + ":")

        print("\nHabitat Power %.2e W" % hab.habPower)
        print("\t Light %.2e W" % hab.lightPower)
        print("\t Electricity %.2e W" % (hab.habPower * hab.electricFraction))
        print("Light Absorption %.2e W" % hab.lightCollection.lightAbsPower)
        print("Hull Transmission %.2e W" % hab.hullPower)
        print("Radiator Emission %.2e W" % hab.emission.radiatorPower)
        print("Window Cooling %.2e W" % hab.lightCollection.windowCoolingPower)
        print("Heating of Habitat by Windows %.2e W" % hab.lightCollection.windowToHabPower)
        print("Absorption Friction %.2e W" % hab.absorption.absorptionFrictionPower)
        print("Connection Friction %.2e W" % hab.connection.connectionFrictionPower)
        print("Emission Friction %.2e W" % hab.emission.emissionFrictionPower)

        # print("\nTotal Mass: %.2e W" % hab.t)

        print("\nHull Mass %.2e kg" % hab.shape.hullMass)
        print("Habitat Interior %.2e kg" % hab.shape.interiorMass)
        print("Electricity Generation %.2e kg" % hab.electricMass)
        print("Light Collection %.2e kg" % hab.lightCollection.lightMass)
        print("Total Cooling %.2e kg" % hab.totalCoolingMass)
        print("\t Absorption Surface %.2e kg" % hab.absorption.absorptionSurfaceMass)
        print("\t Emission Surface %.2e kg" % hab.emission.emissionSurfaceMass)
        print("\t Connection Surface %.2e kg" % hab.connection.connectionSurfaceMass)
        print("\t Absorption Coolant %.2e kg" % hab.absorption.absorptionCoolantMass)
        print("\t Connection Coolant %.2e kg" % hab.connection.connectionCoolantMass)
        print("\t Emission Coolant %.2e kg" % hab.emission.emissionCoolantMass)
        print("\t Additional Electricity %.2e kg" % hab.electricCoolingMass)

        print("\nRotational Radius %.2e m" % hab.shape.rotationalRadius)
        print("Energy Collection Radius %.2e m" % hab.collectionRadius)
        print("Emission Length %.2e m" % hab.connection.emissionLength)
        print("Emission Radius %.2e m" % hab.emission.emissionRadius)
        print("Total Connection %.2e m" % hab.connection.totalLength)

        print("\nHull Surface %.2e m²" % hab.shape.hullSurface)
        print("Light Collection %.2e m²" % hab.lightCollection.lightCollectionArea)
        print("Light Channels %.2e m²" % hab.lightCollection.lightChannelSurface)
        print("Electricity Generation %.2e m²" % hab.electricArea)
        print("Absorption Surface %.2e m²" % hab.absorption.absorptionSurface)
        print("Emission Surface %.2e m²" % hab.emission.emissionSurface)
        print("Connection Surface %.2e m²" % hab.connection.connectionSurface)
        print("Windows %.2e m²" % hab.lightCollection.windowArea)
        print("Emission Cross Section %.2e m²" % hab.emission.emissionCrossSection)
        print("Absorption Cross Section %.2e m²" % hab.absorption.absorptionCrossSection)
        print("Connection Cross Section %.2e m²" % hab.connection.connectionCrossSection)

        print("\nInterior Volume %.2e m³" % hab.shape.habVolume)
        print("Hull %.2e m³" % hab.shape.hullVolume)
        print("Light Channels %.2e m³" % hab.lightCollection.lightVolume)
        print("Absorption %.2e m³" % hab.absorption.absorptionVolume)
        print("Connection %.2e m³" % hab.connection.connectionVolume)
        print("Emission %.2e m³" % hab.emission.emissionVolume)

        if not hab.isCoolingPossible:
            print("Cooling not possible!")
        if not hab.isCompleteLighting:
            print("Complete lighting not possible")

        print("Cooling %.2e of habitat volume" % hab.connection.coolantVolumeFraction)

        if hab.iRun == 0:
            #Sketch(rotational_radius=hab.shape.rotationalRadius, cylinder_length_to_rot_radius=inp.cylinderLengthToRotRadius,
#               light_radius=hab.lightRadius, collection_radius=hab.collectionRadius, emission_radius=hab.emission.emissionRadius,
#               emission_length=hab.connection.emissionLength).plot_shape()
            showGravity(hab, inp, False)
            showGravity(hab, inp, True)


def showGravity(hab: Habitat, inp: Input, normalizedToGravWidth: bool):
    fig, ax = plt.subplots()
    ax.set_title("Gravity Distribution")
    ax.set_xlabel("Gravity [m/s²]")

    nbFloors = len(hab.gravity.groundRadii)
    xvals = [hab.gravity.groundRadii[i] * inp.maxGravity / hab.shape.rotationalRadius for i in range(nbFloors)]

    if normalizedToGravWidth:
        widths = [xvals[i] - xvals[i+1] for i in range(nbFloors-1)]
        widths.append(xvals[-1])
        ax.set_ylabel("Distribution [1 / (m/s²)]")
        lstyle = '-'
    else:
        widths = [1 for i in range(nbFloors)]
        ax.set_ylabel("Distribution [fraction of total]")
        lstyle = ''

    totalGround = sum(hab.gravity.groundAreas)
    yvals = [hab.gravity.groundAreas[i] / totalGround / widths[i] for i in range(nbFloors)]

    ax.plot(xvals, yvals, label="Ground", linestyle=lstyle, marker='o')

    xvals = [hab.gravity.floorRadii[i] * inp.maxGravity / hab.shape.rotationalRadius for i in range(nbFloors)]

    totalVolume = sum(hab.gravity.floorVolumes)
    yvals = [hab.gravity.floorVolumes[i] / totalVolume / widths[i] for i in range(nbFloors)]
    ax.plot(xvals, yvals, label="Volume", linestyle=lstyle, marker='o')

    totalHull = sum(hab.gravity.hullAreas)
    yvals = [hab.gravity.hullAreas[i] / totalHull / widths[i] for i in range(nbFloors)]
    ax.plot(xvals, yvals, label="Hull", linestyle=lstyle, marker='o')

    ax.legend()
    plt.show()
