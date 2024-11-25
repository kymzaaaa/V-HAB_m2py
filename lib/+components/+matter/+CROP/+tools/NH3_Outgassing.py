import math

def NH3_Outgassing(fCurrentTemp, fCurrentOHminus, fCurrentNH3, fCurrentNH4, fCurrent_CO2_gas, fH_cc_CO2):
    """
    Calculate the current NH3 gas concentration in the gas phase above a solution at ambient pressure.

    Parameters:
        fCurrentTemp (float): Current temperature in Kelvin.
        fCurrentOHminus (float): Current OH- concentration in the solution (mol/L).
        fCurrentNH3 (float): Current NH3 concentration in the solution (mol/L).
        fCurrentNH4 (float): Current NH4+ concentration in the solution (mol/L).
        fCurrent_CO2_gas (float): CO2 concentration in the gas phase (mol/L).
        fH_cc_CO2 (float): Dimensionless Henry solubility of CO2.

    Returns:
        float: Current NH3 gas concentration in the gas phase (mol/L).
    """
    # Current total ammonia and ammonium concentration in the solution in mol/L
    fCurrentTotalAmmonia = fCurrentNH3 + fCurrentNH4

    # Empirical dimensionless Henry solubility of ammonia without the effect of CO2 concentration
    fH_cc_NH3 = 10 ** (-1.694 + (1477.7 / fCurrentTemp))

    # Empirical solubility parameters
    fP = 10 ** (28.068 - (5937.7 / fCurrentTemp))
    fQ = 10 ** (25.266 - (6417.8 / fCurrentTemp))

    # Ion product of water at 25°C, estimated as constant
    fK_W = 1e-14

    # Calculation of ammonia dissociation constant K_diss_NH3 in water with empirical equilibrium constant K_a
    fK_a = 10 ** (-0.09018 - (2729.92 / fCurrentTemp))
    fK_diss_NH3 = fK_W / fK_a

    # Calculate the current concentration of NH3 in the gas phase above the solution in mol/L
    fCurrentNH3gas = (
        (fCurrentTotalAmmonia / fH_cc_NH3) *
        ((fH_cc_NH3 * fH_cc_CO2 * fCurrent_CO2_gas * fQ) + 1) /
        (fH_cc_CO2 * fCurrent_CO2_gas * fP + ((fK_diss_NH3 / fCurrentOHminus) + 1))
    )

    return fCurrentNH3gas
