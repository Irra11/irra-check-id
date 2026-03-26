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
# -----------------------------
# FREE FIRE SINGAPORE - NEW API (V8 & SHIZUNE)
# -----------------------------
@app.route("/ff", methods=["GET"])
def check_ff_nickname():
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"status": False, "message": "Missing ID"}), 400

    # These are NEW active APIs that support Singapore/Global IDs
    api_list = [
        # Source 1: V8 Project (Highly stable for SG/Global)
        {"url": "https://api.v8project.my.id/api/v1/game/ff", "params": {"id": user_id}},
        
        # Source 2: Shizune API (Newer provider)
        {"url": "https://api.shizune.my.id/api/game/ff", "params": {"id": user_id}},
        
        # Source 3: Isan FFSG path (Fallback)
        {"url": "https://api.isan.eu.org/nickname/ffsg", "params": {"id": user_id}}
    ]

    # Real Browser Headers to prevent blocking
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    for api in api_list:
        try:
            res = requests.get(api["url"], params=api["params"], timeout=10, headers=headers)
            
            if res.status_code == 200:
                data = res.json()
                
                # Check V8 structure: {"result": {"nickname": "..."}}
                # Check Shizune/Isan structure: {"nickname": "..."}
                nickname = (
                    (data.get("result") if isinstance(data.get("result"), dict) else {}).get("nickname") or
                    data.get("nickname") or 
                    data.get("name")
                )

                if nickname and len(nickname) > 1:
                    low_nick = nickname.lower()
                    # Filter out error messages returned as nicknames
                    if "not found" not in low_nick and "invalid" not in low_nick and "error" not in low_nick:
                        return jsonify({
                            "status": True,
                            "nickname": nickname
                        })
        except Exception as e:
            # Continue to next API if this one fails
            print(f"Log: {api['url']} failed.")
            continue

    return jsonify({
        "status": False, 
        "message": "ID not found. Please try again or check the ID."
    }), 404
