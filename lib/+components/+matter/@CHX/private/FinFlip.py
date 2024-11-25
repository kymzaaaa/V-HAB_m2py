def FinFlip(tInput, tFinOutput):
    """
    This function 'flips' the additional thermal resistance of the fins.
    Used for the lower layer after the upper layer is calculated, as the fin
    configuration changes.
    """
    if tInput['iFinAir'] == 0:
        iFinAirOut = 1 * tFinOutput['fFinFactorAir']
    else:
        iFinAirOut = 0

    if tInput['iFinCoolant'] == 0:
        iFinCoolantOut = 1 * tFinOutput['fFinFactorCoolant']
    else:
        iFinCoolantOut = 0

    return iFinAirOut, iFinCoolantOut
