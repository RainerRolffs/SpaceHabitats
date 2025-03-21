﻿# model results are plotted here

import matplotlib.pyplot as plt

from habitat import Habitat
from input import Input
from sketch import Sketch


class Output:
    showFigures = True  # if figures are shown
    saveFigures = False  # if figures are saved in the project directory
    printOnlyShortResults = False  # if a short version of the results is printed

    def __init__(self, inp: Input, runResults: [[Habitat]]):
        self.inp = inp
        self.runResults = runResults
        self.habitats = runResults[0]
        self.firstHab = self.habitats[0]
        self.xvals = [hab.habPower for hab in self.habitats]

        self.printResultsForFirstPower()

        if inp.population.__class__ is not list:

            self.showSketchForFirstPower(onlyFirstRun=False)
            self.showGravityForFirstPower(normalizedToGravWidth=False, onlyFirstRun=False, withVolume=False, withHull=False)
            self.showGravityForFirstPower(True, True, True, True)

        else:

            self.plot_Mass()
            self.plot_Area()
            self.plot_Length()
            self.plot_PowerFraction()
            self.plot_StructuralMass()
            self.plot_MassPerVolume()

            if inp.numberRuns > 1:  # for different parameters
                self.plot_CoolingMasses()
                self.plot_Frictions()
                self.plot_Volumes()
                self.plot_HullAndStructuralMasses()

            self.print_Limits()

        if self.showFigures:
            plt.show()

    def printResultsForFirstPower(self):
        for res in self.runResults:
            hab = res[0]
            print("\nFirst size (%.2e W, %.2e m³, %.2e people)" % (hab.habPower, hab.shape.habVolume, hab.population))
            if self.inp.numberRuns > 1:
                print(" of model run #" + str(hab.iRun) + " " + self.inp.label[hab.iRun] + ":")

            print("Hull Mass %.2e kg" % hab.shape.hullMass)
            print("Structural Mass %.2e kg" % hab.structure.totalStructuralMass)
            print("Rotational Radius %.2f m" % hab.shape.rotationalRadius)
            print("Number of floors %i" % hab.gravity.numberFloors)
            print("Average Ground Gravity %.2f m/s^2" % hab.gravity.averageGroundGravity)
            if self.printOnlyShortResults:
                continue

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

            print("\nTotal Mass %.2e kg" % hab.totalMass)
            print("Hull Mass %.2e kg" % hab.shape.hullMass)
            print("Habitat Interior %.2e kg" % hab.shape.interiorMass)
            print("\t Air %.2e kg" % hab.shape.airMass)
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
            print("Total Structural %.2e kg" % hab.structure.totalStructuralMass)
            print("\t Pressure Containment %.2e kg" % hab.structure.pressureStructuralMass)
            print("\t Interior Support %.2e kg" % hab.structure.interiorStructuralMass)
            print("\t Hull Support %.2e kg" % hab.structure.hullStructuralMass)
            print("\t Radiator Support %.2e kg" % hab.structure.radiatorStructuralMass)
            print("\t Mirror Support %.2e kg" % hab.structure.lightStructuralMass)
            print("\t Electric Support %.2e kg" % hab.structure.electricStructuralMass)

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

            if hab.lightCollection.isUnconcentratedLightingPossible:
                print("Unconcentrated lighting is possible.")
            if not hab.isCompleteLighting:
                print("Complete lighting not possible (would take up too much space)")
            if hab.structure.coRotationalLightFraction < 1:
                print("No complete co-rotation of mirrors")

            if hab.insidePower == hab.hullPower:
                print("Natural cooling is possible.")
            if not hab.isCoolingPossible:
                print("Cooling of the habitat is not possible! - " + hab.coolingReport)

            print("Cooling %.2e of habitat volume" % hab.connection.coolantVolumeFraction)

            print("Hull : %.2e kg/person" % (hab.shape.hullMass / hab.population))
            print("Habitat Interior %.2e kg/person" % (hab.shape.interiorMass / hab.population))
            print("Electricity Generation %.2e kg/person" % (hab.electricMass / hab.population))
            print("Light Collection %.2e kg/person" % (hab.lightCollection.lightMass / hab.population))
            print("Total Cooling %.2e kg/person" % (hab.totalCoolingMass / hab.population))
            print("Light channels %.2e of habitat volume" % (hab.lightCollection.lightVolume / hab.shape.habVolume))
            print("Cooling %.2e of habitat volume" % hab.connection.coolantVolumeFraction)

    def showCurve(self, ax, y: str, lab: str, cont="", perPower=True, lstyle="-"):
        yvals = []
        for hab in self.habitats:
            if ((cont == "cool") and hab.isCoolingPossible) or (cont == "light") or (cont == ""):
                if "." in y:
                    yvals.append(getattr(getattr(hab, y.split(".")[0]), y.split(".")[1]))
                else:
                    yvals.append(getattr(hab, y))
                if perPower:
                    yvals[-1] /= hab.habPower
        ax.plot(self.xvals[:len(yvals)], yvals, label=lab, linestyle=lstyle)
        if len(yvals) > 0:
            print(lab + ": %.2e" % yvals[0])

    def plot_Mass(self):
        fig, ax = plt.subplots()
        ax.set_title("Ratio of Mass to Habitat Power")
        ax.set_xlabel("Habitat Power [W]")
        ax.set_ylabel("Mass per Power [kg/W]")
        ax.loglog()
        print("\nMass per Power [kg/W] at %.2e W" % self.xvals[0])
        self.showCurve(ax, "shape.hullMass", "Hull")
        self.showCurve(ax, "shape.interiorMass", "Habitat Interior")
        self.showCurve(ax, "electricMass", "Electricity Generation")
        self.showCurve(ax, "lightCollection.lightMass", "Light Collection", "light")
        self.showCurve(ax, "totalCoolingMass", "Total Cooling", "cool")
        self.showCurve(ax, "absorption.absorptionSurfaceMass", "Absorption Surface", "cool", True, "--")
        self.showCurve(ax, "emission.emissionSurfaceMass", "Emission Surface", "cool", True, "--")
        self.showCurve(ax, "connection.connectionSurfaceMass", "Connection Surface", "cool", True, "--")
        self.showCurve(ax, "absorption.absorptionCoolantMass", "Absorption Coolant", "cool", True, ":")
        self.showCurve(ax, "connection.connectionCoolantMass", "Connection Coolant", "cool", True, ":")
        self.showCurve(ax, "electricCoolingMass", "Additional Electricity", "cool", True, "--")
        self.showCurve(ax, "emission.emissionCoolantMass", "Emission Coolant", "cool", True, ":")
        self.showCurve(ax, "structure.totalStructuralMass", "Structure")
        ax.legend()
        if self.saveFigures:
            fig.savefig(self.inp.project + "\\masses.pdf")

    def plot_Area(self):
        fig, ax = plt.subplots()
        ax.set_title("Ratio of Area to Habitat Power")
        ax.set_xlabel("Habitat Power [W]")
        ax.set_ylabel("Area per Power [m²/W]")
        ax.loglog()
        print("\nArea per Power [m²/W]")
        self.showCurve(ax, "shape.hullSurface", "Hull Surface")
        self.showCurve(ax, "lightCollection.lightCollectionArea", "Light Collection", "light", True, "--")
        self.showCurve(ax, "lightCollection.lightChannelSurface", "Light Channels", "light")
        self.showCurve(ax, "electricArea", "Electricity Generation", "", True, "--")
        self.showCurve(ax, "absorption.absorptionSurface", "Absorption Surface", "cool")
        self.showCurve(ax, "emission.emissionSurface", "Emission Surface", "cool")
        self.showCurve(ax, "connection.connectionSurface", "Connection Surface", "cool")
        self.showCurve(ax, "lightCollection.windowArea", "Windows", "light")
        self.showCurve(ax, "emission.emissionCrossSection", "Emission Cross Section", "cool", True, "--")
        self.showCurve(ax, "absorption.absorptionCrossSection", "Absorption Cross Section", "cool", True, "--")
        self.showCurve(ax, "connection.connectionCrossSection", "Connection Cross Section", "cool", True, "--")
        ax.legend()
        if self.saveFigures:
            fig.savefig(self.inp.project + "\\surfaces.pdf")

    def plot_Length(self):
        fig, ax = plt.subplots()
        ax.set_title("Ratio of Length to Habitat Power")
        ax.set_xlabel("Habitat Power [W]")
        ax.set_ylabel("Length per Power [m/W]")
        ax.loglog()
        print("\nLength per Power [m/W]")
        self.showCurve(ax, "shape.rotationalRadius", "Rotational Radius")
        self.showCurve(ax, "structure.coRotationalRadius", "Critical Co-Rotational Radius")
        self.showCurve(ax, "effectiveHabRadius", "Habitat Radius")
        self.showCurve(ax, "collectionRadius", "Energy Collection Radius", "light")
        self.showCurve(ax, "connection.emissionLength", "Emission Length", "cool")
        self.showCurve(ax, "emission.emissionRadius", "Emission Radius", "cool")
        self.showCurve(ax, "connection.totalLength", "Total Connection", "cool")
        ax.legend()
        if self.saveFigures:
            fig.savefig(self.inp.project + "\\lengths.pdf")

    def plot_PowerFraction(self):
        fig, ax = plt.subplots()
        ax.set_title("Fraction of Habitat Power")
        ax.set_xlabel("Habitat Power [W]")
        ax.set_ylabel("Fraction of Habitat Power []")
        ax.loglog()
        print("\nFraction of Habitat Power []")
        self.showCurve(ax, "hullPower", "Hull Transmission")
        self.showCurve(ax, "lightPower", "Lighting", "light", True, "--")
        self.showCurve(ax, "electricPower", "Electricity", "", True, ":")
        self.showCurve(ax, "lightCollection.lightAbsPower", "Light Absorption", "light", True, "--")
        self.showCurve(ax, "emission.radiatorPower", "Radiator Emission", "cool")
        self.showCurve(ax, "lightCollection.windowCoolingPower", "Window Cooling", "light", True, "--")
        self.showCurve(ax, "lightCollection.windowToHabPower", "Heating of Habitat by Windows", "light", True, "--")
        self.showCurve(ax, "absorption.absorptionFrictionPower", "Absorption Friction", "cool", True, ":")
        self.showCurve(ax, "connection.connectionFrictionPower", "Connection Friction", "cool", True, ":")
        self.showCurve(ax, "emission.emissionFrictionPower", "Emission Friction", "cool", True, ":")
        ax.legend()
        if self.saveFigures:
            fig.savefig(self.inp.project + "\\powers.pdf")

    def plot_StructuralFraction(self):
        fig, ax = plt.subplots()
        ax.set_title("Structural Mass")
        ax.set_xlabel("Habitat Power [W]")
        ax.set_ylabel("Fraction of Component Mass []")
        ax.loglog()
        print("\nFraction of Component Mass []")
        ax.plot(self.xvals, [hab.structure.pressureStructuralMass / hab.structure.pressureReferenceMass for hab in self.habitats], label="Air & Coolant", linestyle="-")
        print("\t Air" + ": %.2e" % (self.habitats[0].structure.pressureStructuralMass / self.habitats[0].structure.pressureReferenceMass))
        ax.plot(self.xvals, [hab.structure.interiorFraction for hab in self.habitats], label="Interior", linestyle="-")
        print("\t Interior" + ": %.2e" % self.habitats[0].structure.interiorFraction)
        ax.plot(self.xvals, [hab.structure.hullFraction for hab in self.habitats], label="Hull", linestyle="-")
        print("\t Hull" + ": %.2e" % self.habitats[0].structure.hullFraction)
        ax.plot(self.xvals, [hab.structure.radiatorFraction for hab in self.habitats], label="Radiator", linestyle="-")
        print("\t Radiator" + ": %.2e" % self.habitats[0].structure.radiatorFraction)
        ax.plot(self.xvals, [hab.structure.lightFraction for hab in self.habitats], label="Light", linestyle="-")
        print("\t Light" + ": %.2e" % self.habitats[0].structure.lightFraction)
        ax.plot(self.xvals, [hab.structure.electricFraction for hab in self.habitats], label="Electric", linestyle="-")
        print("\t Electric" + ": %.2e" % self.habitats[0].structure.electricFraction)
        ax.legend()
        if self.saveFigures:
            fig.savefig(self.inp.project + "\\structuralFractions.pdf")

    def plot_StructuralMass(self):
        xvals = [hab.shape.habVolume for hab in self.habitats]

        fig, ax = plt.subplots()
        ax.set_title("Structural mass components")
        ax.set_xlabel("Interior Volume [m³]")
        ax.set_ylabel("Mass per Volume [kg/m³]")
        ax.loglog()

        self.AxisForPopulation(ax)

        ax.plot(xvals, [hab.structure.pressureStructuralMass / hab.shape.habVolume for hab in self.habitats], label="Pressure Containment", linestyle="-", color="magenta")
        ax.plot(xvals, [hab.structure.pressureReferenceMass / hab.shape.habVolume for hab in self.habitats], label="Air & Coolant", linestyle="--", color="magenta")

        ax.plot(xvals, [hab.structure.interiorStructuralMass / hab.shape.habVolume for hab in self.habitats], label="Interior Support", linestyle="-", color="green")
        ax.plot(xvals, [hab.structure.interiorReferenceMass / hab.shape.habVolume for hab in self.habitats], label="Interior & Absorption Cooling", linestyle="--", color="green")

        ax.plot(xvals, [hab.structure.hullStructuralMass / hab.shape.habVolume for hab in self.habitats], label="Hull Support", linestyle="-", color="red")
        ax.plot(xvals, [hab.structure.hullReferenceMass / hab.shape.habVolume for hab in self.habitats], label="Hull", linestyle="--", color="red")

        ax.plot(xvals, [hab.structure.radiatorStructuralMass / hab.shape.habVolume for hab in self.habitats], label="Radiator Support", linestyle="-", color="black")
        ax.plot(xvals, [hab.structure.radiatorReferenceMass / hab.shape.habVolume for hab in self.habitats], label="Radiator", linestyle="--", color="black")

        ax.plot(xvals, [hab.structure.lightStructuralMass / hab.shape.habVolume for hab in self.habitats], label="Mirror Support", linestyle="-", color="yellow")
        ax.plot(xvals, [hab.structure.lightReferenceMass / hab.shape.habVolume for hab in self.habitats], label="Co-rotating Mirrors", linestyle="--", color="yellow")

        ax.plot(xvals, [hab.structure.electricStructuralMass / hab.shape.habVolume for hab in self.habitats], label="PV Support", linestyle="-", color="blue")
        ax.plot(xvals, [hab.structure.electricReferenceMass / hab.shape.habVolume for hab in self.habitats], label="Co-rotating PV", linestyle="--", color="blue")

#        ax.plot(xvals, [hab.structure.totalStructuralMass / hab.shape.habVolume for hab in self.habitats], label="Total Structural", linestyle="-", color="orange")
#        ax.plot(xvals, [hab.structure.totalReferenceMass / hab.shape.habVolume for hab in self.habitats], label="Total Reference", linestyle="--", color="orange")

        plt.subplots_adjust(right=0.6)
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        if self.saveFigures:
            fig.savefig(self.inp.project + "\\structuralMasses.pdf")

    def AxisForPopulation(self, ax):
        # Create a secondary x-axis
        secax = ax.secondary_xaxis('top', functions=(lambda x: x / self.inp.volumePerPerson, lambda x: x * self.inp.volumePerPerson))
        secax.set_xscale('log')  # Set secondary x-axis to logarithmic scale
        secax.set_xlabel('Population')

        plt.subplots_adjust(top=0.85)  # Increase top margin to fit the title if using a tight layout


    def plot_MassPerVolume(self):
        xvals = [hab.shape.habVolume for hab in self.habitats]

        fig, ax = plt.subplots()
        ax.set_title("Main mass components")
        ax.set_xlabel("Interior Volume [m³]")
        ax.set_ylabel("Mass per Volume [kg/m³]")
        ax.loglog()
        self.AxisForPopulation(ax)

        ax.plot(xvals, [hab.shape.interiorMass / hab.shape.habVolume for hab in self.habitats], label="Interior", linestyle="-", color="green")
        ax.plot(xvals, [hab.shape.hullMass / hab.shape.habVolume for hab in self.habitats], label="Hull", linestyle="-", color="red")
        ax.plot(xvals, [hab.totalCoolingMass / hab.shape.habVolume for hab in self.habitats], label="Cooling", linestyle="-", color="blue")
        ax.plot(xvals, [hab.structure.totalStructuralMass / hab.shape.habVolume for hab in self.habitats], label="Structural", linestyle="-", color="orange")
        ax.plot(xvals, [hab.totalMass / hab.shape.habVolume for hab in self.habitats], label="Total Habitat", linestyle=":", color="black")
        plt.subplots_adjust(right=0.75)
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        if self.saveFigures:
            fig.savefig(self.inp.project + "\\massPerVolume.pdf")

    @staticmethod
    def getLinestyle(iRun: int):
        if iRun == 0:
            return "-"
        elif iRun == 1:
            return "--"
        else:
            return ":"

    def plot_CoolingMasses(self):
        fig, ax = plt.subplots()
        ax.set_title("Ratio of total Cooling Mass to Habitat Power")
        ax.set_xlabel("Habitat Power [W]")
        ax.set_ylabel("Mass per Power [kg/W]")
        ax.loglog()
        print("\nCooling Mass per Power [kg/W]")
        for iRun in range(self.inp.numberRuns):
            self.showCurve(ax, "totalCoolingMass", "Cooling Mass " + self.inp.label[iRun], "cool", True, self.getLinestyle(iRun))
        ax.legend()
        if self.saveFigures:
            fig.savefig(self.inp.project + "\\totalCoolingMass.pdf")

    def plot_Frictions(self):
        fig, ax = plt.subplots()
        ax.set_title("Optimized Friction")
        ax.set_xlabel("Habitat Power [W]")
        ax.set_ylabel("Ratio of Friction to Cooling Power []")
        ax.loglog()
        print("\nFriction to Cooling Power")
        for iRun in range(self.inp.numberRuns):
            habitats = self.runResults[iRun]
            self.showCurve(ax, "absFriction", "Absorption " + self.inp.label[iRun], "cool", False, self.getLinestyle(iRun))
            self.showCurve(ax, "conFriction", "Connection " + self.inp.label[iRun], "cool", False, self.getLinestyle(iRun))
            self.showCurve(ax, "emFriction", "Emission " + self.inp.label[iRun], "cool", False, self.getLinestyle(iRun))
        ax.legend()
        if self.saveFigures:
            fig.savefig(self.inp.project + "\\optimizedFriction.pdf")

    def plot_Volumes(self):
        fig, ax = plt.subplots()
        ax.set_title("Ratio of Volume to Habitat Power")
        ax.set_xlabel("Habitat Power [W]")
        ax.set_ylabel("Volume per Power [m³/W]")
        ax.loglog()
        print("\nVolume per Power [m³/W]")
        habitats = self.runResults[0]
        self.showCurve(ax, "shape.habVolume", "Habitat")
        self.showCurve(ax, "shape.hullVolume", "Hull")
        self.showCurve(ax, "lightCollection.lightVolume", "Light Channels", "light")
        for iRun in range(self.inp.numberRuns):
            habitats = self.runResults[iRun]
            self.showCurve(ax, "absorption.absorptionVolume", "Absorption " + self.inp.label[iRun], "cool", True, self.getLinestyle(iRun))
            self.showCurve(ax, "connection.connectionVolume", "Connection " + self.inp.label[iRun], "cool", True, self.getLinestyle(iRun))
            self.showCurve(ax, "emission.emissionVolume", "Emission " + self.inp.label[iRun], "cool", True, self.getLinestyle(iRun))
        ax.legend()
        if self.saveFigures:
            fig.savefig(self.inp.project + "\\volumes.pdf")

    def print_Limits(self):
        for iRun in range(self.inp.numberRuns):
            if self.inp.numberRuns > 1:
                print("\n" + self.inp.label[iRun]+":")
            habitats = self.runResults[iRun]
            for res in habitats:
                if res.shape.hullMass < res.shape.interiorMass:
                    print("Hull mass is larger than interior mass (%.1e kg) below pop. %.1e / %.1e m³ / %.1e W" % (res.shape.interiorMass, res.population, res.shape.habVolume, res.habPower))
                    break
            for res in habitats:
                if res.structure.rotationRate_rpm < 3:
                    print("Rotational rate is larger than 3rpm below pop. %.1e / %.1e m³ / %.1e W" % (res.population, res.shape.habVolume, res.habPower))
                    break

            for res in habitats:
                if res.insidePower > res.hullPower:
                    print("No natural cooling above pop. %.1e / %.1e m³ / %.1e W" % (res.population, res.shape.habVolume, res.habPower))
                    break

            for res in habitats:
                if not res.isCoolingPossible:
                    print("No complete cooling above pop. %.1e / %.1e m³ / %.1e W - %s" % (res.population, res.shape.habVolume, res.habPower, res.coolingReport))
                    break
            for res in habitats:
                if res.structure.coRotationalElectricFraction < 1:
                    print("No complete co-rotation of PV above pop. %.1e / %.1e m³ / %.1e W" % (res.population, res.shape.habVolume, res.habPower))
                    break
            for res in habitats:
                if res.structure.coRotationalLightFraction < 1:
                    print("No complete co-rotation of mirrors above pop. %.1e / %.1e m³ / %.1e W" % (res.population, res.shape.habVolume, res.habPower))
                    break

            for res in habitats:
                if not res.isCompleteLighting:
                    print("No complete lighting above pop. %.1e / %.1e m³ / %.1e W - %s" % (res.population, res.shape.habVolume, res.habPower, res.lightingReport))
                    break
            for res in habitats:
                if res.shape.rotationalRadius > res.structure.coRotationalRadius:
                    print("Rotational radius surpasses critical co-rotational radius at pop. %.1e / %.1e m  %.1e m³ / %.1e W" % (res.population, res.shape.rotationalRadius, res.shape.habVolume, res.habPower))
                    break
            for res in habitats:
                if res.totalCoolingMass > res.shape.interiorMass:
                    print("Cooling mass surpasses the interior mass at pop. %.1e / %.1e m³ / %.1e W" % (res.population, res.shape.habVolume, res.habPower))
                    break

            for res in habitats:
                if res.structure.totalStructuralMass > res.shape.hullMass:
                    print("Structural mass surpasses hull mass at pop. %.1e / %.1e m³ / %.1e W" % (res.population, res.shape.habVolume, res.habPower))
                    break
            for res in habitats:
                if res.structure.totalStructuralMass > res.shape.interiorMass:
                    print("Structural mass surpasses the interior mass at pop. %.1e / %.1e m³ / %.1e W" % (res.population, res.shape.habVolume, res.habPower))
                    break
            oldInteriorMassFraction = 0
            for res in habitats:
                interiorMassFraction = res.shape.interiorMass / res.totalMass
                if interiorMassFraction < oldInteriorMassFraction:
                    print(s)
                    break
                else:
                    oldInteriorMassFraction = interiorMassFraction
                    s = "Maximum interior mass fraction (%.3f) / minimum mass per volume at pop. %.1e / %.1e m³ / %.1e W" % (interiorMassFraction, res.population, res.shape.habVolume, res.habPower)

    def plot_HullAndStructuralMasses(self):
        fig, ax = plt.subplots()
        ax.set_title("Hull and Structural Mass for different shapes")
        ax.set_xlabel("Interior Volume [m³]")
        ax.set_ylabel("Mass per Volume [kg/m³]")
        ax.loglog()
        xvals = [hab.shape.habVolume for hab in self.runResults[0]]
        for iRun in range(self.inp.numberRuns):
            results = self.runResults[iRun]
            ax.plot(xvals, [hab.shape.hullMass / hab.shape.habVolume for hab in results], label="Hull " + self.inp.label[iRun], linestyle="-")
            ax.plot(xvals, [hab.structure.totalStructuralMass / hab.shape.habVolume for hab in results], label="Structure " + self.inp.label[iRun], linestyle=":")
    
        ax.legend()
        if self.saveFigures:
            fig.savefig(self.inp.project + "\\HullAndStructuralMasses.pdf")

    def showSketchForFirstPower(self, onlyFirstRun: bool):
        for iRun in range(self.inp.numberRuns):
            if onlyFirstRun and iRun > 0:
                break
            hab = self.runResults[iRun][0]
            sketch = Sketch(shape=hab.shape, corot_limit=hab.structure.coRotationalRadius,
                   light_radius=hab.lightRadius, collection_radius=hab.collectionRadius, emission_radius=hab.emission.emissionRadius,
                   emission_length=hab.connection.emissionLength)
            sketch.title = self.inp.project
            if self.inp.numberRuns > 1:
                sketch.title = self.inp.label[iRun]
            sketch.show_habitat()
            if self.saveFigures:
                sketch.fig.savefig(self.inp.project + "\\sketch3d_%s.pdf" % self.inp.label[iRun])

    def showGravityForFirstPower(self, normalizedToGravWidth: bool, onlyFirstRun: bool, withVolume: bool, withHull: bool):
        fig, ax = plt.subplots()
        if not withVolume and not withHull:
            ax.set_title("Ground Gravity Distribution")
        else:
            ax.set_title("Gravity Distribution")
        ax.set_xlabel("Gravity [m/s²]")

        for iRun in range(self.inp.numberRuns):
            if onlyFirstRun and iRun > 0:
                break
            labeladdition = ""
            if not onlyFirstRun and self.inp.numberRuns > 1:
                labeladdition = self.inp.label[iRun]

            hab = self.runResults[iRun][0]
            nbFloors = len(hab.gravity.groundRadii)
            xvals = [hab.gravity.groundRadii[i] * self.inp.maxGravity / hab.shape.rotationalRadius for i in range(nbFloors)]

            if normalizedToGravWidth:
                widths = [xvals[i] - xvals[i+1] for i in range(nbFloors-1)]
                widths.append(xvals[-1])
                ax.set_ylabel("Distribution [1 / (m/s²)]")
                lstyle = '-'
            else:
                widths = [1 for i in range(nbFloors)]
                ax.set_ylabel("Distribution [fraction of ground area]")
                lstyle = '--'

            totalGround = sum(hab.gravity.groundAreas)
            if totalGround > 0:
                yvals = [hab.gravity.groundAreas[i] / totalGround / widths[i] for i in range(nbFloors)]

                if not withVolume and not withHull:
                    groundLabel = ""
                else:
                    groundLabel = "Ground "
                ax.plot(xvals, yvals, label=groundLabel+labeladdition, linestyle=lstyle, marker='x')

            xvals = [hab.gravity.floorRadii[i] * self.inp.maxGravity / hab.shape.rotationalRadius for i in range(nbFloors)]

            if withVolume:
                totalVolume = sum(hab.gravity.floorVolumes)
                yvals = [hab.gravity.floorVolumes[i] / totalVolume / widths[i] for i in range(nbFloors)]
                ax.plot(xvals, yvals, label="Volume "+labeladdition, linestyle=lstyle, marker='o')

            if withHull:
                totalHull = sum(hab.gravity.hullAreas)
                yvals = [hab.gravity.hullAreas[i] / totalHull / widths[i] for i in range(nbFloors)]
                ax.plot(xvals, yvals, label="Hull "+labeladdition, linestyle=lstyle, marker='v')

        ax.legend()
        if self.saveFigures:
            fig.savefig(self.inp.project + "\\gravity.pdf")



