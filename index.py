from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "9a7b56b6f5b919658a75bca363637638"

@app.route("/api/weather")
def weather():
    city = request.args.get("city", "Mumbai")

    url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "units": "metric",
        "appid": API_KEY
    }

    r = requests.get(url, params=params)
    return jsonify(r.json())


@app.route("/api/forecast")
def forecast():
    city = request.args.get("city", "Mumbai")

    url = f"https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "units": "metric",
        "appid": API_KEY
    }

    r = requests.get(url, params=params)
    return jsonify(r.json())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
