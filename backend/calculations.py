from datetime import date, timedelta

def calculate_stock_cover(inventory_tonnes, daily_consumption_tonnes):
    if daily_consumption_tonnes <= 0:
        raise ValueError("Daily consumption must be greater than zero")

    return inventory_tonnes / daily_consumption_tonnes

def calculate_projected_stock(
    inventory_tonnes,
    daily_consumption_tonnes,
    days_until_arrival
):
    return inventory_tonnes - (
        daily_consumption_tonnes * days_until_arrival
    )

def calculate_days_until_arrival(target_arrival):
    arrival_date = target_arrival
    today = date.today()
    return (arrival_date - today).days

def calculate_freight_cost(cargo_volume_tonnes, freight_rate_per_tonne):
    return  cargo_volume_tonnes* freight_rate_per_tonne

def calculate_insurance_cost(cargo_value, insurance_rate):

    return cargo_value*insurance_rate    

def calculate_port_charges(port_charge):
    return port_charge    

def calculate_expected_demurrage(expected_delay_days, demurrage_rate_per_day):
    return expected_delay_days*demurrage_rate_per_day

def calculate_landed_cost(freight_cost, insurance_cost, port_charges, expected_demurrage):
    return (freight_cost + insurance_cost + port_charges + expected_demurrage)

def calculate_inventory_status(projected_stock_tonnes, daily_consumption_tonnes, safety_buffer_days):
    safety_buffer_tonnes = daily_consumption_tonnes*safety_buffer_days

    if projected_stock_tonnes < safety_buffer_tonnes:
        return  "BELOW_SAFETY_BUFFER"
       

    return " ABOVE_SAFETY_BUFFER"   


def generate_vessel_options(
    cargo_volume_tonnes,
    scenario_laycan_start,
    scenario_laycan_end,
    target_arrival,
    origin,
    destination_port,
    insurance_cost,
    port_charges,
    expected_demurrage,
    base_freight_rate,
    expected_delay_days
):
    # These are capacity and scenario-rate assumptions, not live vessel listings or quotes.
    candidates = [
        {"option_id": "A", "vessel_class": "Panamax", "capacity_tonnes": 82000,
         "rate_factor": 1.00, "laycan_offset_days": 0, "booking_lead_days": 10},
        {"option_id": "B", "vessel_class": "Supramax", "capacity_tonnes": 58000,
         "rate_factor": 1.08, "laycan_offset_days": 2, "booking_lead_days": 7},
        {"option_id": "C", "vessel_class": "Handysize", "capacity_tonnes": 40000,
         "rate_factor": 1.18, "laycan_offset_days": 4, "booking_lead_days": 5},
    ]
    transit_days = estimate_transit_days(origin, destination_port)
    options = []
    today = date.today()

    for candidate in candidates:
        laycan_start = scenario_laycan_start + timedelta(days=candidate["laycan_offset_days"])
        laycan_end = min(scenario_laycan_end, laycan_start + timedelta(days=2))
        booking_start = max(today, scenario_laycan_start - timedelta(days=candidate["booking_lead_days"]))
        booking_end = max(booking_start, scenario_laycan_start - timedelta(days=1))
        arrival = laycan_start + timedelta(days=transit_days + round(expected_delay_days))
        vessel_count = max(1, int((cargo_volume_tonnes + candidate["capacity_tonnes"] - 1) // candidate["capacity_tonnes"]))
        rate = round(base_freight_rate * candidate["rate_factor"], 2)
        freight_cost = calculate_freight_cost(cargo_volume_tonnes, rate)
        option_port_charges = port_charges * vessel_count
        option_demurrage = expected_demurrage * vessel_count
        candidate_options = {
            **candidate,
            "data_label": "SCENARIO_ASSUMPTION",
            "required_vessels": vessel_count,
            "laycan_start": laycan_start.isoformat(),
            "laycan_end": laycan_end.isoformat(),
            "booking_window_start": booking_start.isoformat(),
            "booking_window_end": booking_end.isoformat(),
            "estimated_arrival": arrival.isoformat(),
            "estimated_transit_days": transit_days,
            "expected_delay_days": round(expected_delay_days, 1),
            "freight_rate_per_tonne": rate,
            "freight_cost": freight_cost,
            "port_charges": option_port_charges,
            "expected_demurrage": option_demurrage,
            "landed_cost": calculate_landed_cost(
                freight_cost, insurance_cost, option_port_charges, option_demurrage
            ),
        }
        candidate_options["capacity_fit"] = True
        candidate_options["laycan_fit"] = calculate_laycan_fit(
            candidate_options["laycan_start"],
            candidate_options["laycan_end"],
            scenario_laycan_start,
            scenario_laycan_end,
        )
        candidate_options["arrival_fit"] = calculate_arrival_fit(
            candidate_options["estimated_arrival"], target_arrival
        )
        candidate_options["route_fit"] = calculate_route_fit(
            origin, destination_port, candidate["vessel_class"]
        )
        candidate_options["feasible"] = all(
            candidate_options[key]
            for key in ("capacity_fit", "laycan_fit", "arrival_fit", "route_fit")
        )

        reasons = [
            f"Rate uses your ${base_freight_rate:.2f}/MT planning assumption and a {candidate['rate_factor']:.2f} vessel-class factor"
        ]
        if vessel_count > 1:
            reasons.append(f"Cargo volume requires {vessel_count} vessels at this capacity")
        if not candidate_options["laycan_fit"]:
            reasons.append("Candidate loading window does not overlap the requested laycan")
        if not candidate_options["arrival_fit"]:
            reasons.append("Estimated arrival is after the required date")
        if not candidate_options["route_fit"]:
            reasons.append("Origin/destination combination is not supported")
        if candidate_options["feasible"]:
            reasons.append("Feasible under the supplied planning assumptions")
        candidate_options["reasons"] = reasons
        options.append(candidate_options)

    return options


def estimate_transit_days(origin, destination_port):
    origin_text = origin.strip().lower()
    if "indonesia" in origin_text or origin_text == "taboneo":
        days = 12
    elif "south africa" in origin_text or origin_text == "richards bay":
        days = 24
    elif "brazil" in origin_text or origin_text == "santos":
        days = 32
    elif "australia" in origin_text or origin_text == "newcastle":
        days = 18
    else:
        return 0

    destination = destination_port.strip().lower()
    if destination in {"paradip", "visakhapatnam", "chennai", "kolkata / haldia", "haldia"}:
        return days
    return 0



def calculate_laycan_fit(
    vessel_laycan_start,
    vessel_laycan_end,
    scenario_laycan_start,
    scenario_laycan_end
):
    vessel_start = date.fromisoformat(vessel_laycan_start)
    vessel_end = date.fromisoformat(vessel_laycan_end)

    scenario_start = (scenario_laycan_start)
    scenario_end = (scenario_laycan_end)

    return (
        vessel_start <= scenario_end
        and vessel_end >= scenario_start
    )

def calculate_port_risk(expected_delay_days):
    if expected_delay_days <= 1:
        risk_level = "LOW"
        risk_score = 20
    elif expected_delay_days <= 3:
        risk_level = "MEDIUM"
        risk_score = 50
    else:
        risk_level = "HIGH"
        risk_score = 80

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_type": "PROXY"
    }



def calculate_confidence(port_risk, vessel_options):
    feasible_options = [
        option for option in vessel_options
        if option["feasible"]
    ]

    if not feasible_options:
        return "LOW"

    if port_risk["risk_type"] == "PROXY":
        return "MEDIUM"

    return "HIGH"    


def generate_decision_summary(
    vessel_options,
    inventory_status,
    stockout_before_arrival,
    port_risk
):
    feasible_options = [
        option for option in vessel_options
        if option["feasible"]
    ]

    if not feasible_options:
        decision_status = "NO_FEASIBLE_OPTION"
    elif stockout_before_arrival:
        decision_status = "REVIEW_INVENTORY_RISK"
    elif inventory_status == "BELOW_SAFETY_BUFFER":
        decision_status = "REVIEW_INVENTORY_BUFFER"
    elif port_risk["risk_level"] == "HIGH":
        decision_status = "REVIEW_PORT_RISK"
    else:
        decision_status = "OPTIONS_AVAILABLE"

    reasons = []

    if stockout_before_arrival:
        reasons.append(
            "Projected inventory reaches stockout before target arrival"
        )

    if inventory_status == "BELOW_SAFETY_BUFFER":
        reasons.append(
            "Projected inventory is below the safety buffer"
        )

    if port_risk["risk_level"] == "HIGH":
        reasons.append(
            "Port delay risk is high"
        )

    if port_risk["risk_type"] == "PROXY":
        reasons.append(
            "Port risk is based on a transparent proxy"
        )

    if not feasible_options:
        reasons.append(
            "No feasible vessel option was found"
        )

    human_review_required = (
        stockout_before_arrival
        or inventory_status == "BELOW_SAFETY_BUFFER"
        or port_risk["risk_level"] == "HIGH"
        or not feasible_options
    )

    return {
        "decision_status": decision_status,
        "feasible_option_count": len(feasible_options),
        "reasons": reasons,
        "human_review_required": human_review_required
    }


def calculate_arrival_fit(
    estimated_arrival,
    target_arrival
):
    vessel_arrival = date.fromisoformat(estimated_arrival)
    target_date = (target_arrival)

    return vessel_arrival <= target_date


def calculate_route_fit(origin, destination_port, vessel_class):
    origin = origin.strip().lower()
    destination_port = destination_port.strip().lower()

    if origin == "australia" and destination_port == "paradip" :
        return True

    return False    
