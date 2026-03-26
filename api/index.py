from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# ------------------------------
# Free Fire UID check endpoint
# ------------------------------
@app.route("/ff", methods=["GET"])
def check_ff_nickname():
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"status": False, "message": "Missing ID"}), 400

    try:
        # Garena UID check API (isan.eu.org)
        url = "https://api.isan.eu.org/nickname/ff"
        params = {"id": user_id}
        headers = {"User-Agent": "Mozilla/5.0"}  # some APIs require UA

        response = requests.get(url, params=params, timeout=10, headers=headers)
        data = response.json()

        # Extract nickname
        nickname = (
            data.get("nickname") or
            data.get("name") or
            (data.get("data") or {}).get("nickname")
        )

        if nickname:
            return jsonify({"status": True, "nickname": nickname})

        return jsonify({"status": False, "message": "Nickname not found (API failed or UID invalid)"}), 404

    except Exception as e:
        return jsonify({"status": False, "message": "FF API failed", "error": str(e)}), 500

# ------------------------------
# Optional: MLBB endpoint
# ------------------------------
@app.route("/ml", methods=["GET"])
def check_ml_nickname():
    user_id = request.args.get("id")
    zone_id = request.args.get("zone")

    if not user_id or not zone_id:
        return jsonify({"status": False, "message": "Missing ID or Zone"}), 400

    try:
        url = "https://api.isan.eu.org/nickname/ml"
        params = {"id": user_id, "server": zone_id}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        nickname = data.get("nickname") or data.get("name")
        if nickname:
            return jsonify({"status": True, "nickname": nickname})
        return jsonify({"status": False, "message": "User not found"}), 404

    except Exception as e:
        return jsonify({"status": False, "error": str(e)}), 500

# No app.run() for Vercel; for local testing:
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
