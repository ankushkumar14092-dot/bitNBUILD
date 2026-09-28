import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



from calculations import (
    calculate_stock_cover,
    calculate_projected_stock,
    calculate_freight_cost,
    calculate_insurance_cost,
    calculate_expected_demurrage,
    calculate_inventory_status,
    calculate_port_risk,
)


def test_stock_cover():
    result = calculate_stock_cover(45000, 2500)
    assert result == 18


def test_stock_cover_zero_consumption():
    try:
        calculate_stock_cover(45000, 0)
        assert False
    except ValueError:
        assert True


def test_projected_stock():
    result = calculate_projected_stock(45000, 2500, 4)
    assert result == 35000


def test_freight_cost():
    result = calculate_freight_cost(50000, 25)
    assert result == 1250000


def test_insurance_cost():
    result = calculate_insurance_cost(2000000, 0.005)
    assert result == 10000


def test_expected_demurrage():
    result = calculate_expected_demurrage(2, 15000)
    assert result == 30000


def test_inventory_status():
    result = calculate_inventory_status(10000, 2500, 5)
    assert result == "BELOW_SAFETY_BUFFER"


def test_port_risk():
    result = calculate_port_risk(2)

    assert result["risk_level"] == "MEDIUM"
    assert result["risk_score"] == 50
    assert result["risk_type"] == "PROXY"


def test_no_feasible_vessel_confidence():
    from calculations import calculate_confidence

    vessel_options = [
        {
            "feasible": False
        }
    ]

    port_risk = {
        "risk_type": "PROXY"
    }

    result = calculate_confidence(
        port_risk,
        vessel_options
    )

    assert result == "LOW"    




def test_high_delay_increases_demurrage():
    from calculations import calculate_expected_demurrage

    low_delay = calculate_expected_demurrage(2, 15000)
    high_delay = calculate_expected_demurrage(5, 15000)

    assert high_delay > low_delay
    assert high_delay == 75000