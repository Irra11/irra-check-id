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
@app.route("/ff", methods=["GET"])
def check_ff_nickname():
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"status": False, "message": "Missing ID"}), 400

    try:
        # 1. Use a more modern browser User-Agent to avoid being blocked
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }
        url = "https://api.isan.eu.org/nickname/ff"
        
        # 2. Call the API with an 8-second timeout
        res = requests.get(url, params={"id": user_id}, timeout=8, headers=headers)
        
        # If API gives error status
        if res.status_code != 200:
            return jsonify({"status": False, "message": f"API Error {res.status_code}"}), res.status_code

        data = res.json()

        # 3. Robust Nickname Picker (Checks all possible keys)
        # Some versions return 'name', some 'nickname', some 'data': {'nickname': ...}
        nickname = (
            data.get("nickname") or 
            data.get("name") or 
            (data.get("data") if isinstance(data.get("data"), dict) else {}).get("nickname") or
            (data.get("result") if isinstance(data.get("result"), dict) else {}).get("nickname")
        )

        if nickname:
            return jsonify({
                "status": True, 
                "nickname": nickname
            })
        else:
            # Helpful for debugging in Vercel logs if it fails
            print(f"FF Debug: API returned structure: {data}")
            return jsonify({"status": False, "message": "Player ID not found"}), 404

    except requests.exceptions.Timeout:
        return jsonify({"status": False, "message": "Connection timed out"}), 504
    except Exception as e:
        return jsonify({"status": False, "message": f"Server Error: {str(e)}"}), 500
