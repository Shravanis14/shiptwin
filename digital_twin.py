"""
ShipTwin - Digital Twin Engine
Member 1 owns this file (with Member 2 consuming its outputs).
"""

from data_model import FUEL_PRICE_PER_TON_USD, CHARTER_COST_PER_DAY_USD

CO2_PER_TON_FUEL = 3.114


def speed_factor(speed_knots, design_speed_knots):
    return (speed_knots / design_speed_knots) ** 3


def hull_factor(hull_fouling_pct):
    return 1 + (hull_fouling_pct / 100) * 0.30


def weather_factor(wave_height_m, headwind_knots):
    return 1 + (wave_height_m * 0.05) + (headwind_knots * 0.015)


def cargo_factor(cargo_load_pct):
    return 1 + ((cargo_load_pct - 50) / 100) * 0.12


def compute_voyage(ship, distance_nm, speed_knots, weather, cargo_load_pct,
                    hull_fouling_pct_override=None):
    fouling = (hull_fouling_pct_override
               if hull_fouling_pct_override is not None
               else ship["hull_fouling_pct"])

    sf = speed_factor(speed_knots, ship["design_speed_knots"])
    hf = hull_factor(fouling)
    wf = weather_factor(weather["wave_height_m"], weather["headwind_knots"])
    cf = cargo_factor(cargo_load_pct)

    fuel_rate_tons_per_day = ship["base_fuel_rate_tons_per_day"] * sf * hf * wf * cf
    time_days = distance_nm / (speed_knots * 24)
    fuel_used_tons = fuel_rate_tons_per_day * time_days
    co2_tons = fuel_used_tons * CO2_PER_TON_FUEL

    fuel_cost = fuel_used_tons * FUEL_PRICE_PER_TON_USD
    charter_cost = time_days * CHARTER_COST_PER_DAY_USD

    return {
        "time_days": round(time_days, 2),
        "fuel_used_tons": round(fuel_used_tons, 2),
        "co2_tons": round(co2_tons, 2),
        "fuel_cost_usd": round(fuel_cost, 2),
        "charter_cost_usd": round(charter_cost, 2),
        "total_cost_usd": round(fuel_cost + charter_cost, 2),
        "factors": {
            "speed_factor": round(sf, 3),
            "hull_factor": round(hf, 3),
            "weather_factor": round(wf, 3),
            "cargo_factor": round(cf, 3),
            "hull_fouling_pct_used": fouling,
        },
    }


if __name__ == "__main__":
    from data_model import get_ship, get_route, WEATHER_SCENARIOS

    ship = get_ship("SHIP001")
    route = get_route("R1")
    weather = WEATHER_SCENARIOS[1]

    result = compute_voyage(ship, route["distance_nm"], ship["design_speed_knots"],
                             weather, cargo_load_pct=70)
    print("Sample voyage calc:", result)