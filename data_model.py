"""
ShipTwin - Data Model / Simulated Dataset
Member 1 owns this file.
"""

import random

SHIPS = [
    {
        "ship_id": "SHIP001",
        "name": "MV Sagar Prabha",
        "type": "Bulk Carrier",
        "design_speed_knots": 14,
        "base_fuel_rate_tons_per_day": 28,
        "capacity_dwt": 45000,
        "hull_fouling_pct": 18,
        "days_since_hull_clean": 210,
    },
    {
        "ship_id": "SHIP002",
        "name": "MV Konkan Star",
        "type": "Container Feeder",
        "design_speed_knots": 16,
        "base_fuel_rate_tons_per_day": 22,
        "capacity_dwt": 18000,
        "hull_fouling_pct": 32,
        "days_since_hull_clean": 340,
    },
    {
        "ship_id": "SHIP003",
        "name": "MV Kandla Pearl",
        "type": "Tanker",
        "design_speed_knots": 13,
        "base_fuel_rate_tons_per_day": 25,
        "capacity_dwt": 38000,
        "hull_fouling_pct": 9,
        "days_since_hull_clean": 60,
    },
]

ROUTES = [
    {"route_id": "R1", "origin": "JNPT",   "destination": "Chennai", "distance_nm": 780,  "alt_distance_nm": 830, "alt_note": "deeper water, avoids monsoon swell"},
    {"route_id": "R2", "origin": "Mundra",  "destination": "Kandla",  "distance_nm": 95,   "alt_distance_nm": 110, "alt_note": "avoids shallow sandbar delay"},
    {"route_id": "R3", "origin": "Chennai", "destination": "Kandla",  "distance_nm": 1450, "alt_distance_nm": 1510,"alt_note": "coastal hugging route, calmer seas"},
    {"route_id": "R4", "origin": "JNPT",    "destination": "Mundra",  "distance_nm": 310,  "alt_distance_nm": 340, "alt_note": "avoids port congestion zone near Pipavav"},
]

WEATHER_SCENARIOS = [
    {"scenario": "calm",          "wave_height_m": 0.5, "headwind_knots": 2},
    {"scenario": "moderate_sea",  "wave_height_m": 1.8, "headwind_knots": 8},
    {"scenario": "monsoon_rough", "wave_height_m": 3.2, "headwind_knots": 18},
]

FUEL_PRICE_PER_TON_USD = 620
CHARTER_COST_PER_DAY_USD = 9500
HULL_CLEAN_COST_USD = 45000
HULL_CLEAN_DOWNTIME_DAYS = 1.5
PORT_DEMURRAGE_PER_DAY_USD = 12000


def get_ship(ship_id):
    return next(s for s in SHIPS if s["ship_id"] == ship_id)


def get_route(route_id):
    return next(r for r in ROUTES if r["route_id"] == route_id)


def random_scenario():
    return {
        "ship": random.choice(SHIPS),
        "route": random.choice(ROUTES),
        "weather": random.choice(WEATHER_SCENARIOS),
        "cargo_load_pct": random.randint(40, 95),
    }


if __name__ == "__main__":
    print("Ships:", [s["name"] for s in SHIPS])
    print("Routes:", [r["route_id"] for r in ROUTES])
    print("Sample scenario:", random_scenario())