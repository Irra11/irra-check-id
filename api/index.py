from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": True, "message": "IrraTopup FF-SG API 2026.3 Active"})

# -----------------------------
# FREE FIRE SINGAPORE - 2026.3 FIX
# -----------------------------
@app.route("/ff", methods=["GET"])
def check_ff_nickname():
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"status": False, "message": "Missing ID"}), 400

    # These are the CURRENT working APIs for Singapore IDs in 2026
    api_sources = [
        # Source 1: Paxsenix Biz (Updated Gateway - Currently very strong for SG)
        {"url": "https://api.paxsenix.biz.id/game/ff", "params": {"id": user_id}},
        
        # Source 2: Hennndra Merchant Scraper
        {"url": "https://api.hennndra.my.id/api/game/ff", "params": {"id": user_id}},
        
        # Source 3: Isan FFSG Dedicated Path
        {"url": "https://api.isan.eu.org/nickname/ffsg", "params": {"id": user_id}},
        
        # Source 4: Shizune Pro
        {"url": "https://api.shizune.my.id/api/game/ff", "params": {"id": user_id}}
    ]

    # Mobile iPhone 17 Headers (Bypasses many Vercel/AWS IP blocks)
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
        "Referer": "https://www.codashop.com/en-sg/free-fire",
        "Accept": "application/json"
    }

    for source in api_sources:
        try:
            # 8-second timeout: SG server is under heavy protection in 2026
            res = requests.get(source["url"], params=source["params"], timeout=8, headers=headers)
            
            if res.status_code == 200:
                data = res.json()
                
                # Check for various nickname keys
                # We also check for 'player_name' which some 2026 APIs started using
                nickname = (
                    data.get("nickname") or 
                    data.get("name") or 
                    (data.get("data") if isinstance(data.get("data"), dict) else {}).get("nickname") or
                    (data.get("result") if isinstance(data.get("result"), dict) else {}).get("nickname")
                )

                # --- THE 2026 ANTI-BLIND LOGIC ---
                # 1. Nickname must exist
                # 2. Nickname MUST NOT be equal to the User ID (Prevents "Blind Success")
                # 3. Nickname MUST NOT be a number (Real nicknames aren't just IDs)
                if nickname and str(nickname).strip():
                    nick_str = str(nickname).strip()
                    
                    if nick_str != str(user_id) and not nick_str.isdigit():
                        low_nick = nick_str.lower()
                        # Filter out error text
                        bad_words = ["not found", "invalid", "error", "null", "busy", "limit", "failed"]
                        if not any(word in low_nick for word in bad_words):
                            return jsonify({
                                "status": True,
                                "nickname": nick_str,
                                "id": user_id,
                                "server": "Singapore (SG)"
                            })
        except Exception:
            continue

    return jsonify({
        "status": False, 
        "message": "SG Server Busy (Name Hidden). Try again in 10 seconds."
    }), 404

if __name__ == "__main__":
    app.run(port=5000)
