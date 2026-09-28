import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from datetime import date

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import ScenarioInput
from ml.ml_forecast import predict_market_proxy
from port_observations import get_paradip_snapshot
from calculations import (calculate_stock_cover , calculate_projected_stock, calculate_days_until_arrival,
 calculate_freight_cost, calculate_insurance_cost, calculate_port_charges, calculate_expected_demurrage, calculate_landed_cost,
 calculate_inventory_status, generate_vessel_options, calculate_port_risk, calculate_confidence, generate_decision_summary)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "FreightIQ backend is running", "status": "ok"}


@app.get("/ml/market-proxy")
def market_proxy():
    try:
        return predict_market_proxy()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Forecast unavailable: {exc}") from exc


@app.get("/port-observations/paradip")
def paradip_observations():
    try:
        return get_paradip_snapshot()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Paradip report unavailable: {exc}") from exc




@app.post("/analyze")
def analyze_scenario(scenario: ScenarioInput):

    if scenario.laycan_start > scenario.laycan_end:
        raise HTTPException(
            status_code = 400,
            detail = "laycan_start must be before laycan_end"
        )


    if scenario.target_arrival < scenario.laycan_start:
        raise HTTPException(
            status_code=400,
            detail="target_arrival cannot be before laycan_start"
        )    
    stock_cover_days = calculate_stock_cover(
        scenario.inventory_tonnes,
        scenario.daily_consumption_tonnes
    )
    days_until_arrival = calculate_days_until_arrival(
    scenario.target_arrival
)

    projected_stock_tonnes = calculate_projected_stock(
    scenario.inventory_tonnes,
    scenario.daily_consumption_tonnes,
    days_until_arrival
)
    stockout_before_arrival = projected_stock_tonnes < 0
    freight_cost = calculate_freight_cost(scenario.cargo_volume_tonnes, scenario.freight_rate_per_tonne)
    insurance_cost = calculate_insurance_cost(scenario.cargo_value, scenario.insurance_rate)
    port_charges = calculate_port_charges(scenario.port_charge)
    expected_demurrage = calculate_expected_demurrage(scenario.expected_delay_days, scenario.demurrage_rate_per_day)
    if scenario.demurrage_free_days:
        expected_demurrage = max(0, scenario.expected_delay_days - scenario.demurrage_free_days) * scenario.demurrage_rate_per_day
    landed_cost = calculate_landed_cost(freight_cost, insurance_cost, port_charges, expected_demurrage)
    inventory_status = calculate_inventory_status(
        projected_stock_tonnes, 
    
    scenario.daily_consumption_tonnes, scenario.safety_buffer_days)
    vessel_options = generate_vessel_options(
        scenario.cargo_volume_tonnes,
        scenario.laycan_start,
        scenario.laycan_end,
        scenario.target_arrival,
        scenario.origin,
        scenario.destination_port,
        insurance_cost,
        port_charges,
        expected_demurrage
    )

    for option in vessel_options:
        option["inventory_buffer_days"] = stock_cover_days - calculate_days_until_arrival(
            date.fromisoformat(option["estimated_arrival"])
        )
        option["review_required"] = (
            not option["feasible"]
            or option["inventory_buffer_days"] < scenario.safety_buffer_days
            or calculate_port_risk(scenario.expected_delay_days)["risk_level"] == "HIGH"
        )

    eligible_options = [option for option in vessel_options if option["feasible"]]
    selected_option = min(eligible_options or vessel_options, key=lambda option: option["landed_cost"])
    for option in vessel_options:
        option["is_recommended"] = option["option_id"] == selected_option["option_id"]


    port_risk = calculate_port_risk(
        scenario.expected_delay_days
    )


    confidence = calculate_confidence(
        port_risk,
        vessel_options
    )

    decision_summary = generate_decision_summary(
        vessel_options,
        inventory_status,
        stockout_before_arrival,
        port_risk
    )
    return {
        "status": "success",

        "scenario": {
            "scenario_id": scenario.scenario_id,
            "commodity": scenario.commodity,
            "origin": scenario.origin,
            "destination_port": scenario.destination_port,
            "cargo_volume_tonnes": scenario.cargo_volume_tonnes,
            "target_arrival": scenario.target_arrival,
            "currency": scenario.currency
        },

        "inventory": {
            "data_label": "DERIVED",
            "stock_cover_days": stock_cover_days,
            "days_until_arrival": days_until_arrival,
            "projected_stock_tonnes": projected_stock_tonnes,
            "stockout_before_arrival": stockout_before_arrival,
            "status": inventory_status
        },

        "cost": {
            "data_label": "DERIVED",
            "freight_cost": freight_cost,
            "insurance_cost": insurance_cost,
            "port_charges": port_charges,
            "expected_demurrage": expected_demurrage,
            "landed_cost": landed_cost
        },

        "vessel_options": vessel_options,

        "port_risk": port_risk,

        "confidence": confidence,

        
    "decision": {
    "data_label": "DERIVED",
    **decision_summary
}
    }
