class CROP(vsys):
    """
    The system file for the C.R.O.P. system.
    As described in chapter 4 of the thesis, the CROP system
    contains 2 stores "Tank" and "BioFilter". The store "Tank" is
    implemented in this file, including the phase "TankSolution" and two
    Exmes on it ("Tank.In" and "Tank.Out"). The modular "BioFilter" is
    implemented in the "+components" folder. Two branches
    "Tank_to_BioFilter" and "BioFilter_to_Tank" are also implemented to
    realize the wastewater circulation between "Tank" and "BioFilter".
    """

    def __init__(self, oParent, sName, fTimeStep=300):
        super().__init__(oParent, sName, fTimeStep)
        self.fCapacity = 30  # kg
        self.afInitialMasses = None
        self.bManualUrineSupply = False
        self.fCurrentPowerConsumption = 7  # EHEIM compactON 300 pump (7W)
        self.fInitialMassParentUrineSupply = 0
        self.bResetInitialMass = False
        eval(self.oRoot.oCfgParams.configCode(self))

    def createMatterStructure(self):
        super().createMatterStructure()

        # Tank volume
        fVolume_Tank = 0.03

        # Tank store in CROP model
        matter.store(self, "CROP_Tank", fVolume_Tank + 0.005)

        # Phase "TankSolution" in the store
        oTankSolution = matter.phases.mixture(
            self.toStores.CROP_Tank, "TankSolution", "liquid",
            {"H2O": 1e-4}, 293.15, 1e5
        )
        oFlow = self.toStores.CROP_Tank.createPhase(
            "mixture", "flow", "Aeration", "liquid", 1e-6, {"H2O": 1}, 293, 1e5
        )

        self.afInitialMasses = oTankSolution.afMass

        # Exme processors on the "TankSolution" phase
        matter.procs.exmes.mixture(oTankSolution, "Tank_Out")
        matter.procs.exmes.mixture(oTankSolution, "Tank_In")
        matter.procs.exmes.mixture(oTankSolution, "Urine_In")
        matter.procs.exmes.mixture(oTankSolution, "Solution_Out")

        components.matter.pH_Module.flowManip("CROP_pHManip", oFlow)

        # Calcite acidic dissolution manipulator
        oCalcite = matter.phases.mixture(
            self.toStores.CROP_Tank, "Calcite", "liquid",
            {"H2O": 0.5, "CaCO3": 0.5}, 293.15, 1e5
        )
        components.matter.CROP.tools.AcidOnCalcite("Acid Reaction on Calcite", oCalcite)

        # "TankAir" phase for air in the tank
        oTankAir = self.toStores.CROP_Tank.createPhase(
            "gas", "flow", "TankAir", 0.001,
            {"N2": 0.9 * 8e4, "O2": 0.9 * 2e4, "CO2": 0.9 * 500, "NH3": 0},
            293, 0.5
        )

        # NH3 and CO2 outgassing ExMes
        matter.procs.exmes.mixture(oTankSolution, "NH3TankSolutionOutgassing")
        matter.procs.exmes.gas(oTankAir, "NH3OutgassingFromTankSolution")
        matter.procs.exmes.mixture(oTankSolution, "CO2TankSolutionOutgassing")
        matter.procs.exmes.gas(oTankAir, "CO2OutgassingFromTankSolution")

        # Outgassing P2Ps
        components.matter.CROP.tools.P2P_Outgassing(
            self.toStores.CROP_Tank, "NH3_Outgassing_Tank",
            "TankSolution.NH3TankSolutionOutgassing",
            "TankAir.NH3OutgassingFromTankSolution", "NH3"
        )
        components.matter.CROP.tools.P2P_Outgassing(
            self.toStores.CROP_Tank, "CO2_Outgassing_Tank",
            "TankSolution.CO2TankSolutionOutgassing",
            "TankAir.CO2OutgassingFromTankSolution", "CO2"
        )

        self.toStores.CROP_Tank.addStandardVolumeManipulators()

        # BioFilter store
        components.matter.CROP.components.BioFilter(self, "CROP_BioFilter")

        # Additional P2Ps
        components.matter.P2Ps.ManualP2P(
            self.toStores.CROP_Tank, "O2_to_TankSolution", oTankAir, oFlow
        )
        components.matter.P2Ps.ManualP2P(
            self.toStores.CROP_Tank, "Calcite_to_TankSolution", oCalcite, oTankSolution
        )
        components.matter.Manips.ManualManipulator(
            self.toStores.CROP_Tank, "UrineConversion", oTankSolution
        )

        # Branches for wastewater circulation
        matter.branch(self, "CROP_Tank.Tank_Out", {}, oFlow, "Tank_to_BioFilter")
        matter.branch(self, oFlow, {}, "CROP_BioFilter.In", "Aeration_to_BioFilter")
        matter.branch(self, "CROP_BioFilter.Out", {}, "CROP_Tank.Tank_In", "BioFilter_to_Tank")
        matter.branch(self, "CROP_Tank.Urine_In", {}, "CROP_Urine_Inlet", "CROP_Urine_Inlet")
        matter.branch(self, "CROP_Tank.Solution_Out", {}, "CROP_Solution_Outlet", "CROP_Solution_Outlet")
        matter.branch(self, oTankAir, {}, "CROP_Air_Inlet", "CROP_Air_Inlet")
        matter.branch(self, oTankAir, {}, "CROP_Air_Outlet", "CROP_Air_Outlet")
        matter.branch(self, oCalcite, {}, "CROP_Calcite_Inlet", "CROP_Calcite_Inlet")

    def setUrineSupplyToManual(self, bManualUrineSupply):
        self.bManualUrineSupply = bManualUrineSupply

    def createThermalStructure(self):
        super().createThermalStructure()

        oHeatSource = thermal.heatsource("Heater", 0)
        self.toStores.CROP_Tank.toPhases.TankSolution.oCapacity.addHeatSource(oHeatSource)

    def createSolverStructure(self):
        super().createSolverStructure()

        # Use the "manual" solver for specific branches
        solver.matter.manual.branch(self.toBranches.Tank_to_BioFilter)
        solver.matter.manual.branch(self.toBranches.CROP_Air_Inlet)
        solver.matter.manual.branch(self.toBranches.CROP_Calcite_Inlet)
        self.toBranches.CROP_Air_Inlet.oHandler.setVolumetricFlowRate(-0.1)

        aoMultiSolverBranches = [
            self.toBranches.Aeration_to_BioFilter,
            self.toBranches.BioFilter_to_Tank,
            self.toBranches.CROP_Air_Outlet,
        ]
        solver.matter_multibranch.iterative.branch(aoMultiSolverBranches, "complex")

        # Interface branches
        solver.matter.manual.branch(self.toBranches.CROP_Urine_Inlet)
        solver.matter.manual.branch(self.toBranches.CROP_Solution_Outlet)

        # Set flow rate for wastewater circulation
        self.toBranches.Tank_to_BioFilter.oHandler.setVolumetricFlowRate(1 / 3600)

        # Set time step properties for phases
        csStoreNames = list(self.toStores.keys())
        for sStore in csStoreNames:
            for oPhase in self.toStores[sStore].aoPhases:
                tTimeStepProperties = {"fMaxStep": self.fTimeStep * 5}
                oPhase.setTimeStepProperties(tTimeStepProperties)
                oPhase.oCapacity.setTimeStepProperties(tTimeStepProperties)

        tTimeStepProperties = {"rMaxChange": 0.01}
        self.toStores.CROP_Tank.toPhases.TankAir.setTimeStepProperties(tTimeStepProperties)

        tTimeStepProperties = {"arMaxChange": np.zeros(self.oMT.iSubstances)}
        self.toStores.CROP_Tank.toPhases.TankSolution.setTimeStepProperties(tTimeStepProperties)

        self.setThermalSolvers()

    def setIfFlows(self, sUrineInlet, sSolutionOutlet, sAirInlet, sAirOutlet, sCalciteInlet):
        self.connectIF("CROP_Urine_Inlet", sUrineInlet)
        self.connectIF("CROP_Solution_Outlet", sSolutionOutlet)
        self.connectIF("CROP_Air_Inlet", sAirInlet)
        self.connectIF("CROP_Air_Outlet", sAirOutlet)
        self.connectIF("CROP_Calcite_Inlet", sCalciteInlet)
        self.fInitialMassParentUrineSupply = self.toBranches.CROP_Urine_Inlet.coExmes[2].oPhase.fMass

    def exec(self, _):
        super().exec(_)

        # Logic for managing tank solution and refilling urine supply
        # ... (Similar to the original MATLAB implementation)
