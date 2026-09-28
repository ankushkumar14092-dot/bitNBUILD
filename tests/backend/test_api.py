import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_analyze_success():
    response = client.post(
        "/analyze",
        json={
            "scenario_id": "demo-001",
            "commodity": "Coal",
            "cargo_volume_tonnes": 50000,
            "origin": "Australia",
            "destination_port": "Paradip",
            "laycan_start": "2026-10-10",
            "laycan_end": "2026-10-20",
            "target_arrival": "2026-10-28",
            "inventory_tonnes": 45000,
            "daily_consumption_tonnes": 2500,
            "safety_buffer_days": 5,
            "currency": "USD",
            "freight_rate_per_tonne": 25,
            "cargo_value": 2000000,
            "insurance_rate": 0.005,
            "port_charge": 50000,
            "expected_delay_days": 2,
            "demurrage_rate_per_day": 15000
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["inventory"]["stock_cover_days"] == 18
    assert data["cost"]["landed_cost"] == 1340000
    assert data["port_risk"]["risk_type"] == "PROXY"
    assert data["decision"]["human_review_required"] is True



def test_stockout_before_arrival():
    response = client.post(
        "/analyze",
        json={
            "scenario_id": "stockout-test",
            "commodity": "Coal",
            "cargo_volume_tonnes": 50000,
            "origin": "Australia",
            "destination_port": "Paradip",
            "laycan_start": "2026-10-10",
            "laycan_end": "2026-10-20",
            "target_arrival": "2026-10-28",
            "inventory_tonnes": 45000,
            "daily_consumption_tonnes": 2500,
            "safety_buffer_days": 5,
            "currency": "USD",
            "freight_rate_per_tonne": 25,
            "cargo_value": 2000000,
            "insurance_rate": 0.005,
            "port_charge": 50000,
            "expected_delay_days": 2,
            "demurrage_rate_per_day": 15000
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["inventory"]["stockout_before_arrival"] is True
    assert data["inventory"]["projected_stock_tonnes"] == -32500
    assert data["decision"]["human_review_required"] is True




def test_invalid_target_arrival_date():
    response = client.post(
        "/analyze",
        json={
            "scenario_id": "invalid-date-test",
            "commodity": "Coal",
            "cargo_volume_tonnes": 50000,
            "origin": "Australia",
            "destination_port": "Paradip",
            "laycan_start": "2026-10-10",
            "laycan_end": "2026-10-20",
            "target_arrival": "2026-99-99",
            "inventory_tonnes": 45000,
            "daily_consumption_tonnes": 2500,
            "safety_buffer_days": 5,
            "currency": "USD",
            "freight_rate_per_tonne": 25,
            "cargo_value": 2000000,
            "insurance_rate": 0.005,
            "port_charge": 50000,
            "expected_delay_days": 2,
            "demurrage_rate_per_day": 15000
        }
    )

    assert response.status_code == 422

def test_negative_freight_rate_rejected():
    response = client.post(
        "/analyze",
        json={
            "scenario_id": "negative-rate-test",
            "commodity": "Coal",
            "cargo_volume_tonnes": 50000,
            "origin": "Australia",
            "destination_port": "Paradip",
            "laycan_start": "2026-10-10",
            "laycan_end": "2026-10-20",
            "target_arrival": "2026-10-28",
            "inventory_tonnes": 45000,
            "daily_consumption_tonnes": 2500,
            "safety_buffer_days": 5,
            "currency": "USD",
            "freight_rate_per_tonne": -25,
            "cargo_value": 2000000,
            "insurance_rate": 0.005,
            "port_charge": 50000,
            "expected_delay_days": 2,
            "demurrage_rate_per_day": 15000
        }
    )

    assert response.status_code == 422


def test_zero_cargo_rejected():
    response = client.post(
        "/analyze",
        json={
            "scenario_id": "zero-cargo-test",
            "commodity": "Coal",
            "cargo_volume_tonnes": 0,
            "origin": "Australia",
            "destination_port": "Paradip",
            "laycan_start": "2026-10-10",
            "laycan_end": "2026-10-20",
            "target_arrival": "2026-10-28",
            "inventory_tonnes": 45000,
            "daily_consumption_tonnes": 2500,
            "safety_buffer_days": 5,
            "currency": "USD",
            "freight_rate_per_tonne": 25,
            "cargo_value": 2000000,
            "insurance_rate": 0.005,
            "port_charge": 50000,
            "expected_delay_days": 2,
            "demurrage_rate_per_day": 15000
        }
    )

    assert response.status_code == 422



def test_at_least_three_vessel_options():
    response = client.post(
        "/analyze",
        json={
            "scenario_id": "vessel-options-test",
            "commodity": "Coal",
            "cargo_volume_tonnes": 50000,
            "origin": "Australia",
            "destination_port": "Paradip",
            "laycan_start": "2026-10-10",
            "laycan_end": "2026-10-20",
            "target_arrival": "2026-10-28",
            "inventory_tonnes": 45000,
            "daily_consumption_tonnes": 2500,
            "safety_buffer_days": 5,
            "currency": "USD",
            "freight_rate_per_tonne": 25,
            "cargo_value": 2000000,
            "insurance_rate": 0.005,
            "port_charge": 50000,
            "expected_delay_days": 2,
            "demurrage_rate_per_day": 15000
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["vessel_options"]) >= 3


def test_port_risk_is_labeled_as_proxy():
    response = client.post(
        "/analyze",
        json={
            "scenario_id": "risk-label-test",
            "commodity": "Coal",
            "cargo_volume_tonnes": 50000,
            "origin": "Australia",
            "destination_port": "Paradip",
            "laycan_start": "2026-10-10",
            "laycan_end": "2026-10-20",
            "target_arrival": "2026-10-28",
            "inventory_tonnes": 45000,
            "daily_consumption_tonnes": 2500,
            "safety_buffer_days": 5,
            "currency": "USD",
            "freight_rate_per_tonne": 25,
            "cargo_value": 2000000,
            "insurance_rate": 0.005,
            "port_charge": 50000,
            "expected_delay_days": 2,
            "demurrage_rate_per_day": 15000
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["port_risk"]["risk_type"] == "PROXY"