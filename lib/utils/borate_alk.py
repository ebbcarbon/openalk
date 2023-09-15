import numpy as np


def borateALK(S, T, pHinit):
    lnKB = (
        (
            -8966.90
            - 2890.53 * (S**0.5)
            - 77.942 * S
            + 1.728 * (S**1.5)
            - 0.0996 * (S**2)
        )
        / T
        + 148.0248
        + 137.1942 * (S**0.5)
        + 1.62142 * S
        - (24.4344 + 25.085 * (S**0.5) + 0.2474 * S) * np.log(T)
        + 0.053105 * (S**0.5) * T
    )  # Dickson 1990

    KB = np.exp(lnKB)
    TB = 0.000416 * S / 35
    BA = TB * (KB / (KB + np.power(10, -1 * pHinit))) * 1000000  # in microM/Kg

    return BA
