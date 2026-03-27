from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# -----------------------------
# 2026 PRO HEADERS (Mimics UniPin Singapore)
# -----------------------------
SG_HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Referer": "https://www.unipin.com/sg/garena/free-fire",
    "Origin": "https://www.unipin.com",
    "Accept": "application/json"
}

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": True,
        "message": "IrraTopup 2026 API Gateway Active 🚀",
        "endpoints": ["/ml", "/ff"]
    })

# -----------------------------
# MLBB CHECKER
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
        return jsonify({"status": False, "message": "MLBB User not found"}), 404
    except:
        return jsonify({"status": False, "message": "MLBB Service Offline"}), 500

# -----------------------------
# FREE FIRE SINGAPORE CHECKER (2026 ANTI-BLIND)
# -----------------------------
@app.route("/ff", methods=["GET"])
def check_ff_nickname():
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"status": False, "message": "Missing ID"}), 400

    # These sources are prioritized for the Singapore (SG) Database
    api_sources = [
        # Source 1: Paxsenix Biz (Strongest 2026 SG gateway)
        # {"url": "https://api.paxsenix.biz.id/game/ff", "params": {"id": user_id, "region": "sg"}},
        
        # Source 2: Hennndra (Reliable Merchant Scraper)
        {"url": "https://api.hennndra.my.id/api/game/ff", "params": {"id": user_id}},
        
        # # Source 3: Kenz API (Stable Singapore provider)
        # {"url": "https://api.kenz.my.id/api/game/ff", "params": {"id": user_id}},
        
        # # Source 4: Dedicated SG Route
        # {"url": "https://api.isan.eu.org/nickname/ffsg", "params": {"id": user_id}}
    ]

    for source in api_sources:
        try:
            # 8-second timeout: SG gateways are under high load in 2026
            res = requests.get(source["url"], params=source["params"], timeout=8, headers=SG_HEADERS)
            
            if res.status_code == 200:
                data = res.json()
                
                # Check all common 2026 nickname locations
                nickname = (
                    data.get("nickname") or 
                    data.get("name") or 
                    (data.get("result") if isinstance(data.get("result"), dict) else {}).get("nickname") or
                    (data.get("data") if isinstance(data.get("data"), dict) else {}).get("nickname")
                )

                # --- 2026 ANTI-BLIND VALIDATION ---
                # 1. Ensure nickname is not empty
                # 2. Ensure nickname is not just the ID (Garena hides names by sending the ID instead)
                if nickname and str(nickname).strip() and str(nickname) != str(user_id):
                    name_clean = str(nickname).strip()
                    
                    # Filter out error text from APIs
                    bad_words = ["not found", "invalid", "error", "null", "busy", "limit", "failed", "hidden"]
                    if not any(word in name_clean.lower() for word in bad_words):
                        return jsonify({
                            "status": True,
                            "nickname": name_clean,
                            "id": user_id,
                            "server": "Singapore"
                        })
        except Exception:
            continue # Try next API immediately

    return jsonify({
        "status": False, 
        "message": "Name hidden by SG server security. Please try again in 5 minutes."
    }), 404

if __name__ == "__main__":
    app.run(port=5000)
