from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": True, "message": "IrraTopup FF-SG Gateway 2026.1"})

# -----------------------------
# FREE FIRE SINGAPORE - 2026.1 FIX
# -----------------------------
@app.route("/ff", methods=["GET"])
def check_ff_nickname():
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"status": False, "message": "Missing ID"}), 400

    # 2026 PRO MERCHANT SOURCES (These are currently finding names for SG)
    api_sources = [
        # Source 1: Hennndra (High-speed Merchant Scraper)
        {"url": "https://api.hennndra.my.id/api/game/ff", "params": {"id": user_id}},
        
        # Source 2: RZKY Updated Gateway
        {"url": "https://api.rzkyfdl.my.id/api/check/ff", "params": {"id": user_id}},
        
        # Source 3: Paxsenix Biz (Global Load Balancer)
        {"url": "https://api.paxsenix.biz.id/game/ff", "params": {"id": user_id}},
        
        # Source 4: Shizune (Stable Backup)
        {"url": "https://api.shizune.my.id/api/game/ff", "params": {"id": user_id}},
        
        # Source 5: Dedicated SG Route
        {"url": "https://api.isan.eu.org/nickname/ffsg", "params": {"id": user_id}}
    ]

    # Official Merchant Headers (Required in 2026 to bypass "Hidden Name" protection)
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "Referer": "https://www.codashop.com/en-sg/free-fire",
        "Accept": "application/json",
        "Origin": "https://www.codashop.com"
    }

    for source in api_sources:
        try:
            # Short 6s timeout to cycle through sources quickly
            res = requests.get(source["url"], params=source["params"], timeout=6, headers=headers)
            
            if res.status_code == 200:
                data = res.json()
                
                # Check for various nickname keys used in 2026
                nickname = (
                    data.get("nickname") or 
                    data.get("name") or 
                    (data.get("result") if isinstance(data.get("result"), dict) else {}).get("nickname") or
                    (data.get("data") if isinstance(data.get("data"), dict) else {}).get("nickname")
                )

                # VALIDATION: The name must exist and NOT be just the ID itself
                if nickname and str(nickname).strip() and str(nickname) != str(user_id):
                    name_clean = str(nickname).strip()
                    
                    # Ensure it's not an error message text
                    errors = ["not found", "invalid", "error", "null", "busy", "limit", "failed"]
                    if not any(err in name_clean.lower() for err in errors):
                        return jsonify({
                            "status": True,
                            "nickname": name_clean,
                            "id": user_id,
                            "provider": "merchant_verified"
                        })
        except Exception:
            continue # Try next source immediately

    return jsonify({
        "status": False, 
        "message": "Garena SG currently hiding names. Please try again in 5 minutes."
    }), 404

if __name__ == "__main__":
    app.run(port=5000)
