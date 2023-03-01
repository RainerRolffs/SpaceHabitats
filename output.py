
# model results are plotted here

import os
import matplotlib.pyplot as plt

import input
from result import Result


def writeResults(runResults: [[Result]]):
    os.system("mkdir " + input.project)
    os.system("copy input.py " + input.project)

    def plot(y, lab, cont="", perPower=True, lstyle="-"):
        yvals = []
        for res in results:
            if ((cont == "cool") and res.isCoolingPossible) or (cont == "light") or (cont == ""):
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
    plot("hullMass", "Hull")
    plot("interiorMass", "Habitat Interior")
    plot("electricMass", "Electricity Generation")
    plot("lightMass", "Light Collection", "light")
    plot("totalCoolingMass", "Total Cooling", "cool")
    plot("absorptionSurfaceMass", "Absorption Surface", "cool", True, "--")
    plot("emissionSurfaceMass", "Emission Surface", "cool", True, "--")
    plot("connectionSurfaceMass", "Connection Surface", "cool", True, "--")
    plot("absorptionCoolantMass", "Absorption Coolant", "cool", True, ":")
    plot("connectionCoolantMass", "Connection Coolant", "cool", True, ":")
    plot("electricCoolingMass", "Additional Electricity", "cool", True, "--")
    plot("emissionCoolantMass", "Emission Coolant", "cool", True, ":")
    ax.legend()
    fig.savefig(input.project + "\\masses.pdf")

    fig, ax = plt.subplots()
    ax.set_title("Ratio of Area to Habitat Power")
    ax.set_xlabel("Habitat Power [W]")
    ax.set_ylabel("Area per Power [m²/W]")
    ax.loglog()
    print("\nArea per Power [m²/W]")
    plot("hullSurface", "Hull Surface")
    plot("lightCollectionArea", "Light Collection", "light", True, "--")
    plot("lightChannelSurface", "Light Channels", "light")
    plot("electricArea", "Electricity Generation", "", True, "--")
    plot("absorptionSurface", "Absorption Surface", "cool")
    plot("emissionSurface", "Emission Surface", "cool")
    plot("connectionSurface", "Connection Surface", "cool")
    plot("windowArea", "Windows", "light")
    plot("emissionCrossSection", "Emission Cross Section", "cool", True, "--")
    plot("absorptionCrossSection", "Absorption Cross Section", "cool", True, "--")
    plot("connectionCrossSection", "Connection Cross Section", "cool", True, "--")
    ax.legend()
    fig.savefig(input.project + "\\surfaces.pdf")

    fig, ax = plt.subplots()
    ax.set_title("Ratio of Length to Habitat Power")
    ax.set_xlabel("Habitat Power [W]")
    ax.set_ylabel("Length per Power [m/W]")
    ax.loglog()
    print("\nLength per Power [m/W]")
    plot("habRadius", "Habitat Radius")
    plot("collectionRadius", "Energy Collection Radius", "light")
    plot("emissionLength", "Emission Length", "cool")
    plot("emissionRadius", "Emission Radius", "cool")
    plot("totalLength", "Total Connection", "cool")
    ax.legend()
    fig.savefig(input.project + "\\lengths.pdf")

    fig, ax = plt.subplots()
    ax.set_title("Fraction of Habitat Power")
    ax.set_xlabel("Habitat Power [W]")
    ax.set_ylabel("Fraction of Habitat Power []")
    ax.loglog()
    print("\nFraction of Habitat Power []")
    plot("hullPower", "Hull Transmission")
    plot("lightPower", "Lighting", "light", True, "--")
    plot("electricPower", "Electricity", "", True, ":")
    plot("lightAbsPower", "Light Absorption", "light", True, "--")
    plot("radiatorPower", "Radiator Emission", "cool")
    plot("windowCoolingPower", "Window Cooling", "light", True, "--")
    plot("windowToHabPower", "Heating of Habitat by Windows", "light", True, "--")
    plot("absorptionFrictionPower", "Absorption Friction", "cool", True, ":")
    plot("connectionFrictionPower", "Connection Friction", "cool", True, ":")
    plot("emissionFrictionPower", "Emission Friction", "cool", True, ":")
    ax.legend()
    fig.savefig(input.project + "\\powers.pdf")

    if input.numberRuns > 1:  # for different parameters
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
        for iRun in range(input.numberRuns):
            results = runResults[iRun]
            plot("totalCoolingMass", "Cooling Mass " + input.label[iRun], "cool", True, getLinestyle())
        ax.legend()
        fig.savefig(input.project + "\\totalCoolingMass.pdf")

        fig, ax = plt.subplots()
        ax.set_title("Optimized Friction")
        ax.set_xlabel("Habitat Power [W]")
        ax.set_ylabel("Ratio of Friction to Cooling Power []")
        ax.loglog()
        print("\nFriction to Cooling Power")
        for iRun in range(input.numberRuns):
            results = runResults[iRun]
            plot("absFriction", "Absorption " + input.label[iRun], "cool", False, getLinestyle())
            plot("conFriction", "Connection " + input.label[iRun], "cool", False, getLinestyle())
            plot("emFriction", "Emission " + input.label[iRun], "cool", False, getLinestyle())
        ax.legend()
        fig.savefig(input.project + "\\optimizedFriction.pdf")

        fig, ax = plt.subplots()
        ax.set_title("Ratio of Volume to Habitat Power")
        ax.set_xlabel("Habitat Power [W]")
        ax.set_ylabel("Volume per Power [m³/W]")
        ax.loglog()
        print("\nVolume per Power [m³/W]")
        results = runResults[0]
        plot("habVolume", "Habitat")
        plot("hullVolume", "Hull")
        plot("lightVolume", "Light Channels", "light")
        for iRun in range(input.numberRuns):
            results = runResults[iRun]
            plot("absorptionVolume", "Absorption " + input.label[iRun], "cool", True, getLinestyle())
            plot("connectionVolume", "Connection " + input.label[iRun], "cool", True, getLinestyle())
            plot("emissionVolume", "Emission " + input.label[iRun], "cool", True, getLinestyle())
        ax.legend()
        fig.savefig(input.project + "\\volumes.pdf")

    for iRun in range(input.numberRuns):
        print("\n"+input.label[iRun])
        results = runResults[iRun]
        for res in results:
            if not res.isCoolingPossible:
                print("No complete cooling above %.2e W" % res.habPower)
                break
        for res in results:
            if not res.isCompleteLighting:
                print("No complete lighting above %.2e W" % res.habPower)
                break
        print("Hull : %.2e kg/W" % (results[0].hullMass / results[0].habPower))
        print("Habitat Interior %.2e kg/W" % (results[0].interiorMass / results[0].habPower))
        print("Electricity Generation %.2e kg/W" % (results[0].electricMass / results[0].habPower))
        print("Light Collection %.2e kg/W" % (results[0].lightMass / results[0].habPower))
        print("Total Cooling %.2e kg/W" % (results[0].totalCoolingMass / results[0].habPower))
        print("Light channels %.2e of habitat volume" % (results[0].lightVolume / results[0].habVolume))
        print("Cooling %.2e of habitat volume" % results[0].coolantVolumeFraction)
    plt.show()
