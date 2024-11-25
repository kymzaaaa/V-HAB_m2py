classdef BPA < vsys
    %% BPA
    % this a simple model of the Brine Processing Assembly used on the ISS
    % it only models the delays and recovery rates and is not based on
    % first principles.
    
    properties (SetAccess = protected, GetAccess = public)
        % Source "Closing the Water Loop for Exploration: 2018
        % Status of the Brine Processor Assembly", Laura K. Kelsey
        % et.al., 2018, ICES-2018-272 is mentioned as [1] in
        % the following
        
        % Size of the Brine Bladder (WSTA)
        % According to  [1] the Brine Bladders are oversized to have a
        % capacity of 24 l but are only filled with 22.5 l which is the
        % UPAs ARTFA capacity
        fBladderCapacity = 24 * 0.998;
        
        fActivationFillBPA = 22.5 * 0.998;
        
        % BPA flowrate based on 22.5 l per 26 day cycle mentioned in [1] 
        fBaseFlowRate = 22.5*0.998 / (26*24*3600);
        
        % Boolean that indicates UPA activity
        bProcessing = false;
        bDisposingConcentratedBrine = false;
        
        % Time at which the last UPA process finished
        fProcessingFinishTime = -20000;
        
        % According to [1] each cycle requires 26 days
        fProcessingTime = 26*24*3600;
        
        % Power usage of BPA (which is based on the Paragon IWP technology)
        % is 142 W according to "Selection of a Brine Processor Technology
        % for NASA Manned Missions", Donald L. Carter et.al. 2016, ICES-2016-014
        fPower = 142 ; % [W]
    endclass BPA(vsys):
    """
    BPA (Brine Processing Assembly) is a simplified model that simulates the
    delays and recovery rates of the BPA used on the ISS. It is not based on first principles.
    """

    def __init__(self, oParent, sName, fTimeStep=60):
        """
        Initialize the BPA system.

        :param oParent: Parent system.
        :param sName: Name of the BPA system.
        :param fTimeStep: Simulation time step.
        """
        super().__init__(oParent, sName, fTimeStep)

        # Brine bladder properties
        self.fBladderCapacity = 24 * 0.998
        self.fActivationFillBPA = 22.5 * 0.998

        # Base flow rate (22.5 liters processed in 26 days)
        self.fBaseFlowRate = 22.5 * 0.998 / (26 * 24 * 3600)

        # Processing flags and timing
        self.bProcessing = False
        self.bDisposingConcentratedBrine = False
        self.fProcessingFinishTime = -20000
        self.fProcessingTime = 26 * 24 * 3600

        # Power usage in watts
        self.fPower = 142

    def createMatterStructure(self):
        """
        Create the matter structure for the BPA system.
        """
        super().createMatterStructure()

        # Creating the WSTA (Wastewater Storage Tank Assembly)
        self.createStore('Bladder', (self.fBladderCapacity / 998) + 0.5)
        oBladder = self.toStores['Bladder'].createPhase(
            'mixture', 'Brine', 'liquid', {'Brine': 22.5 * 0.998 + 0.01}, 293, 1e5
        )
        oAir = self.toStores['Bladder'].createPhase(
            'gas', 'flow', 'Air', 0.5, {'N2': 8e4, 'O2': 2e4, 'CO2': 400}, 293, 0.5
        )

        self.createP2P('Bladder', 'WaterP2P', oBladder, oAir)

        # Creating the disposal store for concentrated brine
        self.createStore('ConcentratedBrineDisposal', 2)
        self.toStores['ConcentratedBrineDisposal'].createPhase(
            'mixture', 'ConcentratedBrine', 'liquid', 0.1, {'ConcentratedBrine': 0.1}, 293, 1e5
        )

        # Creating manual branches
        self.createBranch(oBladder, {}, 'BrineInlet', 'BrineInlet')
        self.createBranch(oAir, {}, 'AirInlet', 'AirInlet')
        self.createBranch(oAir, {}, 'AirOutlet', 'AirOutlet')
        self.createBranch(
            oBladder, {}, self.toStores['ConcentratedBrineDisposal'], 'ConcentratedBrineDisposal'
        )

        # Creating the manipulator
        self.createManipulator('BPA_Manip', self.toStores['Bladder'].toPhases['Brine'])

    def createSolverStructure(self):
        """
        Create the solver structure for the BPA system.
        """
        super().createSolverStructure()

        self.createSolverBranch('BrineInlet')
        self.createSolverBranch('AirInlet')
        self.createSolverBranch('ConcentratedBrineDisposal')

        self.toBranches['AirInlet'].setFlowRate(-0.1)

        solver_properties = {
            'fMaxError': 1e-6,
            'iMaxIterations': 1000,
            'fMinimumTimeStep': 1,
            'iIterationsBetweenP2PUpdate': 200,
            'bSolveOnlyFlowRates': True,
        }
        self.createMultiBranchSolver(self.toBranches['AirOutlet'], 'complex', solver_properties)

        timestep_properties = {'rMaxChange': float('inf')}
        self.toStores['Bladder'].toPhases['Brine'].setTimeStepProperties(timestep_properties)
        self.toStores['ConcentratedBrineDisposal'].toPhases['ConcentratedBrine'].setTimeStepProperties(
            timestep_properties
        )

        for store in self.toStores.values():
            for phase in store.aoPhases:
                timestep_properties = {'fMaxStep': self.fTimeStep * 5}
                phase.setTimeStepProperties(timestep_properties)
                phase.oCapacity.setTimeStepProperties(timestep_properties)

        self.setThermalSolvers()

    def setIfFlows(self, sBrineInlet, sAirInlet, sAirOutlet):
        """
        Connect the system and subsystem level branches.

        :param sBrineInlet: Interface for brine inlet.
        :param sAirInlet: Interface for air inlet.
        :param sAirOutlet: Interface for air outlet.
        """
        self.connectIF('BrineInlet', sBrineInlet)
        self.connectIF('AirInlet', sAirInlet)
        self.connectIF('AirOutlet', sAirOutlet)

    def exec(self):
        """
        Execute the BPA processing logic.
        """
        super().exec()

        brine_phase = self.toStores['Bladder'].toPhases['Brine']

        if brine_phase.afMass[self.oMT.tiN2I['Brine']] >= self.fActivationFillBPA:
            self.bProcessing = True
            self.fProcessingFinishTime = float('inf')

            # Limit mass change during processing
            timestep_properties = {'rMaxChange': 1e-3}
            brine_phase.setTimeStepProperties(timestep_properties)

        if self.bProcessing:
            if (
                self.oTimer.fTime >= self.fProcessingFinishTime
                or brine_phase
                .afMass[self.oMT.tiN2I['Brine']] == 0
            ):
                brine_phase.toManips['substance'].setActive(False)
                self.bProcessing = False

                # Allow unrestricted mass change
                timestep_properties = {'rMaxChange': float('inf')}
                brine_phase.setTimeStepProperties(timestep_properties)
            elif brine_phase.fMass >= 0.01:
                brine_phase.toManips['substance'].setActive(True)
                self.fProcessingFinishTime = self.oTimer.fTime + self.fProcessingTime

        if (
            not self.bProcessing
            and brine_phase.afMass[self.oMT.tiN2I['ConcentratedBrine']] > 0.02
            and not self.toBranches['ConcentratedBrineDisposal'].oHandler.bMassTransferActive
        ):
            self.toBranches['ConcentratedBrineDisposal'].oHandler.setMassTransfer(
                brine_phase.fMass - 0.01, 300
            )
            self.bDisposingConcentratedBrine = True
        elif not self.toBranches['ConcentratedBrineDisposal'].oHandler.bMassTransferActive:
            self.bDisposingConcentratedBrine = False

    
    methods
        function this = BPA(oParent, sName, fTimeStep, ~)
            if nargin < 3
                fTimeStep = 60;
            end
            this@vsys(oParent, sName, fTimeStep);
            
            eval(this.oRoot.oCfgParams.configCode(this));
            
        end
        
        function createMatterStructure(this)
            createMatterStructure@vsys(this);
            
            % Creating the WSTA (Wastewater Storage Tank Assembly)
            
            matter.store(this, 'Bladder', (this.fBladderCapacity / 998) + 0.5);
            % BPA is initialized as full as UPA ARTFA is initiliazed empty
            oBladder = matter.phases.mixture(this.toStores.Bladder,          'Brine', 'liquid', struct('Brine', 22.5*0.998 + 0.01), 293, 1e5);
            oAir     = this.toStores.Bladder.createPhase(  'gas', 'flow',   'Air',   0.5, struct('N2', 8e4, 'O2', 2e4, 'CO2', 400), 293, 0.5);
            
            components.matter.P2Ps.ManualP2P(this.toStores.Bladder, 'WaterP2P', oBladder, oAir);
            
            % The Brine Bladders actually have to be disposed manually,
            % here we use a store to move the concentrated brine there at
            % the end of each cycle.
            matter.store(this, 'ConcentratedBrineDisposal', 2);
            oConcentratedBrine = this.toStores.ConcentratedBrineDisposal.createPhase( 	'mixture', 	'ConcentratedBrine',  'liquid', 0.1, struct('ConcentratedBrine', 0.1), 293, 1e5);
            
            % Creating the manual branches
            matter.branch(this, oBladder,        	{}, 'BrineInlet',  	'BrineInlet');
            matter.branch(this, oAir,             	{}, 'AirInlet',    	'AirInlet');
            matter.branch(this, oAir,           	{}, 'AirOutlet',    'AirOutlet');
            
            matter.branch(this, oBladder,         	{}, oConcentratedBrine,  'ConcentratedBrineDisposal');
            
            % Creating the manipulator
            components.matter.BPA.components.BPA_Manip('BPA_Manip', this.toStores.Bladder.toPhases.Brine);
            
        end
        
        function createSolverStructure(this)
            createSolverStructure@vsys(this);
            
            
            solver.matter.manual.branch(this.toBranches.BrineInlet);
            solver.matter.manual.branch(this.toBranches.AirInlet);
            solver.matter.manual.branch(this.toBranches.ConcentratedBrineDisposal);
            
            this.toBranches.AirInlet.oHandler.setFlowRate(-0.1);
            
            tSolverProperties.fMaxError = 1e-6;
            tSolverProperties.iMaxIterations = 1000;
            tSolverProperties.fMinimumTimeStep = 1;
            tSolverProperties.iIterationsBetweenP2PUpdate = 200;
            tSolverProperties.bSolveOnlyFlowRates = true;
            
            oSolver = solver.matter_multibranch.iterative.branch(this.toBranches.AirOutlet, 'complex');
            oSolver.setSolverProperties(tSolverProperties);
            
            tTimeStepProperties.rMaxChange = inf;

            this.toStores.Bladder.toPhases.Brine.setTimeStepProperties(tTimeStepProperties);
            this.toStores.ConcentratedBrineDisposal.toPhases.ConcentratedBrine.setTimeStepProperties(tTimeStepProperties);
            
            csStoreNames = fieldnames(this.toStores);
            for iStore = 1:length(csStoreNames)
                for iPhase = 1:length(this.toStores.(csStoreNames{iStore}).aoPhases)
                    oPhase = this.toStores.(csStoreNames{iStore}).aoPhases(iPhase);
                    tTimeStepProperties = struct();
                    tTimeStepProperties.fMaxStep = this.fTimeStep * 5;

                    oPhase.setTimeStepProperties(tTimeStepProperties);

                    tTimeStepProperties = struct();
                    tTimeStepProperties.fMaxStep = this.fTimeStep * 5;
                    oPhase.oCapacity.setTimeStepProperties(tTimeStepProperties);
                end
            end
            
            this.setThermalSolvers();
        end
        
        function setIfFlows(this, sBrineInlet, sAirInlet, sAirOultet)
            % This function connects the system and subsystem level branches with each other. It
            % uses the connectIF function provided by the matter.container class
            
            this.connectIF('BrineInlet',   	sBrineInlet);
            this.connectIF('AirInlet',      sAirInlet);
            this.connectIF('AirOutlet',     sAirOultet);
            
        end
    end
    
    methods (Access = protected)
        
        function exec(this, ~)
            exec@vsys(this);
            
            if (this.toStores.Bladder.toPhases.Brine.afMass(this.oMT.tiN2I.Brine) >= this.fActivationFillBPA)
                this.bProcessing = true;
                this.fProcessingFinishTime = inf;
                
                % During processing the brine bladder mass change is
                % limited
                tTimeStepProperties = struct();
                tTimeStepProperties.rMaxChange = 1e-3;

                this.toStores.Bladder.toPhases.Brine.setTimeStepProperties(tTimeStepProperties);
            end
            
            if (this.bProcessing == true)
                if this.oTimer.fTime >= this.fProcessingFinishTime || this.toStores.Bladder.toPhases.Brine.afMass(this.oMT.tiN2I.Brine) == 0
                    this.toStores.Bladder.toPhases.Brine.toManips.substance.setActive(false);
                    this.bProcessing = false;
                    
                    % While BPA is not processing the mass in the brine
                    % bladder phase can change by as much as it likes
                    tTimeStepProperties = struct();
                    tTimeStepProperties.rMaxChange = inf;

                    this.toStores.Bladder.toPhases.Brine.setTimeStepProperties(tTimeStepProperties);
                    
                elseif(this.toStores.Bladder.toPhases.Brine.fMass >= 0.01)
                    this.toStores.Bladder.toPhases.Brine.toManips.substance.setActive(true);
                    this.fProcessingFinishTime = this.oTimer.fTime + this.fProcessingTime;
                    
                end
            end
            
            if ~this.bProcessing && this.toStores.Bladder.toPhases.Brine.afMass(this.oMT.tiN2I.ConcentratedBrine) > 0.02 && ~this.toBranches.ConcentratedBrineDisposal.oHandler.bMassTransferActive
                this.toBranches.ConcentratedBrineDisposal.oHandler.setMassTransfer(this.toStores.Bladder.toPhases.Brine.fMass - 0.01, 300);
                this.bDisposingConcentratedBrine = true;
            elseif ~this.toBranches.ConcentratedBrineDisposal.oHandler.bMassTransferActive
                this.bDisposingConcentratedBrine = false;
            end
        end
    end
end