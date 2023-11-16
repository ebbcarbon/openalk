from typing import Tuple

import numpy as np

from lib.utils import regression

class ModifiedGranTitration:
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

    def get_last_volume(self) -> float:
        """Returns the volume reading from the most recent titration step.
        """
        return float(self.volume_array[-1])

    def get_last_ph(self) -> float:
        """Returns the pH reading from the most recent titration step.
        """
        return float(self.ph_array[-1])

    def get_last_emf(self) -> float:
        """Returns the emf reading from the most recent titration step.
        """
        return float(self.emf_array[-1])

    def add_step_data(self, ph: float, emf: float, volume: float) -> None:
        """Adds the pH/emf readings and volume of titrant added at
        each step to the proper arrays.
        """
        self.ph_array = np.append(self.ph_array, ph)
        self.emf_array = np.append(self.emf_array, emf)

        last_volume = self.get_last_volume()
        new_volume = last_volume + volume
        self.volume_array = np.append(self.volume_array, new_volume)

    def calc_IS(self) -> float:
        """Calculates ionic strength (IS) of the sample.
        """
        return (19.924 * self.salinity) / (1000 - (1.005 * self.salinity))

    def calc_K1(self) -> np.float64:
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

    def calc_K2(self) -> np.float64:
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

    def calc_KW(self) -> np.float64:
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

    def calc_KB(self) -> np.float64:
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

    def calc_H_concentration(self, ph: float) -> np.float64:
        """Calculates the hydrogen ion concentration at a particular pH.
        ***For individual floats only***
        """
        return np.power(10, -1 * ph)

    def calc_H_concentration_array(self, pharray: np.ndarray) -> np.ndarray:
        """Calculates the hydrogen ion concentration at a particular pH.
        ***For numpy arrays only***
        """
        return np.power(10, np.multiply(-1, pharray))

    def calc_concentration_denominator(self, ph: float) -> np.float64:
        """Calculates the common denominator term in the expressions
        for the concentrations of bicarbonate and carbonate:

                      [H+]^2 + K1*[H+] + K1*K2.
        """
        H_conc = self.calc_H_concentration(ph)
        return (H_conc**2) + (self.K1 * H_conc) + (self.K1 * self.K2)

    def calc_carbonate_alkalinity(self, ph: float) -> np.float64:
        """Calculates the carbonate alkalinity:

                        Ac = [HCO3] + 2[CO3],

        at a given pH using the estimated level of DIC.
        """
        H_conc = self.calc_H_concentration(ph)
        conc_denom = self.calc_concentration_denominator(ph)

        alpha_C1 = (self.K1 * H_conc) / conc_denom
        alpha_C2 = (self.K1 * self.K2) / conc_denom

        return self.DIC * (alpha_C1 + (2 * alpha_C2))

    def calc_borate_alkalinity(self, ph: float) -> np.float64:
        """Calculates the borate alkalinity:

                          Ab = [B(OH)4],

        at a given pH using the estimated level of total borate.
        """
        H_conc = self.calc_H_concentration(ph)
        return self.BT / (1 + (H_conc / self.KB))

    def calc_required_acid_vol(self, target_ph: float) -> float:
        """Calculates the volume of HCl required to lower the pH from
        the most recent pH reading to the target pH.

        ***Different calculations used in the original code for initial
        and final titrations
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
        return float(required_vol)

    def calc_ygran(self, pHs: np.ndarray, volumes: np.ndarray) -> np.ndarray:
        """
        """
        H_conc_array = self.calc_H_concentration_array(pHs)
        print(f"H_concentration_array: {H_conc_array}")

        adj_volumes = np.add(self.sample_mass_kg, volumes)

        # total moles of H+ at each step?
        return np.multiply(adj_volumes, H_conc_array)

    def gran_polynomial_fit(self) -> Tuple[float, float, float]:
        """Fits a polynomial of degree 1
        """

        # Take volumes of steps with ph under 3.8. Must be numpy arrays
        volumes = self.volume_array[self.ph_array < 3.8]
        print(f"Volume array: {volumes}")

        # Take ph of steps with ph under 3.8. Must be numpy arrays
        pHs = self.ph_array[self.ph_array < 3.8]
        print(f"pH array: {pHs}")

        ygran = self.calc_ygran(pHs, volumes)
        print(f"ygran: {ygran}")

        slope, intercept, x_model, y_model, rsq = regression.linear_regression(
                                                                volumes, ygran)
        print(f"Slope: {slope}, int: {intercept}, xModel: {x_model}, yModel: {y_model}, rsq: {rsq}")

        gamma = slope / self.acid_conc_M
        print(f"Gamma: {gamma}")

        # Veq: HCO3/H2CO3 equivalence point volume, volume HCl needed to
        # drive all HCO3 into H2CO3
        Veq = -1 * intercept / slope
        print(f"Veq: {Veq}")

        # Hansson/Jagner 1973 lists this as moles alkalinity/kg seawater?
        molIn = Veq * self.acid_conc_M
        print(f"molIn: {molIn}")

        TA = molIn / self.sample_mass_kg * 1e6
        print(f"TA: {TA}")

        return TA, gamma, rsq
