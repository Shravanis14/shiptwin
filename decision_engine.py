"""
ShipTwin - Decision Engine
Member 2 owns this file.
"""

from digital_twin import compute_voyage
from data_model import (HULL_CLEAN_COST_USD, HULL_CLEAN_DOWNTIME_DAYS,
                         CHARTER_COST_PER_DAY_USD)


def generate_options(ship, route, weather, cargo_load_pct):
    design_speed = ship["design_speed_knots"]
    options = []

    base = compute_voyage(ship, route["distance_nm"], design_speed, weather, cargo_load_pct)
    options.append({
        "option": "Continue as-is",
        **base,
        "notes": "No changes to route, speed, or hull.",
    })

    calmer_weather = {"wave_height_m": weather["wave_height_m"] * 0.6,
                       "headwind_knots": weather["headwind_knots"] * 0.7}
    reroute = compute_voyage(ship, route["alt_distance_nm"], design_speed,
                              calmer_weather, cargo_load_pct)
    options.append({
        "option": f"Reroute ({route['alt_note']})",
        **reroute,
        "notes": f"+{route['alt_distance_nm'] - route['distance_nm']} nm distance, but calmer conditions.",
    })

    slow_speed = design_speed * 0.85
    slow = compute_voyage(ship, route["distance_nm"], slow_speed, weather, cargo_load_pct)
    options.append({
        "option": f"Slow down to {slow_speed:.1f} kn",
        **slow,
        "notes": "Reduced speed cuts fuel burn but adds transit time.",
    })

    clean_voyage = compute_voyage(ship, route["distance_nm"], design_speed, weather,
                                   cargo_load_pct, hull_fouling_pct_override=2)
    clean_voyage["total_cost_usd"] = round(
        clean_voyage["total_cost_usd"] + HULL_CLEAN_COST_USD
        + HULL_CLEAN_DOWNTIME_DAYS * CHARTER_COST_PER_DAY_USD, 2)
    clean_voyage["time_days"] = round(clean_voyage["time_days"] + HULL_CLEAN_DOWNTIME_DAYS, 2)
    options.append({
        "option": "Hull clean now, then sail",
        **clean_voyage,
        "notes": (f"Adds ${HULL_CLEAN_COST_USD:,} cleaning cost + "
                  f"{HULL_CLEAN_DOWNTIME_DAYS} days downtime, but cuts fuel for "
                  f"this AND future voyages."),
    })

    fast_speed = design_speed * 1.10
    fast = compute_voyage(ship, route["distance_nm"], fast_speed, weather, cargo_load_pct)
    options.append({
        "option": f"Speed up to {fast_speed:.1f} kn",
        **fast,
        "notes": "Faster arrival, but cubic fuel penalty makes this costly.",
    })

    return options


def score_and_rank(options, weight_cost=0.5, weight_time=0.2, weight_co2=0.3):
    max_cost = max(o["total_cost_usd"] for o in options)
    max_time = max(o["time_days"] for o in options)
    max_co2 = max(o["co2_tons"] for o in options)

    for o in options:
        norm_cost = o["total_cost_usd"] / max_cost
        norm_time = o["time_days"] / max_time
        norm_co2 = o["co2_tons"] / max_co2
        o["score"] = round(
            weight_cost * norm_cost + weight_time * norm_time + weight_co2 * norm_co2, 4)

    ranked = sorted(options, key=lambda o: o["score"])
    for i, o in enumerate(ranked, start=1):
        o["rank"] = i
    return ranked


def top_contributing_factors(option):
    f = option["factors"]
    reasons = []
    if f["hull_factor"] > 1.05:
        reasons.append(f"Hull fouling ({f['hull_fouling_pct_used']}%) adding drag")
    if f["weather_factor"] > 1.1:
        reasons.append("Rough weather increasing resistance")
    if f["speed_factor"] > 1.0:
        reasons.append("Higher speed driving cubic fuel increase")
    if f["cargo_factor"] > 1.05:
        reasons.append("Heavy cargo load increasing displacement")
    if not reasons:
        reasons.append("Near-baseline conditions, no major penalty factor")
    return reasons[:3]


if __name__ == "__main__":
    from data_model import get_ship, get_route, WEATHER_SCENARIOS

    ship = get_ship("SHIP002")
    route = get_route("R3")
    weather = WEATHER_SCENARIOS[2]

    opts = generate_options(ship, route, weather, cargo_load_pct=80)
    ranked = score_and_rank(opts)

    for o in ranked:
        print(f"#{o['rank']} {o['option']} | cost=${o['total_cost_usd']} "
              f"time={o['time_days']}d CO2={o['co2_tons']}t score={o['score']}")
        print("   why:", top_contributing_factors(o))