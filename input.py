# The input parameters are defined here

import helpers

project = "default"

# Habitat:
powers = helpers.LogRange(100, 1e3, 1e18)  # number of models, min. and max. habitat power; set to [power] to compute only one power
powerPerVolume = 25  # power density (total electric and lighting consumption per habitat volume) [W/m**3]
interiorMassPerPower = 2.5  # [kg/W]
aspectRatio = 1.3  # cylinder length to radius
insidePowerFraction = 1  # fraction of the habitat power inside the shielding

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
coolantType = helpers.CoolantType.Liquid
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
airPressure = 0.4  # [bar=1e5Pa]
innerSurfacePerPower = 0.01  # [m**2/W]
windyVolumeFraction = 0.25  # fraction of the habitat volume occupied by airflow

# Heat Emission:
emissivity = 0.9  # emissivity of the radiator
skyTemp = 3  # average temperature of counter-radiation [K]
emissionSurfaceDensity = 5  # [kg/m**2]
maxRadiatorToHabRadius = 2   # maximum ratio of radiator radius to habitat radius

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


def changeParameters(self, iRun):
    if iRun == 1:
        self.coolantType = helpers.CoolantType.Air
        self.label.append("Air")
    elif iRun == 2:
        self.coolantType = helpers.CoolantType.Vapor
        self.label.append("Vapor")

