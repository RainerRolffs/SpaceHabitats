# The input parameters are defined here

from helpers import ShapeType, LogRange, CoolantType


class Input:

    project = "default"  # a directory of this name is created, containting input.py and the result figures (in case of computing more than one power)

    # Habitat:
    powers = LogRange(numberOfModels=100, minPower=1e3, maxPower=1e18)  # list of habitat powers to be computed
    # set to [power] to compute only one power; (can be overriden by command-line argument "--power" or "--volume")
    powerPerVolume = 25  # power density (total electric and lighting consumption per habitat volume) [W/m**3]
    # (overriden if both "--power" and "--volume" are given)
    interiorMassPerPower = 2.5  # [kg/W]
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
    maxGravity = 10  # [m/s²]

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
    maxRadiatorToHabRadius = 2   # maximum ratio of radiator radius to habitat radius
    maxRadiatorToCorotRadius = 1   # maximum ratio of radiator radius to co-rotational radius

    # Friction:
    pumpEfficiency = 0.8  # efficiency of pump or fan
    minFrictionFactor = 0.005  # assumed minimum friction factor at very high Reynolds
    isFrictionOptimized = True  # if friction fractions are optimized or fixed
    absorptionFrictionFraction = 0.01  # fraction of the habitat power devoted to overcome friction in heat absorption (not for Air)
    connectionFrictionFraction = 0.01  # fraction of the habitat power devoted to overcome friction in heat connection
    emissionFrictionFraction = 0.01  # fraction of the habitat power devoted to overcome friction in heat emission
    maxFrictionFraction = 0.5  # maximum fraction of the habitat power devoted to overcome friction

    # multiple runs:
    numberRuns = 3
    label = ["Liquid"]
    iRun = 0

    def changeParameters(self, iRun):
        self.iRun = iRun
        if iRun == 1:
            self.coolantType = CoolantType.Air
            self.label.append("Air")
        elif iRun == 2:
            self.coolantType = CoolantType.Vapor
            self.label.append("Vapor")

    def getIrradiation(self):
        return 1360 / self.solarDistance ** 2 * (1 - self.shadedFraction)
