# Write unit tests for titration logic here
# Tests MUST start with `test_` for pytest to find them

import csv

import numpy as np

from lib.services.titration import gran

"""This block loads the example titration data into the
ModifiedGranTitration object before proceeding with testing.
"""
RAWDATA_FN = 'lib/services/titration/tests/testdata.csv'

rawdata = {}
with open(RAWDATA_FN) as f:
    read = csv.reader(f, delimiter=',')
    rowcount = 0
    for row in read:
        if rowcount == 0:
            rawdata['sample_mass_g'] = float(row[1])
        if rowcount == 1:
            rawdata['temp_C'] = float(row[1])
        if rowcount == 2:
            rawdata['salinity'] = float(row[1])
        if rowcount == 3:
            rawdata['emf_mV'] = [float(x) for x in row[1].split(',')]
        if rowcount == 4:
            rawdata['volume_added'] = [float(x) for x in row[1].split(',')]
        if rowcount == 5:
            rawdata['ph'] = [float(x) for x in row[1].split(',')]
        if rowcount == 6:
            rawdata['total_alk'] = float(row[1])
        rowcount += 1

    step_volumes = []
    for x in rawdata['volume_added']:
        idx = rawdata['volume_added'].index(x)
        if idx == 0:
            step_volumes.append(x)
            continue
        prev_step_vol = rawdata['volume_added'][idx-1]
        step_volumes.append(x - prev_step_vol)
    rawdata['step_volumes'] = step_volumes


titration = gran.ModifiedGranTitration(
                sample_mass=rawdata['sample_mass_g'],
                salinity=rawdata['salinity'],
                acid_conc=0.1,
                temp=rawdata['temp_C'],
                ph_initial=rawdata['ph'][0],
                emf_initial=rawdata['emf_mV'][0]
)


def test_init_attributes() -> None:
    """Test that the titration object loads the initial conditions.
    """
    assert titration.sample_mass_kg == rawdata['sample_mass_g'] / 1000
    assert titration.salinity == rawdata['salinity']
    assert titration.temp_C == rawdata['temp_C']
    assert titration.temp_K == rawdata['temp_C'] + 273.15
    assert titration.ph_array.size == 1
    assert titration.ph_array[0] == rawdata['ph'][0]
    assert titration.emf_array.size == 1
    assert titration.emf_array[0] == rawdata['emf_mV'][0]
    assert titration.volume_array.size == 1
    assert titration.volume_array[0] == 0

def test_getting_initial_data() -> None:
    """Test that the get_last methods return the most recent data point.
    """
    assert titration.get_last_ph() == rawdata['ph'][0]
    assert titration.get_last_emf() == rawdata['emf_mV'][0]
    assert titration.get_last_volume() == 0

def test_adding_step_data() -> None:
    """Test that, for each step of the simulated titration, the step data
    is added properly to the titration object.
    """
    stepdata = zip(rawdata['ph'][1:],
                   rawdata['emf_mV'][1:],
                   rawdata['step_volumes'][1:]
    )
    for (ph, emf, step_volume) in stepdata:
        last_total_volume = titration.get_last_volume()
        titration.add_step_data(ph, emf, step_volume)
        assert titration.get_last_ph() == ph
        assert titration.get_last_emf() == emf
        assert titration.get_last_volume() == last_total_volume + step_volume

def test_ionic_strength_calculation() -> None:
    """Test that the ionic strength calculation works as expected.
    """
    expected = 0.7013822308273712
    assert titration.calc_IS() == expected

def test_K1_calculation() -> None:
    """Test that the K1 equilibrium constant calculation works as expected.
    """
    expected = 1.3887690569727345e-6
    assert titration.calc_K1() == expected

def test_K2_calculation() -> None:
    """Test that the K2 equilibrium constant calculation works as expected.
    """
    expected = 1.0100523856322994e-9
    assert titration.calc_K2() == expected

def test_KW_calculation() -> None:
    """Test that the KW equilibrium constant calculation works as expected.
    """
    expected = 5.020316548371792e-14
    assert titration.calc_KW() == expected

def test_KB_calculation() -> None:
    """Test that the KB equilibrium constant calculation works as expected.
    """
    expected = 2.369939795066332e-09
    assert titration.calc_KB() == expected

def test_BT_calculation() -> None:
    """Test that the total borate calculation works as expected.
    """
    expected = 0.0004041142857142857
    assert titration.calc_BT() == expected

def test_DIC_calculation() -> None:
    """Test that the dissolved inorganic carbon calculation works as expected.
    """
    expected = 0.001991428571428572
    assert titration.calc_DIC() == expected

def test_H_concentration_calculation() -> None:
    """Test that the hydrogen ion concentration calculation works as expected.
    """
    expected = 0.00031622776601683794
    assert titration.calc_H_concentration(ph=3.5) == expected

def test_H_concentration_array_calculation() -> None:
    """Test that the hydrogen ion concentration calculation works as expected.
    """
    test_array = np.array([3.5, 6.5, 9.5])
    expected = np.array([0.00031622776601683794,
                         3.162277660168379e-07,
                         3.1622776601683795e-10])
    result_array = titration.calc_H_concentration_array(pharray=test_array)
    assert np.array_equal(result_array, expected)

def test_concentration_denom_calculation() -> None:
    """Test that the concentration denominator calculation works as expected.
    """
    expected = 1.5390420068814973e-14
    assert titration.calc_concentration_denominator(ph=8.0) == expected

def test_carbonate_alkalinity_calculation() -> None:
    """Test that the carbonate alkalinity calculation works as expected.
    """
    expected = 0.0021599939993848013
    assert titration.calc_carbonate_alkalinity(ph=8.0) == expected

def test_borate_alkalinity_calculation() -> None:
    """Test that the borate alkalinity calculation works as expected.
    """
    expected = 7.742370159724416e-05
    assert titration.calc_borate_alkalinity(ph=8.0) == expected

def test_required_acid_vol_calculation() -> None:
    """Test that the required acid volume calculation works as expected.
    """
    expected = 0.000723807918578496
    assert titration.calc_required_acid_vol(target_ph=2.5) == expected

def test_ygran_calculation() -> None:
    """Test that the y values of the regression are calculated properly.
    """
    volume_data = titration.volume_array[titration.ph_array < 3.8]
    ph_data = titration.ph_array[titration.ph_array < 3.8]
    expected = np.array([3.81653103, 3.7265705, 3.63659706, 3.54658725,
                          3.45655471, 3.3764654, 3.28636159, 3.19620847,
                          3.10599666, 3.01571523])
    result_array = titration.calc_ygran(volume_data, ph_data)
    assert np.allclose(result_array, expected)

def test_gran_polynomial_fit() -> None:
    """Test that the linear regression works as expected.
    """
    expected_TA = 2267.6036574069217
    expected_gamma = 0.89400469992681
    expected_rsq = 0.9996977669718775
    TA, gamma, rsq = titration.gran_polynomial_fit()

    assert TA == expected_TA
    assert gamma == expected_gamma
    assert rsq == expected_rsq
