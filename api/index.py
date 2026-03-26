from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# -----------------------------
# ROOT
# -----------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": True,
        "message": "API is running 🚀",
        "endpoints": {
            "MLBB": "/ml?id=USERID&zone=ZONE",
            "FREE FIRE": "/ff?id=USERID"
        }
    })


# -----------------------------
# MLBB CHECK
# -----------------------------
@app.route("/ml", methods=["GET"])
def check_ml():
    user_id = request.args.get("id")
    zone_id = request.args.get("zone")

    if not user_id or not zone_id:
        return jsonify({"status": False, "message": "Missing ID or Zone"}), 400

    try:
        url = "https://api.isan.eu.org/nickname/ml"
        res = requests.get(url, params={"id": user_id, "server": zone_id}, timeout=10)
        data = res.json()
        nickname = data.get("nickname") or data.get("name")

        if nickname:
            return jsonify({"status": True, "nickname": nickname})
        return jsonify({"status": False, "message": "User not found"}), 404

    except:
        return jsonify({"status": False, "message": "ML API failed"}), 500


# -----------------------------
# FREE FIRE CHECK
# -----------------------------
@app.route("/ff", methods=["GET"])
def check_ff():
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"status": False, "message": "Missing ID"}), 400

    apis = [
        f"https://api.isan.eu.org/nickname/ff?id={user_id}"
    ]

    for api in apis:
        try:
            res = requests.get(api, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
            if res.status_code != 200:
                continue
            data = res.json()
            nickname = data.get("nickname") or data.get("name") or (data.get("data") or {}).get("nickname")
            if nickname and str(nickname).strip() != "":
                return jsonify({"status": True, "nickname": nickname})
        except:
            continue

    return jsonify({"status": False, "message": "Nickname not found"}), 404
