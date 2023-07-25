import numpy as np
from . import RSQ


class Titration(object):
    def __init__(self, sampleSize, S, T, pHs, emf, volumeAdded):
        self.sampleSize = sampleSize / 1000
        self.S = S
        self.T = T + 273.15
        self.pHs = pHs
        self.emf = emf
        self.volumeAdded = volumeAdded

    def requiredVol(self, Cacid, pHf):

        I = 19.924 * self.S / (1000 - 1.005 * self.S)  # ionic strength
        pK1c = (
            3670.7 / self.T
            - 62.008
            + 9.7944 * np.log(self.T)
            - 0.0118 * self.S
            + 0.000116 * (self.S ** 2)
        )  # H2CO3  --> H + HCO3 (Mehrbach 1973 refitted by Dickson and Millero 1987)
        pK2c = (
            1394.7 / self.T + 4.777 - 0.0184 * self.S + 0.000118 * (self.S ** 2)
        )  # HCO3   --> H + CO3  (Mehrbach 1973 refitted by Dickson and Millero 1987F)
        lnKw = (
            148.96502
            - 13847.26 / self.T
            - 23.6521 * np.log(self.T)
            + (118.67 / self.T - 5.977 + 1.0495 * np.log(self.T)) * (self.S ** 0.5)
            - 0.01615 * self.S
        )  # (DOE 1994)
        lnKB = (
            (
                -8966.90
                - 2890.53 * (self.S ** 0.5)
                - 77.942 * self.S
                + 1.728 * (self.S ** 1.5)
                - 0.0996 * (self.S ** 2)
            )
            / self.T
            + 148.0248
            + 137.1942 * (self.S ** 0.5)
            + 1.62142 * self.S
            - (24.4344 + 25.085 * (self.S ** 0.5) + 0.2474 * self.S) * np.log(self.T)
            + 0.053105 * (self.S ** 0.5) * self.T
        )

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

    def granCalc(self, Cacid):

        volumes = self.volumeAdded[self.pHs < 3.8]  # need to be numpy arrays
        pHs = self.pHs[self.pHs < 3.8]
        pH_modified = np.power(10, np.multiply(-1, pHs))

        ygran = np.multiply(np.add(self.sampleSize, volumes), pH_modified)

        slope, intercept, xModel, yModel, rsquare = RSQ.RSQ(volumes, ygran)
        gamma = slope / Cacid
        Veq = -1 * intercept / slope
        molIn = Veq * Cacid

        TA = molIn / self.sampleSize * 1000000

        return TA, gamma, rsquare
