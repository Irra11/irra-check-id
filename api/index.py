from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": True,
        "message": "MLBB Cambodia Checker 🇰🇭",
        "endpoint": "/ml?id=USERID&zone=ZONEID"
    })

# -----------------------------
# CAMBODIA FILTER (SEA ZONES)
# -----------------------------
# These are common SEA zones (KH, VN, TH, ID, MY, PH mixed)
# You can adjust this list
ALLOWED_ZONES = [
    "4000","5000","6000","7000","8000","9000",
    "1000","2000","3000"
]

@app.route("/ml", methods=["GET"])
def check_ml():
    user_id = request.args.get("id")
    zone_id = request.args.get("zone")

    # ❌ Missing input
    if not user_id or not zone_id:
        return jsonify({
            "status": False,
            "message": "Missing ID or Zone"
        }), 400

    # ❌ Block non-Cambodia zones (simulation)
    if zone_id not in ALLOWED_ZONES:
        return jsonify({
            "status": False,
            "message": "Only Cambodia/SEA accounts allowed"
        }), 403

    try:
        url = "https://api.isan.eu.org/nickname/ml"

        res = requests.get(url, params={
            "id": user_id,
            "server": zone_id
        }, timeout=6)

        data = res.json()

        nickname = data.get("nickname") or data.get("name")

        # ✅ VALIDATION
        if nickname and str(nickname) != str(user_id):
            return jsonify({
                "status": True,
                "nickname": nickname.strip(),
                "id": user_id,
                "zone": zone_id,
                "region": "Cambodia"
            })

        return jsonify({
            "status": False,
            "message": "Player not found"
        }), 404

    except requests.exceptions.Timeout:
        return jsonify({
            "status": False,
            "message": "API timeout"
        }), 504

    except Exception:
        return jsonify({
            "status": False,
            "message": "Service error"
        }), 500


if __name__ == "__main__":
    app.run(port=5000)
