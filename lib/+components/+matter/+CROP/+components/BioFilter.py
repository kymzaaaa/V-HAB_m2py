import math

class BioFilter:
    """
    The modular store "BioFilter" in the CROP model.

    The store "BioFilter" with its three phases "FlowPhase", "BioPhase" and 
    "Atmosphere" is implemented here. The modular manipulator "Enzyme 
    Reactions" is handled in the corresponding Enzyme_Reactions class in the 
    components package.
    """

    def __init__(self, oContainer, sName):
        """
        Initialize the BioFilter store.
        """
        # The store "BioFilter" is implemented as a cylinder with a
        # diameter of 10 cm and a length of 100 cm
        fVolume = math.pi * (0.1 / 2)**2 * 1.0

        # Create the store "BioFilter" based on the cylinder's volume
        self.store = matter.Store(oContainer, sName, fVolume)

        # Initialize phases
        self.create_flow_phase()
        self.create_bio_phase()

        # Add enzyme reactions
        self.add_enzyme_reactions()

        # Add P2Ps
        self.add_p2ps()

    def create_flow_phase(self):
        """
        Create the FlowPhase in the BioFilter store.
        """
        fVolume_FlowPhase = 0.001  # 1 L
        self.oFlow = self.store.createPhase(
            'mixture', 'flow', 'FlowPhase', 'liquid', 
            fVolume_FlowPhase, {'H2O': 1}, 293, 1e5
        )

        # Add ExMe processors to the FlowPhase
        matter.procs.exmes.mixture(self.oFlow, 'In')
        matter.procs.exmes.mixture(self.oFlow, 'Out')
        matter.procs.exmes.mixture(self.oFlow, 'Flow_P2P_In')
        matter.procs.exmes.mixture(self.oFlow, 'Flow_P2P_Out')

    def create_bio_phase(self):
        """
        Create the BioPhase in the BioFilter store.
        """
        self.oBio = matter.phases.mixture(
            self.store, 'BioPhase', 'liquid',
            {
                'H2O': 0.1, 'CH4N2O': 1e-4, 'NH3': 1e-4, 'NO2': 1e-4,
                'NO3': 1e-4, 'NH4': 1e-4, 'O2': 1e-4, 'CO2': 1e-4, 'H': 1e-4
            },
            293.15, 9e4
        )

        # Add ExMe processors to the BioPhase
        matter.procs.exmes.mixture(self.oBio, 'Bio_P2P_In')
        matter.procs.exmes.mixture(self.oBio, 'Bio_P2P_Out')

    def add_enzyme_reactions(self):
        """
        Add the Enzyme Reactions manipulator to the BioFilter.
        """
        components.matter.CROP.components.Enzyme_Reactions(
            'Enzyme Reactions', self.oBio, self.store.fVolume
        )

    def add_p2ps(self):
        """
        Add P2Ps to the BioFilter to hold nominal levels of substances.
        """
        components.matter.P2Ps.ManualP2P(
            self.store, 'BiofilterOut', 
            'BioPhase.Bio_P2P_Out', 'FlowPhase.Flow_P2P_Out'
        )
        components.matter.P2Ps.ManualP2P(
            self.store, 'BiofilterIn', 
            'BioPhase.Bio_P2P_In', 'FlowPhase.Flow_P2P_In'
        )
