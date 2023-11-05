# model results are plotted here

import os
import matplotlib.pyplot as plt

from habitat import Habitat
from input import Input


def writeResults(inp: Input, runResults: [[Habitat]]):
    os.system("mkdir " + inp.project)
    os.system("copy input.py " + inp.project)

    def plot(y, lab, cont="", perPower=True, lstyle="-"):
        yvals = []
        for res in results:
            if ((cont == "cool") and res.isCoolingPossible) or (cont == "light") or (cont == ""):
                if "." in y:
                    yvals.append(getattr(getattr(res, y.split(".")[0]), y.split(".")[1]))
                else:
                    yvals.append(getattr(res, y))
                if perPower:
                    yvals[-1] /= res.habPower
        ax.plot(xvals[:len(yvals)], yvals, label=lab, linestyle=lstyle)
        if len(yvals) > 0:
            print(lab + ": %.2e" % yvals[0])

    results = runResults[0]
    xvals = [res.habPower for res in results]

    fig, ax = plt.subplots()
    ax.set_title("Ratio of Mass to Habitat Power")
    ax.set_xlabel("Habitat Power [W]")
    ax.set_ylabel("Mass per Power [kg/W]")
    ax.loglog()
    print("\nMass per Power [kg/W] at %.2e W" % xvals[0])
    plot("shape.hullMass", "Hull")
    plot("shape.interiorMass", "Habitat Interior")
    plot("electricMass", "Electricity Generation")
    plot("lightCollection.lightMass", "Light Collection", "light")
    plot("totalCoolingMass", "Total Cooling", "cool")
    plot("absorption.absorptionSurfaceMass", "Absorption Surface", "cool", True, "--")
    plot("emission.emissionSurfaceMass", "Emission Surface", "cool", True, "--")
    plot("connection.connectionSurfaceMass", "Connection Surface", "cool", True, "--")
    plot("absorption.absorptionCoolantMass", "Absorption Coolant", "cool", True, ":")
    plot("connection.connectionCoolantMass", "Connection Coolant", "cool", True, ":")
    plot("electricCoolingMass", "Additional Electricity", "cool", True, "--")
    plot("emission.emissionCoolantMass", "Emission Coolant", "cool", True, ":")
    ax.legend()
    fig.savefig(inp.project + "\\masses.pdf")

    fig, ax = plt.subplots()
    ax.set_title("Ratio of Area to Habitat Power")
    ax.set_xlabel("Habitat Power [W]")
    ax.set_ylabel("Area per Power [m²/W]")
    ax.loglog()
    print("\nArea per Power [m²/W]")
    plot("shape.hullSurface", "Hull Surface")
    plot("lightCollection.lightCollectionArea", "Light Collection", "light", True, "--")
    plot("lightCollection.lightChannelSurface", "Light Channels", "light")
    plot("electricArea", "Electricity Generation", "", True, "--")
    plot("absorption.absorptionSurface", "Absorption Surface", "cool")
    plot("emission.emissionSurface", "Emission Surface", "cool")
    plot("connection.connectionSurface", "Connection Surface", "cool")
    plot("lightCollection.windowArea", "Windows", "light")
    plot("emission.emissionCrossSection", "Emission Cross Section", "cool", True, "--")
    plot("absorption.absorptionCrossSection", "Absorption Cross Section", "cool", True, "--")
    plot("connection.connectionCrossSection", "Connection Cross Section", "cool", True, "--")
    ax.legend()
    fig.savefig(inp.project + "\\surfaces.pdf")

    fig, ax = plt.subplots()
    ax.set_title("Ratio of Length to Habitat Power")
    ax.set_xlabel("Habitat Power [W]")
    ax.set_ylabel("Length per Power [m/W]")
    ax.loglog()
    print("\nLength per Power [m/W]")
    plot("shape.effectiveHabRadius", "Habitat Radius")
    plot("collectionRadius", "Energy Collection Radius", "light")
    plot("connection.emissionLength", "Emission Length", "cool")
    plot("emission.emissionRadius", "Emission Radius", "cool")
    plot("connection.totalLength", "Total Connection", "cool")
    ax.legend()
    fig.savefig(inp.project + "\\lengths.pdf")

    fig, ax = plt.subplots()
    ax.set_title("Fraction of Habitat Power")
    ax.set_xlabel("Habitat Power [W]")
    ax.set_ylabel("Fraction of Habitat Power []")
    ax.loglog()
    print("\nFraction of Habitat Power []")
    plot("hullPower", "Hull Transmission")
    plot("lightPower", "Lighting", "light", True, "--")
    plot("electricPower", "Electricity", "", True, ":")
    plot("lightCollection.lightAbsPower", "Light Absorption", "light", True, "--")
    plot("emission.radiatorPower", "Radiator Emission", "cool")
    plot("lightCollection.windowCoolingPower", "Window Cooling", "light", True, "--")
    plot("lightCollection.windowToHabPower", "Heating of Habitat by Windows", "light", True, "--")
    plot("absorption.absorptionFrictionPower", "Absorption Friction", "cool", True, ":")
    plot("connection.connectionFrictionPower", "Connection Friction", "cool", True, ":")
    plot("emission.emissionFrictionPower", "Emission Friction", "cool", True, ":")
    ax.legend()
    fig.savefig(inp.project + "\\powers.pdf")

    if inp.numberRuns > 1:  # for different parameters
        def getLinestyle():
            if iRun == 0:
                return "-"
            elif iRun == 1:
                return "--"
            else:
                return ":"

        fig, ax = plt.subplots()
        ax.set_title("Ratio of total Cooling Mass to Habitat Power")
        ax.set_xlabel("Habitat Power [W]")
        ax.set_ylabel("Mass per Power [kg/W]")
        ax.loglog()
        print("\nCooling Mass per Power [kg/W]")
        for iRun in range(inp.numberRuns):
            results = runResults[iRun]
            plot("totalCoolingMass", "Cooling Mass " + inp.label[iRun], "cool", True, getLinestyle())
        ax.legend()
        fig.savefig(inp.project + "\\totalCoolingMass.pdf")

        fig, ax = plt.subplots()
        ax.set_title("Optimized Friction")
        ax.set_xlabel("Habitat Power [W]")
        ax.set_ylabel("Ratio of Friction to Cooling Power []")
        ax.loglog()
        print("\nFriction to Cooling Power")
        for iRun in range(inp.numberRuns):
            results = runResults[iRun]
            plot("absFriction", "Absorption " + inp.label[iRun], "cool", False, getLinestyle())
            plot("conFriction", "Connection " + inp.label[iRun], "cool", False, getLinestyle())
            plot("emFriction", "Emission " + inp.label[iRun], "cool", False, getLinestyle())
        ax.legend()
        fig.savefig(inp.project + "\\optimizedFriction.pdf")

        fig, ax = plt.subplots()
        ax.set_title("Ratio of Volume to Habitat Power")
        ax.set_xlabel("Habitat Power [W]")
        ax.set_ylabel("Volume per Power [m³/W]")
        ax.loglog()
        print("\nVolume per Power [m³/W]")
        results = runResults[0]
        plot("shape.habVolume", "Habitat")
        plot("shape.hullVolume", "Hull")
        plot("lightCollection.lightVolume", "Light Channels", "light")
        for iRun in range(inp.numberRuns):
            results = runResults[iRun]
            plot("absorption.absorptionVolume", "Absorption " + inp.label[iRun], "cool", True, getLinestyle())
            plot("connection.connectionVolume", "Connection " + inp.label[iRun], "cool", True, getLinestyle())
            plot("emission.emissionVolume", "Emission " + inp.label[iRun], "cool", True, getLinestyle())
        ax.legend()
        fig.savefig(inp.project + "\\volumes.pdf")

    for iRun in range(inp.numberRuns):
        print("\n"+inp.label[iRun])
        results = runResults[iRun]
        for res in results:
            if not res.isCoolingPossible:
                print("No complete cooling above %.2e W" % res.habPower)
                break
        for res in results:
            if not res.isCompleteLighting:
                print("No complete lighting above %.2e W" % res.habPower)
                break
        print("Hull : %.2e kg/W" % (results[0].shape.hullMass / results[0].habPower))
        print("Habitat Interior %.2e kg/W" % (results[0].shape.interiorMass / results[0].habPower))
        print("Electricity Generation %.2e kg/W" % (results[0].electricMass / results[0].habPower))
        print("Light Collection %.2e kg/W" % (results[0].lightCollection.lightMass / results[0].habPower))
        print("Total Cooling %.2e kg/W" % (results[0].totalCoolingMass / results[0].habPower))
        print("Light channels %.2e of habitat volume" % (results[0].lightCollection.lightVolume / results[0].shape.habVolume))
        print("Cooling %.2e of habitat volume" % results[0].connection.coolantVolumeFraction)
    plt.show()
