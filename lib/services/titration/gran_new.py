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

        self.IS = self.calc_IS()
        self.K1 = self.calc_K1()
        self.K2 = self.calc_K2()
        self.KW = self.calc_KW()
        self.KB = self.calc_KB()

        self.BT = self.calc_BT()
        self.DIC = self.calc_DIC()

    def calc_IS(self) -> float:
        """Calculates ionic strength (IS) of the sample.
        """
        return (19.924 * self.salinity) / (1000 - (1.005 * self.salinity))

    def calc_K1(self) -> float:
        """Calculates the carbonic acid equilibrium constant (K1) for the
        reaction:
                          H2CO3 --> H + HCO3.

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
        """Calculates the bicarbonate equilibrium constant (K2) for the
        reaction:
                          HCO3 --> H + CO3.

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
        """Calculates the water equilibrium constant (KW) for the
        reaction:
                          H2O --> H + OH.

        lnKW = ln(KW), KW = exp(ln(KW)), etc.

        (DOE 1994)
        """
        lnKW = (
            - (13847.26 / self.temp_K)
            + 148.9652
            - (23.6521 * np.log(self.temp_K))
            + (
                ((118.67 / self.temp_K)
                - 5.977
                + (1.0495 * np.log(self.temp_K)))
                * (self.salinity**0.5)
              )
            - (0.01615 * self.salinity)
        )
        return np.exp(lnKW)

    def calc_KB(self) -> float:
        """Calculates the boric acid equilibrium constant (KB) for the
        reaction:
                        B(OH)3 --> B(OH)4 + H.

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
                ) / self.temp_K
            )
            + 148.0248
            + (137.1942 * (self.salinity**0.5))
            + (1.62142 * self.salinity)
            - ((
                24.4344
                + (25.085 * (self.salinity**0.5))
                + (0.2474 * self.salinity)
                ) * np.log(self.temp_K)
            )
            + (0.053105 * (self.salinity**0.5) * self.temp_K)
        )
        return np.exp(lnKB)

    def calc_BT(self) -> float:
        """Estimate of total borate based on salinity.
        """
        return (0.000416 * self.salinity) / 35

    def calc_DIC(self) -> float:
        """Estimate of dissolved inorganic carbon based on salinity.
        """
        return (0.002050 * self.salinity) / 35

    def calc_H_concentration(self, ph: float) -> float:
        """Calculates the hydrogen ion concentration at a particular pH.
        """
        return np.power(10, -1 * ph)

    def calc_concentration_denominator(self, ph: float) -> float:
        """Calculates the common denominator term in the expressions
        for the concentrations of bicarbonate and carbonate:

                      [H+]^2 + K1*[H+] + K1*K2.
        """
        H_conc = self.calc_H_concentration(ph)
        return (H_conc**2) + (self.K1 * H_conc) + (self.K1 * self.K2)

    def calc_carbonate_alkalinity(self, ph: float) -> float:
        """Calculates the carbonate alkalinity:

                        Ac = [HCO3] + 2[CO3],

        at a given pH using the estimated level of DIC.
        """
        H_conc = self.calc_H_concentration(ph)
        conc_denom = self.calc_concentration_denominator(ph)

        alpha_C1 = (self.K1 * H_conc) / conc_denom
        # I'm fairly certain it was a typo, but in the original code
        # the alphaC2 parameter was np.square(K1, K2)
        alpha_C2 = (self.K1 * self.K2) / conc_denom

        return self.DIC * (alpha_C1 + (2 * alpha_C2))

    def calc_borate_alkalinity(self, ph: float) -> float:
        """Calculates the borate alkalinity:

                          Ab = [B(OH)4],

        at a given pH using the estimated level of total borate.
        """
        H_conc = self.calc_H_concentration(ph)
        return self.BT * (self.KB / (self.KB + H_conc))

    def get_last_ph(self) -> float:
        """Returns the pH reading from the most recent titration step.
        """
        return self.ph_array[-1]

    def get_required_acid_vol(self, target_ph: float) -> float:
        """Calculates the volume of HCl required to lower the pH from
        the most recent pH reading to the target pH.
        """
        initial_ph = self.get_last_ph()

        H_conc_initial = self.calc_H_concentration(initial_ph)
        H_conc_final = self.calc_H_concentration(target_ph)

        carbonate_alk_initial = self.calc_carbonate_alkalinity(initial_ph)
        carbonate_alk_final = self.calc_carbonate_alkalinity(target_ph)

        borate_alk_initial = self.calc_borate_alkalinity(initial_ph)
        borate_alk_final = self.calc_borate_alkalinity(target_ph)

        H_conc_diff = H_conc_final - H_conc_initial
        carbonate_alk_diff = carbonate_alk_final - carbonate_alk_initial
        borate_alk_diff = borate_alk_final - borate_alk_initial

        # Need a better explanation of this
        required_vol = (
            self.sample_mass_kg
            / self.acid_conc_M
            * (
                H_conc_diff
                - carbonate_alk_diff
                - borate_alk_diff
                - self.KW
                * ((1 / H_conc_final) - (1 / H_conc_initial))
            )
        )
        return required_vol

    def gran_calc(self) -> Tuple[float, float, float]:
        """Give this a more explanatory name
        """
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
