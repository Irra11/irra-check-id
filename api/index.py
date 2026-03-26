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
## -----------------------------
# FREE FIRE SINGAPORE - PRO CHECK
# -----------------------------
@app.route("/ff", methods=["GET"])
def check_ff_nickname():
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"status": False, "message": "Missing ID"}), 400

    # These endpoints are currently the most stable for SG/Global
    sources = [
        # Source 1: The direct Singapore Merchant path
        "https://api.isan.eu.org/nickname/ffsg",
        # Source 2: The standard path with region force
        "https://api.isan.eu.org/nickname/ff",
        # Source 3: Backup Global Checker
        "https://sandipanmaji.tech/ff/api.php"
    ]

    # REAL MOBILE HEADERS (Helps bypass "Not Found" errors)
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Accept": "application/json",
        "Referer": "https://codashop.com/"
    }

    for url in sources:
        try:
            # Prepare params based on the URL type
            params = {"id": user_id}
            if "region" not in url and url == "https://api.isan.eu.org/nickname/ff":
                params["region"] = "sg"

            res = requests.get(url, params=params, timeout=8, headers=headers)
            
            if res.status_code == 200:
                data = res.json()
                
                # Check all possible locations for the nickname
                nickname = (
                    data.get("nickname") or 
                    data.get("name") or 
                    (data.get("result") if isinstance(data.get("result"), dict) else {}).get("nickname") or
                    (data.get("data") if isinstance(data.get("data"), dict) else {}).get("nickname")
                )

                # Validate the nickname isn't an error message
                if nickname and len(nickname) > 1:
                    low_nick = nickname.lower()
                    if "not found" not in low_nick and "invalid" not in low_nick and "error" not in low_nick:
                        return jsonify({
                            "status": True,
                            "nickname": nickname,
                            "source": "verified"
                        })
        except Exception as e:
            continue

    return jsonify({
        "status": False, 
        "message": "ID 2757260223 not found. Make sure it's the Singapore Server."
    }), 404
