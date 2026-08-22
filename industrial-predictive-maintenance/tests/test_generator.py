import pytest
from src.generator.generator import MachineSimulator, MACHINE_PROFILES

def test_machine_profiles_exist():
    assert len(MACHINE_PROFILES) == 5
    assert "M-101" in MACHINE_PROFILES
    assert "M-102" in MACHINE_PROFILES

def test_reading_generation():
    simulator = MachineSimulator()
    for m_id in MACHINE_PROFILES.keys():
        reading = simulator.generate_reading(m_id)
        assert reading["machine_id"] == m_id
        assert "timestamp" in reading
        assert isinstance(reading["vibration"], float)
        assert isinstance(reading["temperature"], float)
        assert isinstance(reading["rpm"], (int, float))
        assert isinstance(reading["pressure"], float)

def test_degradation_drift():
    simulator = MachineSimulator()
    # Check that M-102 vibration drifts upward as degradation state increases
    initial_reading = simulator.generate_reading("M-102")
    
    # Manually increment degradation state to simulate drift
    simulator.degradation_states["M-102"] = 10.0
    drifted_reading = simulator.generate_reading("M-102")
    
    # Drifts should cause vibration and temp to increase significantly
    assert drifted_reading["vibration"] > initial_reading["vibration"]
    assert drifted_reading["temperature"] > initial_reading["temperature"]
