"""
ShipTwin - Carbon Compliance / IMO CII Score Module
Member 3 owns this file.
"""

CII_BANDS = [
    (0, 3.0, "A"),
    (3.0, 4.0, "B"),
    (4.0, 5.0, "C"),
    (5.0, 6.5, "D"),
    (6.5, float("inf"), "E"),
]

PENALTY_USD_BY_RATING = {
    "A": 0,
    "B": 0,
    "C": 5000,
    "D": 20000,
    "E": 50000,
}


def compute_cii(co2_tons, capacity_dwt, distance_nm):
    co2_grams = co2_tons * 1_000_000
    attained_cii = co2_grams / (capacity_dwt * distance_nm)
    for lower, upper, rating in CII_BANDS:
        if lower <= attained_cii < upper:
            return round(attained_cii, 3), rating
    return round(attained_cii, 3), "E"


def compliance_report(option, ship, route):
    attained_cii, rating = compute_cii(option["co2_tons"], ship["capacity_dwt"],
                                        route["distance_nm"])
    penalty = PENALTY_USD_BY_RATING[rating]
    return {
        "attained_cii": attained_cii,
        "cii_rating": rating,
        "penalty_usd": penalty,
        "total_cost_with_compliance_usd": round(option["total_cost_usd"] + penalty, 2),
    }


def attach_compliance(options, ship, route):
    for o in options:
        report = compliance_report(o, ship, route)
        o.update(report)
    return options


if __name__ == "__main__":
    from data_model import get_ship, get_route, WEATHER_SCENARIOS
    from decision_engine import generate_options, score_and_rank

    ship = get_ship("SHIP001")
    route = get_route("R1")
    weather = WEATHER_SCENARIOS[1]

    opts = generate_options(ship, route, weather, cargo_load_pct=70)
    opts = attach_compliance(opts, ship, route)
    ranked = score_and_rank(opts)

    for o in ranked:
        print(f"{o['option']}: CII={o['cii_rating']} penalty=${o['penalty_usd']} "
              f"total_with_compliance=${o['total_cost_with_compliance_usd']}")