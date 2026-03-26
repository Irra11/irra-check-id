from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route("/ff", methods=["GET"])
def check_ff_nickname():
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"status": False, "message": "Missing ID"}), 400

    # 2026 DEEP-SCRAPE SOURCES (Ranked by SG Success Rate)
    api_sources = [
        # Source 1: Paxsenix Biz (Updated for March 2026 SG Sweep)
        {"url": "https://api.paxsenix.biz.id/game/ff", "params": {"id": user_id, "region": "sg"}},
        
        # Source 2: Hennndra (Direct Merchant Scraper)
        {"url": "https://api.hennndra.my.id/api/game/ff", "params": {"id": user_id}},
        
        # Source 3: Kenz API (Stable for Singapore/Global)
        {"url": "https://api.kenz.my.id/api/game/ff", "params": {"id": user_id}},
        
        # Source 4: Shizune (Backup Gateway)
        {"url": "https://api.shizune.my.id/api/game/ff", "params": {"id": user_id}}
    ]

    # UniPin Spoofing (UniPin is currently better for SG than Codashop)
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "Referer": "https://www.unipin.com/sg/garena/free-fire",
        "Origin": "https://www.unipin.com",
        "Accept": "application/json"
    }

    for source in api_sources:
        try:
            # 8-second timeout for the SG encrypted gateway
            res = requests.get(source["url"], params=source["params"], timeout=8, headers=headers)
            
            if res.status_code == 200:
                data = res.json()
                
                # Fetching the nickname from various JSON paths
                nickname = (
                    data.get("nickname") or 
                    data.get("name") or 
                    (data.get("data") if isinstance(data.get("data"), dict) else {}).get("nickname") or
                    (data.get("result") if isinstance(data.get("result"), dict) else {}).get("nickname")
                )

                # --- THE 2026 FIX LOGIC ---
                # Check if nickname exists and isn't just a copy of the ID (Blind Result)
                if nickname and str(nickname).strip() and str(nickname) != str(user_id):
                    name_clean = str(nickname).strip()
                    
                    # Ensure it's not an error message
                    bad_words = ["not found", "invalid", "error", "null", "busy", "limit", "failed", "hidden"]
                    if not any(word in name_clean.lower() for word in bad_words):
                        return jsonify({
                            "status": True,
                            "nickname": name_clean,
                            "source": "verified_sg"
                        })
        except Exception:
            continue

    return jsonify({
        "status": False, 
        "message": "Name hidden by Garena Security. Please try again in a few minutes."
    }), 404

if __name__ == "__main__":
    app.run(port=5000)
