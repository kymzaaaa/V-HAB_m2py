class PressureRegulator(vsys):
    """
    PressureRegulator class for controlling gas pressure in two stages.
    """

    def __init__(self, oParent, sName, tParameters):
        """
        Constructor for PressureRegulator.

        Args:
            oParent: Parent system.
            sName: Name of the regulator.
            tParameters: Parameters including first and second stage settings.
        """
        super().__init__(oParent, sName)

        self.fFixedTimeStep = tParameters.get("fFixedTimeStep", 0.1)
        self.iFlowRateDampeningFactor = 0
        self.sAtmosphereHelper = tParameters.get("sAtmosphereHelper", "N2Atmosphere")
        self.bActive = tParameters.get("bActive", False)

        self.fPressureSetpoint = 28900
        self.tFirstStageParameters = tParameters["tFirstStageParameters"]
        self.tSecondStageParameters = tParameters["tSecondStageParameters"]

    def createMatterStructure(self):
        """
        Creates the matter structure for the pressure regulator.
        """
        super().createMatterStructure()

        # Add InterStage store with volume 0.01 m^3
        matter.store(self, "InterStage", 0.01)

        # Create gas phase in InterStage store
        oGasPhaseInter = self.toStores.InterStage.createPhase(
            self.sAtmosphereHelper, 0.01, 293.15, 0, self.tFirstStageParameters["fPressureSetpoint"]
        )

        # Adding valves for first and second stages
        components.matter.PressureRegulator.valve(self, "FirstStageValve", self.tFirstStageParameters)
        components.matter.PressureRegulator.valve(self, "SecondStageValve", self.tSecondStageParameters)

        # Add extract/merge processors
        matter.procs.exmes.gas(oGasPhaseInter, "PortInterIn")
        matter.procs.exmes.gas(oGasPhaseInter, "PortInterOut")

        # Connect components to set the flow path
        matter.branch(self, "InterStage.PortInterIn", ["FirstStageValve"], "Inlet", "InletBranch")
        matter.branch(self, "InterStage.PortInterOut", ["SecondStageValve"], "Outlet", "OutletBranch")

    def createSolverStructure(self):
        """
        Creates the solver structure for the pressure regulator.
        """
        super().createSolverStructure()

        # Add branches to solver
        solver.matter.interval.branch(self.toBranches.InletBranch)
        solver.matter.interval.branch(self.toBranches.OutletBranch)

        self.setThermalSolvers()

    def setIfFlows(self, sInlet, sOutlet):
        """
        Sets the inlet and outlet interface flows.

        Args:
            sInlet: Inlet interface.
            sOutlet: Outlet interface.
        """
        self.connectIF("Inlet", sInlet)
        self.connectIF("Outlet", sOutlet)

    def setEnvironmentReference(self, oGasPhaseEnvRef):
        """
        Sets the environment reference for the valves.

        Args:
            oGasPhaseEnvRef: Reference gas phase environment.
        """
        self.toProcsF2F.FirstStageValve.setEnvironmentReference(oGasPhaseEnvRef)
        self.toProcsF2F.SecondStageValve.setEnvironmentReference(oGasPhaseEnvRef)

    def setPressureSetpoint(self, fPressureSetpoint):
        """
        Sets the pressure setpoint for the second stage valve.

        Args:
            fPressureSetpoint: Desired pressure setpoint.
        """
        self.fPressureSetpoint = fPressureSetpoint
        self.toProcsF2F.SecondStageValve.changeSetpoint(fPressureSetpoint)

    def exec(self, _):
        """
        Executes the regulator logic.
        """
        super().exec()
