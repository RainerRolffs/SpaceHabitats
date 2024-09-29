# The input parameters are defined here

from helpers import ShapeType, LogRange, CoolantType


class Input:

    project = "default"  # a directory of this name is created, containing a copy of this input.py (and figures, if set in output.py)

    # Habitat:
    population = LogRange(numberOfModels=500, minValue=1e3/4e4, maxValue=1e18/4e4)  # [people], can be a number or list of numbers
    # (can be overriden by command-line arguments "--power", "--volume", or "--population")
    volumePerPerson = 1600  # [m³]
    powerPerPerson = 4e4  # [W]
    interiorMassPerPerson = 1e5  # [kg]
    insidePowerFraction = 1  # fraction of the habitat power inside the shielding

    # Geometry
    shapeType = ShapeType.Cylinder
    cylinderLengthToRotRadius = 1.3  # for Cylinder
    tubeRadiusToRotRadius = 0.1  # for Tube and DumbbellTube
    oblateMinorToRotRadius = 1  # for Oblate
    torusHabToRotRadius = 0.25  # for Torus
    dumbbellMinorToRotRadius = 0.1  # for Dumbbell and DumbbellTube
    dumbbellMajorToMinorRadius = 1  # for Dumbbell and DumbbellTube

    # Gravity Distribution
    constantFloorHeight = 5  # part that is independent of radius [m]
    variableFloorHeight = 5  # part that grows with lower gravity [m]

    # Structural Integrity
    stressPerDensity = 1e5  # tensile stress per density of structural material [Nm/kg]
    airPressure = 0.4  # [bar=1e5Pa]
    maxGravity = 9.81  # [m/s²]
    distanceBetweenVerticalCables = 10  # [m]
    bridgeThickness = 1  # [m]

    # Energy Collection:
    solarDistance = 1  # distance to the Sun [AU=1.5e11m]
    shadedFraction = 0  # fraction of shading
    electricFraction = 0.25  # of habitat power
    electricEfficiency = 0.2  # efficiency of converting sunlight to electricity
    electricSurfaceDensity = 5  # [kg/m**2]
    concentrationFactor = 400
    outerReflectivity = 0.5  # of primary mirrors
    windowReflectivity = 0.3
    windowAbsorptivity = 0.05
    maxWindowTemperature = 500
    innerReflectivity = 0.99  # of channel mirrors
    surfaceIntensity = 500  # [W/m**2]
    lightSurfaceDensity = 1  # average surface density in light collectiom [kg/m**2]
    maxLightVolumeFraction = 0.2  # max. fraction of the habitat volume occupied by light channels
    maxCollectionToCoRotRadius = 1   # maximum size of the co-rotating collection system, as ratio of radius to co-rotational radius

    # Hull:
    hullSurfaceDensity = 5000  # [kg/m**2]
    hullDensity = 1000  # [kg/m**3]
    hullConductivity = 1  # [W/Km]
    hullSurfaceAbsorptivity = 0  # absorptivity of the outer hull surface
    gapThickness = 0.1  # [m]
    gapLocation = 0.1  # fraction of hull from the inside
    innerGapEmissivity = 0.9  #
    outerGapEmissivity = 0.9  #
    gapTransferCoeff = 5  # [W/Km**2]
    gapConductivity = 0.01  # [W/Km]

    # Coolant:
    coolantType = CoolantType.Liquid
    liquidDensity = 1000  # [kg/m**3] (only for Liquid)
    liquidHeatCapacity = 4280  # [J/kgK] (only for Liquid)
    vaporLatentHeat = 2.453e6  # [J/kg] (only for Vapor)

    # Habitat Temperature:
    minHabTemp = 273 + 12  # [K]
    maxHabTemp = 273 + 27  # [K]

    # Heat Absorption (Liquid and Vapor):
    tempDiffFlow = 20  # temperature difference between entering and leaving flow [K]
    minTempDiffHabCoolant = 5  # minimum temperature difference between habitat and coolant temperature [K]
    absorptionTransferCoeff = 20  # heat transfer coefficient between habitat air and cooling pipes [W/Km**2]
    absorptionSurfaceDensity = 3  # [kg/m**2]
    maxCoolantVolumeFraction = 0.2  # max. fraction of the habitat volume occupied by coolant

    # Heat Absorption (Air):
    outgoingRelativeHumidity = 0.8  # relative humidity of outgoing air
    innerSurfacePerPower = 0.01  # [m**2/W]
    windyVolumeFraction = 0.25  # fraction of the habitat volume occupied by airflow

    # Heat Emission:
    emissivity = 0.9  # emissivity of the radiator
    skyTemp = 3  # average temperature of counter-radiation [K]
    emissionSurfaceDensity = 5  # [kg/m**2]
    maxRadiatorToRotRadius = 2   # maximum ratio of radiator radius to rotational radius
    maxRadiatorToCorotRadius = 1   # maximum ratio of radiator radius to co-rotational radius

    # Friction:
    pumpEfficiency = 0.8  # efficiency of pump or fan
    minFrictionFactor = 0.005  # assumed minimum friction factor at very high Reynolds
    isFrictionOptimized = False  # if friction fractions are optimized or fixed
    absorptionFrictionFraction = 0.01  # fraction of the habitat power devoted to overcome friction in heat absorption (not for Air)
    connectionFrictionFraction = 0.01  # fraction of the habitat power devoted to overcome friction in heat connection
    emissionFrictionFraction = 0.01  # fraction of the habitat power devoted to overcome friction in heat emission
    maxFrictionFraction = 0.5  # maximum fraction of the habitat power devoted to overcome friction

    # multiple runs:
    numberRuns = 1  # set e.g. to 6 to compute examples with changeParameters
    iRun = 0  # initialized
    label = []  # initialized

    def changeParameters(self, iRun):  # only used if numberRuns > 1
        self.iRun = iRun
        self.hullSurfaceDensity = 5000
        if iRun == 0:
            self.hullSurfaceDensity = 500
            self.population = 1
            self.shapeType = ShapeType.Dumbbell
            self.label.append("XS - Dumbbell")
        elif iRun == 1:
            self.population = 100
            self.shapeType = ShapeType.Tube
            self.label.append("S - Tube")
        elif iRun == 2:
            self.population = 1e4
            self.shapeType = ShapeType.Torus
            self.label.append("M - Torus")
        elif iRun == 3:
            self.population = 1e6
            self.shapeType = ShapeType.DumbbellTube
            self.dumbbellMajorToMinorRadius = 2 ** (1/3)
            self.label.append("L - Asymmetric Dumbbell with Tube")
        elif iRun == 4:
            self.population = 1e8
            self.shapeType = ShapeType.Cylinder
            self.label.append("XL - Cylinder")
        elif iRun == 5:
            self.population = 6e6
            self.shapeType = ShapeType.Oblate
            self.label.append("Lowest mass - Sphere")

    def getIrradiation(self):
        return 1360 / self.solarDistance ** 2 * (1 - self.shadedFraction)
