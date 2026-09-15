"""
ShipTwin - Integration Layer (Flask API)
Member 5 owns this file.
Run with: python main.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

from data_model import SHIPS, ROUTES, WEATHER_SCENARIOS, get_ship, get_route
from decision_engine import generate_options, score_and_rank, top_contributing_factors
from compliance import attach_compliance

app = Flask(__name__)
CORS(app)


@app.route("/api/metadata", methods=["GET"])
def metadata():
    return jsonify({
        "ships": SHIPS,
        "routes": ROUTES,
        "weather_scenarios": WEATHER_SCENARIOS,
    })


@app.route("/api/decide", methods=["POST"])
def decide():
    data = request.get_json()
    ship = get_ship(data["ship_id"])
    route = get_route(data["route_id"])
    weather = WEATHER_SCENARIOS[int(data.get("weather_scenario_index", 0))]
    cargo_load_pct = float(data.get("cargo_load_pct", 70))

    options = generate_options(ship, route, weather, cargo_load_pct)
    options = attach_compliance(options, ship, route)
    ranked = score_and_rank(options)

    for o in ranked:
        o["why"] = top_contributing_factors(o)

    return jsonify({
        "ship": ship["name"],
        "route": f"{route['origin']} -> {route['destination']}",
        "weather": weather["scenario"],
        "recommended": ranked[0]["option"],
        "options": ranked,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)