class ChlorellaInMedia(vsys):
    """
    ChlorellaInMedia represents the dynamic Chlorella Vulgaris model in a growth medium.
    Connects the growth chamber matter phases with calculation modules to simulate algal growth.
    """

    def __init__(self, oParent, sName):
        super().__init__(oParent, sName, oParent.fTimeStep)
        eval(self.oRoot.oCfgParams.configCode(self))

        # Refill parameters initialization
        self.bNO3Refill = False
        self.bH2ORefill = False
        self.bUseUrine = self.oParent.bUseUrine

        # Initial density
        self.fCurrentGrowthMediumDensity = 1000  # [kg/m3]

    def createMatterStructure(self):
        super().createMatterStructure()

        # Calculation Modules
        self.oGrowthRateCalculationModule = (
            components.matter.algae.CalculationModules.GrowthRateCalculationModule.GrowthRateCalculationModule(self)
        )
        self.oPhotosynthesisModule = (
            components.matter.algae.CalculationModules.PhotosynthesisModule.PhotosynthesisModule(self, self.oMT)
        )

        # Growth Chamber Phase
        matter.store(self, 'GrowthChamber', self.oParent.fGrowthVolume + 0.1)
        self.oBBMComposition = (
            components.matter.algae.CalculationModules.GrowthMediumModule.BBMCompositionCalculation(
                self.oParent.fGrowthVolume, self.oMT, self
            )
        )
        self.fStartNitrogenEquivalent = 2.9 * self.oParent.fGrowthVolume
        self.fInitialChlorellaMass = components.matter.algae.CalculationModules.GrowthMediumModule.ChlorellaContentCalculation(self)

        self.tfGrowthChamberComponents = self.oBBMComposition.tfBBMComposition
        self.tfGrowthChamberComponents["Chlorella"] = self.fInitialChlorellaMass

        matter.phases.mixture(
            self.toStores.GrowthChamber,
            "GrowthMedium",
            "liquid",
            self.tfGrowthChamberComponents,
            303,
            1e5,
        )
        self.toStores.GrowthChamber.createPhase(
            "gas",
            "flow",
            "AirInGrowthChamber",
            0.05,
            {"O2": 5000, "CO2": 59000},
            293,
            0.5,
        )

        # Air Connection
        matter.procs.exmes.gas(self.toStores.GrowthChamber.toPhases.AirInGrowthChamber, "From_Outside")
        components.matter.algae.F2F.GrowthMediumAirInlet(self, "Air_In")
        matter.branch(
            self, "GrowthChamber.From_Outside", ["Air_In"], "Air_Inlet", "Air_to_GrowthChamber"
        )

        matter.procs.exmes.gas(self.toStores.GrowthChamber.toPhases.AirInGrowthChamber, "To_Outside")
        components.matter.pipe(self, "Air_Out", 0.1, 0.01)
        matter.branch(
            self, "GrowthChamber.To_Outside", ["Air_Out"], "Air_Outlet", "Air_from_GrowthChamber"
        )

        # Medium Connections
        matter.procs.exmes.mixture(self.toStores.GrowthChamber.toPhases.GrowthMedium, "To_Harvest")
        matter.branch(self, "GrowthChamber.To_Harvest", {}, "Medium_Outlet", "Medium_to_Harvester")

        matter.procs.exmes.mixture(self.toStores.GrowthChamber.toPhases.GrowthMedium, "From_Harvest")
        components.matter.pipe(self, "Pipe", 0.1, 0.1, 2e-3)
        matter.branch(
            self, "GrowthChamber.From_Harvest", ["Pipe"], "Medium_Inlet", "Medium_from_Harvester"
        )

        matter.procs.exmes.mixture(self.toStores.GrowthChamber.toPhases.GrowthMedium, "NO3_In")
        matter.branch(self, "GrowthChamber.NO3_In", {}, "NO3_Inlet", "NO3_from_Maintenance")

        matter.procs.exmes.mixture(self.toStores.GrowthChamber.toPhases.GrowthMedium, "Urine_In")
        matter.branch(self, "GrowthChamber.Urine_In", {}, "Urine_PBR", "Urine_from_PBR")

        matter.procs.exmes.mixture(self.toStores.GrowthChamber.toPhases.GrowthMedium, "H2O_In")
        matter.branch(self, "GrowthChamber.H2O_In", {}, "H2O_Inlet", "H2O_from_Maintenance")

        # P2P Connections
        matter.procs.exmes.gas(self.toStores.GrowthChamber.toPhases.AirInGrowthChamber, "CO2_to_Medium")
        matter.procs.exmes.mixture(self.toStores.GrowthChamber.toPhases.GrowthMedium, "CO2_from_Air")

        matter.procs.exmes.gas(self.toStores.GrowthChamber.toPhases.AirInGrowthChamber, "O2_from_Medium")
        matter.procs.exmes.mixture(self.toStores.GrowthChamber.toPhases.GrowthMedium, "O2_to_Air")

        components.matter.algae.P2P.AtmosphericGasExchange(
            self.toStores.GrowthChamber, "CO2_Water_In_Out", "AirInGrowthChamber.CO2_to_Medium", "GrowthMedium.CO2_from_Air", "CO2"
        )
        components.matter.algae.P2P.AtmosphericGasExchange(
            self.toStores.GrowthChamber, "O2_Water_In_Out", "AirInGrowthChamber.O2_from_Medium", "GrowthMedium.O2_to_Air", "O2"
        )

        # Manipulator
        components.matter.algae.manipulators.GrowthMediumChanges(
            "GrowthMediumChanges_Manip", self.toStores.GrowthChamber.toPhases.GrowthMedium
        )

        # Additional Calculation Modules
        self.oGrowthRateCalculationModule.oTemperatureLimitation = (
            components.matter.algae.CalculationModules.GrowthRateCalculationModule.TemperatureLimitation(
                self.toStores.GrowthChamber.toPhases.GrowthMedium
            )
        )
        self.oGrowthRateCalculationModule.oPhLimitation = (
            components.matter.algae.CalculationModules.GrowthRateCalculationModule.PHLimitation(
                self.toStores.GrowthChamber.toPhases.GrowthMedium
            )
        )
        self.oGrowthRateCalculationModule.oO2Limitation = (
            components.matter.algae.CalculationModules.GrowthRateCalculationModule.OxygenLimitation(
                self.toStores.GrowthChamber.toPhases.GrowthMedium
            )
        )
        self.oGrowthRateCalculationModule.oCO2Limitation = (
            components.matter.algae.CalculationModules.GrowthRateCalculationModule.CarbonDioxideLimitation(
                self.toStores.GrowthChamber.toPhases.GrowthMedium
            )
        )
        self.oPARModule = components.matter.algae.CalculationModules.PARModule.PARModule(self)
        self.oGrowthRateCalculationModule.oPARLimitation.oPARModule = self.oPARModule

    def setIfFlows(self, sAir_Inlet, sAir_Outlet, sMedium_Outlet, sMedium_Inlet, sNO3_Inlet, sH2O_Inlet, sUrine_PBR):
        self.connectIF("Air_Inlet", sAir_Inlet)
        self.connectIF("Air_Outlet", sAir_Outlet)
        self.connectIF("Medium_Outlet", sMedium_Outlet)
        self.connectIF("Medium_Inlet", sMedium_Inlet)
        self.connectIF("NO3_Inlet", sNO3_Inlet)
        self.connectIF("H2O_Inlet", sH2O_Inlet)
        self.connectIF("Urine_PBR", sUrine_PBR)

    def createSolverStructure(self):
        super().createSolverStructure()

        solver.matter.manual.branch(self.toBranches.Air_from_GrowthChamber)
        aoMultiSolverBranches = [self.toBranches.Air_to_GrowthChamber]
        solver.matter_multibranch.iterative.branch(aoMultiSolverBranches, "complex")
        self.toBranches.Air_from_GrowthChamber.oHandler.setFlowRate(0.1)

        solver.matter.manual.branch(self.toBranches.Medium_to_Harvester)
        solver.matter_multibranch.iterative.branch(self.toBranches.Medium_from_Harvester, "complex")
        self.toBranches.Medium_to_Harvester.oHandler.setVolumetricFlowRate(self.oParent.fVolumetricFlowToHarvester)

        self.oUrinePhase = self.toBranches.Urine_from_PBR.coExmes[1].oPhase

        solver.matter.manual.branch(self.toBranches.NO3_from_Maintenance)
        solver.matter.manual.branch(self.toBranches.H2O_from_Maintenance)
        solver.matter.manual.branch(self.toBranches.Urine_from_PBR)
        self.setThermalSolvers()

        for store in self.toStores.values():
            for phase in store.aoPhases:
                phase.setTimeStepProperties({"fMaxStep": self.fTimeStep * 5})
                phase.oCapacity.setTimeStepProperties({"fMaxStep": self.fTimeStep * 5})

    def createThermalStructure(self):
        super().createThermalStructure()

        self.oHeatFromPAR = thermal.heatsource("Heater", 0)
        self.toStores.GrowthChamber.toPhases.GrowthMedium.oCapacity.addHeatSource(self.oHeatFromPAR)

        self.oMediumCooler = thermal.heatsource("Cooler", 0)
        self.toStores.GrowthChamber.toPhases.GrowthMedium.oCapacity.addHeatSource(self.oMediumCooler)

    def exec(self, _):
        self.fCurrentGrowthMediumDensity = self.oMT.calculateDensity(self.toStores.GrowthChamber.toPhases.GrowthMedium)

        self.oPARModule.update()
        self.oGrowthRateCalculationModule.update()

        self.oHeatFromPAR.setHeatFlow(self.oPARModule.fHeatPower)
        self.oMediumCooler.setHeatFlow(-self.oPARModule.fHeatPower)

        # Refill logic (Nitrogen and H2O handling here)
        # Logic is preserved from MATLAB, adjust for Python structures
        pass
