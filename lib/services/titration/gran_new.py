from typing import Tuple

import numpy as np

from lib.utils import rsq

class ModifiedGranTitrationNew:
    def __init__(self, sample_mass: float, salinity: float, acid_conc: float,
                  temp: float, ph_initial: float, emf_initial: float) -> None:
        self.sample_mass_kg = sample_mass / 1000
        self.salinity = salinity
        self.acid_conc_M = acid_conc
        self.temp_C = temp
        self.temp_K = self.temp_C + 273.15
        self.ph_array = np.array([ph_initial])
        self.emf_array = np.array([emf_initial])
        self.volume_array = np.array([0])

    def calc_K1(self) -> float:
        """Calculates the carbonic acid dissociation constant (K1) for the
        reaction H2CO3 --> H + HCO3.

        pK1 = -log_10(K1), K1 = 10^(-pK1), etc.

        (Mehrbach 1973 refitted by Dickson and Millero 1987)
        """
        pK1 = (
            (3670.7 / self.temp_K)
            - 62.008
            + (9.7944 * np.log(self.temp_K))
            - (0.0118 * self.salinity)
            + (0.000116 * (self.salinity**2))
        )
        return np.power(10, -1 * pK1)

    def calc_K2(self) -> float:
        """Calculates the bicarbonate dissociation constant (K2) for the
        reaction HCO3 --> H + CO3.

        pK2 = -log_10(K2), K2 = 10^(-pK2), etc.

        (Mehrbach 1973 refitted by Dickson and Millero 1987)
        """
        pK2 = (
            (1394.7 / self.temp_K)
            + 4.777
            - (0.0184 * self.salinity)
            + 0.000118 * (self.salinity**2)
        )
        return np.power(10, -1 * pK2)

    def calc_KW(self) -> float:
        """Calculates the water dissociation constant (KW) for the
        reaction H2O --> H + OH.

        lnKW = ln(KW), KW = exp(ln(KW)), etc.

        (DOE 1994)
        """
        lnKW = (
            - (13847.26 / self.temp_K)
            + 148.9652
            - (23.6521 * np.log(self.temp_K))
            + (((118.67 / self.temp_K) - 5.977 + (1.0495 * np.log(self.temp_K))) * (self.salinity**0.5))
            - (0.01615 * self.salinity)
        )
        return np.exp(lnKW)

    def calc_KB(self) -> float:
        """Calculates the boric acid dissociation constant (KB) for the
        reaction B(OH)3 --> B(OH)4 + H.

        lnKB = ln(KB), KB = exp(ln(KB)), etc.

        (Dickson 1990b)
        """
        lnKB = (
            ((
                - 8966.90
                - (2890.53 * (self.salinity**0.5))
                - (77.942 * self.salinity)
                + (1.728 * (self.salinity**1.5))
                - (0.0996 * (self.salinity**2))
            ) / self.temp_K)
            + 148.0248
            + (137.1942 * (self.salinity**0.5))
            + (1.62142 * self.salinity)
            - (24.4344 + (25.085 * (self.salinity**0.5)) + (0.2474 * self.salinity)) * np.log(self.temp_K)
            + (0.053105 * (self.salinity**0.5) * self.temp_K)
        )
        return np.exp(lnKB)

    def get_required_acid_vol(self, target_ph: float) -> float:
        K1c = np.power(10, -1 * pK1c)
        K2c = np.power(10, -1 * pK2c)
        Kw = np.exp(lnKw)
        TB = 0.000416 * self.S / 35
        DIC = 0.002050 * self.S / 35
        KB = np.exp(lnKB)

        # Calculate initial acid volume

        denumCinit = (
            np.square(np.power(10, -1 * self.pHs[-1]))
            + K1c * np.power(10, -1 * self.pHs[-1])
            + K1c * K2c
        )
        denumCf = (
            np.square(np.power(10, -1 * pHf)) + K1c * np.power(10, -1 * pHf) + K1c * K2c
        )
        alphaC1init = K1c * np.power(10, -1 * self.pHs[-1]) / denumCinit
        alphaC2init = np.square(K1c * K2c) / denumCinit
        C_alk_i = DIC * (2 * alphaC2init + alphaC1init)
        alphaC1f = K1c * np.power(10, -1 * pHf) / denumCf
        alphaC2f = np.square(K1c * K2c) / denumCf
        C_alk_f = DIC * (2 * alphaC2f + alphaC1f)
        BAi = TB * (KB / (KB + np.power(10, -1 * self.pHs[-1])))
        BAf = TB * (KB / (KB + np.power(10, -1 * pHf)))
        acidVol = (
            self.sampleSize
            / Cacid
            * (
                np.power(10, -1 * pHf)
                - np.power(10, -1 * self.pHs[-1])
                - (C_alk_f - C_alk_i)
                - (BAf - BAi)
                - Kw
                * (
                    np.reciprocal(np.power(10, -1 * pHf))
                    - np.reciprocal(np.power(10, -1 * self.pHs[-1]))
                )
            )
        )

        return acidVol

    """Give this another name that's clearer about what it does"""
    def gran_calc(self) -> Tuple[float, float, float]:
        volumes = self.volumeAdded[self.pHs < 3.8]  # need to be numpy arrays
        pHs = self.pHs[self.pHs < 3.8]
        pH_modified = np.power(10, np.multiply(-1, pHs))

        ygran = np.multiply(np.add(self.sampleSize, volumes), pH_modified)

        slope, intercept, xModel, yModel, rsquare = rsq.RSQ(volumes, ygran)
        gamma = slope / Cacid
        Veq = -1 * intercept / slope
        molIn = Veq * Cacid

        TA = molIn / self.sampleSize * 1000000

        return TA, gamma, rsquare
