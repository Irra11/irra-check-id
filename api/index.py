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
# FREE FIRE SINGAPORE - MULTI-SOURCE
# -----------------------------
@app.route("/ff", methods=["GET"])
def check_ff_nickname():
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"status": False, "message": "Missing ID"}), 400

    # These are the 3 most reliable ways to check SG IDs
    sources = [
        # Source 1: Dedicated Singapore Path
        {"url": "https://api.isan.eu.org/nickname/ffsg", "params": {"id": user_id}},
        
        # Source 2: Regional Parameter Path
        {"url": "https://api.isan.eu.org/nickname/ff", "params": {"id": user_id, "region": "sg"}},
        
        # Source 3: Global/Other API
        {"url": "https://api.v8project.my.id/api/v1/game/ff", "params": {"id": user_id}}
    ]

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    for source in sources:
        try:
            res = requests.get(source["url"], params=source["params"], timeout=7, headers=headers)
            if res.status_code == 200:
                data = res.json()
                
                # Check all possible nickname locations in the JSON
                nickname = (
                    data.get("nickname") or 
                    data.get("name") or 
                    (data.get("result") if isinstance(data.get("result"), dict) else {}).get("nickname") or
                    (data.get("data") if isinstance(data.get("data"), dict) else {}).get("nickname")
                )

                if nickname and "not found" not in nickname.lower() and "invalid" not in nickname.lower():
                    return jsonify({"status": True, "nickname": nickname})
        except Exception as e:
            print(f"Source {source['url']} failed: {e}")
            continue # Try the next source in the list

    # If all 3 sources fail to find a name
    return jsonify({
        "status": False, 
        "message": "Player ID not found on Singapore server"
    }), 404
