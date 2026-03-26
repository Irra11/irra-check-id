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
# FREE FIRE CHECK (Improved)
# -----------------------------
# -----------------------------
# FREE FIRE SINGAPORE CHECK
# -----------------------------
@app.route("/ff", methods=["GET"])
def check_ff_nickname():
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"status": False, "message": "Missing ID"}), 400

    try:
        # URL for the Singapore region
        url = "https://api.isan.eu.org/nickname/ff"
        
        # We add region='sg' to force the Singapore server check
        params = {
            "id": user_id,
            "region": "sg" 
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        res = requests.get(url, params=params, timeout=10, headers=headers)
        data = res.json()

        # The API usually returns 'name' or 'nickname'
        nickname = data.get("name") or data.get("nickname")

        if nickname:
            return jsonify({
                "status": True,
                "nickname": nickname
            })
        else:
            # If still not found, return the API's own message
            error_msg = data.get("message") or "ID not found on Singapore server"
            return jsonify({"status": False, "message": error_msg}), 404

    except Exception as e:
        return jsonify({"status": False, "message": f"Server Error: {str(e)}"}), 500
