from typing import Tuple

import numpy as np

from lib.utils import rsq

class ModifiedGranTitrationNew:
    def __init__(self, sample_mass: float, salinity: float, acid_conc: float,
                  temp: float, ph_initial: float, emf_initial: float) -> None:
        self.sample_mass = sample_mass / 1000 # why /1000?
        self.salinity = salinity
        self.acid_conc = acid_conc
        self.temp_C = temp
        self.temp_K = self.temp_C + 273.15
        self.ph_array = np.array([ph_initial])
        self.emf_array = np.array([emf_initial])
        self.volume_added = np.array([0])

    def get_ionic_strength(self) -> float:
        pass

    def get_pK1c(self) -> float:
        pass

    def get_pK2c(self) -> float:
        pass

    def get_lnKw(self) -> float:
        pass

    def get_lnKB(self) -> float:
        pass

    def get_required_acid_vol(self, target_ph: float) -> float:
        pass

    """Give this another name that's clearer about what it does"""
    def gran_calc(self) -> Tuple[float, float, float]:
        pass
