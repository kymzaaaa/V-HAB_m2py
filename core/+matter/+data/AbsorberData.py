class AbsorberData:
    """
    ABSORBERDATA Constant data class containing the data for several absorber substances.
    For each substance, the following data is stored in this class:

    Toth parameters:
        A0 in mol/(kg Pa)
        B0 in 1/Pa
        E in K
        T0 in -
        C0 in K

    Absorption enthalpy in J/mol
    """

    Zeolite5A = {
        "tToth": {
            "fA0_CO2": 9.875E-10,
            "fB0_CO2": 6.761E-11,
            "fE_CO2": 5.625E3,
            "fT0_CO2": 2.700E-1,
            "fC0_CO2": -2.002E1,
            "fA0_H2O": 1.106E-11,
            "fB0_H2O": 4.714E-13,
            "fE_H2O": 9.955E3,
            "fT0_H2O": 3.548E-1,
            "fC0_H2O": -5.114E1,
        },
        "fAdsorptionEnthalpy_CO2": -38000,
        "fAdsorptionEnthalpy_H2O": -45000,
    }

    Zeolite5A_RK38 = {
        "tToth": {
            "fA0_CO2": 9.875E-10,
            "fB0_CO2": 6.761E-11,
            "fE_CO2": 5.625E3,
            "fT0_CO2": 2.700E-1,
            "fC0_CO2": -2.002E1,
            "fA0_H2O": 1.106E-11,
            "fB0_H2O": 4.714E-13,
            "fE_H2O": 9.955E3,
            "fT0_H2O": 3.548E-1,
            "fC0_H2O": -5.114E1,
        },
        "fAdsorptionEnthalpy_CO2": -38000,
        "fAdsorptionEnthalpy_H2O": -45000,
    }

    Zeolite13x = {
        "tToth": {
            "fA0_CO2": 6.509E-6,
            "fB0_CO2": 4.884E-7,
            "fE_CO2": 2.991E3,
            "fT0_CO2": 7.487E-2,
            "fC0_CO2": 3.805E1,
            "fA0_H2O": 3.634E-9,
            "fB0_H2O": 2.408E-10,
            "fE_H2O": 6.852E3,
            "fT0_H2O": 3.974E-1,
            "fC0_H2O": -4.199,
        },
        "fAdsorptionEnthalpy_CO2": -40000,
        "fAdsorptionEnthalpy_H2O": -55000,
    }

    SilicaGel_40 = {
        "tToth": {
            "fA0_CO2": 7.678E-9,
            "fB0_CO2": 5.164E-10,
            "fE_CO2": 2.330E3,
            "fT0_CO2": -3.053E-1,
            "fC0_CO2": 2.386E2,
            "fA0_H2O": 1.767E-1,
            "fB0_H2O": 2.787E-8,
            "fE_H2O": 1.093E3,
            "fT0_H2O": -1.190E-3,
            "fC0_H2O": 2.213E1,
        },
        "fAdsorptionEnthalpy_CO2": -40000,
        "fAdsorptionEnthalpy_H2O": -50200,
    }

    Sylobead_B125 = {
        "tToth": {
            "fA0_CO2": 7.678E-9,
            "fB0_CO2": 5.164E-10,
            "fE_CO2": 2.330E3,
            "fT0_CO2": -3.053E-1,
            "fC0_CO2": 2.386E2,
            "fA0_H2O": 1.767E-1,
            "fB0_H2O": 2.787E-8,
            "fE_H2O": 1.093E3,
            "fT0_H2O": -1.190E-3,
            "fC0_H2O": 2.213E1,
        },
        "fAdsorptionEnthalpy_CO2": -40000,
        "fAdsorptionEnthalpy_H2O": -50200,
    }

    BMIMAc = {
        "tToth": {
            "fA0_CO2": float("nan"),
            "fB0_CO2": float("nan"),
            "fE_CO2": float("nan"),
            "fT0_CO2": float("nan"),
            "fC0_CO2": float("nan"),
            "fA0_H2O": float("nan"),
            "fB0_H2O": float("nan"),
            "fE_H2O": float("nan"),
            "fT0_H2O": float("nan"),
            "fC0_H2O": float("nan"),
        },
        "fAdsorptionEnthalpy_CO2": -10190,
        "fAdsorptionEnthalpy_H2O": float("nan"),
    }

    EMIMAc = {
        "tToth": {
            "fA0_CO2": float("nan"),
            "fB0_CO2": float("nan"),
            "fE_CO2": float("nan"),
            "fT0_CO2": float("nan"),
            "fC0_CO2": float("nan"),
            "fA0_H2O": float("nan"),
            "fB0_H2O": float("nan"),
            "fE_H2O": float("nan"),
            "fT0_H2O": float("nan"),
            "fC0_H2O": float("nan"),
        },
        "fAdsorptionEnthalpy_CO2": -8290,
        "fAdsorptionEnthalpy_H2O": float("nan"),
    }
