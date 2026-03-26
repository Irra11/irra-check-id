from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# -----------------------------
# ROOT ENDPOINT
# -----------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": True,
        "message": "IrraTopup FF-SG API 2026 Active 🚀",
        "author": "IrraTopup"
    })

# -----------------------------
# FREE FIRE SINGAPORE - 2026 PRO CHECK
# -----------------------------
@app.route("/ff", methods=["GET"])
def check_ff_nickname():
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"status": False, "message": "Missing ID"}), 400

    # These are the most stable API gateways for Singapore/Global in 2026
    api_sources = [
        # Source 1: Paxsenix Biz (Powerful 2026 Gateway)
        {"url": "https://api.paxsenix.biz.id/game/ff", "params": {"id": user_id}},
        
        # Source 2: Isan Dedicated SG Route
        {"url": "https://api.isan.eu.org/nickname/ffsg", "params": {"id": user_id}},
        
        # Source 3: Shizune (Updated 2026 path)
        {"url": "https://api.shizune.my.id/api/game/ff", "params": {"id": user_id}},
        
        # Source 4: Regional Force Path
        {"url": "https://api.isan.eu.org/nickname/ff", "params": {"id": user_id, "region": "sg"}}
    ]

    # Pro-Store Headers (Mimics official top-up platforms to bypass bot detection)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Referer": "https://www.codashop.com/",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9"
    }

    for source in api_sources:
        try:
            # 7-second timeout: long enough for SG server but quick for failover
            res = requests.get(source["url"], params=source["params"], timeout=7, headers=headers)
            
            if res.status_code == 200:
                data = res.json()
                
                # Check for 'status' within the API response itself if available
                if data.get("status") is False or data.get("success") is False:
                    continue

                # Multi-Path Nickname Parser for 2026
                nickname = (
                    data.get("nickname") or 
                    data.get("name") or 
                    (data.get("data") if isinstance(data.get("data"), dict) else {}).get("nickname") or
                    (data.get("result") if isinstance(data.get("result"), dict) else {}).get("nickname")
                )

                # Final Validation
                if nickname and len(str(nickname)) > 1:
                    name_str = str(nickname).lower()
                    # Filter common error messages returned as strings
                    bad_words = ["not found", "invalid", "error", "null", "busy", "failed"]
                    if not any(word in name_str for word in bad_words):
                        return jsonify({
                            "status": True,
                            "nickname": nickname,
                            "server": "Singapore/Global"
                        })
        except Exception:
            # Skip if API DNS is dead (NXDOMAIN) or times out
            continue

    # If all sources fail
    return jsonify({
        "status": False, 
        "message": "SG Server Busy. Please verify ID 2757260223 and try again."
    }), 404

# Local Test
if __name__ == "__main__":
    app.run(port=5000)
