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
# FREE FIRE SINGAPORE - STABLE MULTI-API
# -----------------------------
@app.route("/ff", methods=["GET"])
def check_ff_nickname():
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"status": False, "message": "Missing ID"}), 400

    # These APIs are ONLINE and stable for Singapore/Global IDs
    # I have removed the dead 'v8project' domain
    api_sources = [
        # Source 1: Lexxy API (Stable)
        {"url": "https://api.lexxy.my.id/api/check/ff", "params": {"id": user_id}},
        
        # Source 2: RZKY API (Excellent for SG/Global)
        {"url": "https://api.rzkyfdl.my.id/api/check/ff", "params": {"id": user_id}},
        
        # Source 3: M-Pedia API (Backup)
        {"url": "https://api.m-pedia.my.id/api/v1/game/ff", "params": {"id": user_id}},
        
        # Source 4: Isan SG path
        {"url": "https://api.isan.eu.org/nickname/ffsg", "params": {"id": user_id}}
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "application/json"
    }

    for source in api_sources:
        try:
            # We use a 5-second timeout so it moves quickly if an API is down
            res = requests.get(source["url"], params=source["params"], timeout=5, headers=headers)
            
            if res.status_code == 200:
                data = res.json()
                
                # Extract nickname (Handling different JSON structures)
                nickname = (
                    data.get("nickname") or 
                    data.get("name") or 
                    (data.get("data") if isinstance(data.get("data"), dict) else {}).get("nickname") or
                    (data.get("result") if isinstance(data.get("result"), dict) else {}).get("nickname")
                )

                # Filter out "Invalid" or "Not Found" text returned as a name
                if nickname and len(str(nickname)) > 2:
                    low_nick = str(nickname).lower()
                    if "not found" not in low_nick and "invalid" not in low_nick and "error" not in low_nick:
                        return jsonify({
                            "status": True,
                            "nickname": nickname
                        })
        except Exception as e:
            # If the site is down (NXDOMAIN) or timed out, just skip to the next source
            continue

    return jsonify({
        "status": False, 
        "message": "All servers are busy. Please check the ID or try again in 1 minute."
    }), 404
