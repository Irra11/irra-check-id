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

    # 2026 ACTIVE Gateways that are currently returning NAMES for SG
    api_sources = [
        # Source 1: Paxsenix (Currently the strongest for SG/Global names)
        {"url": "https://api.paxsenix.biz.id/game/ff", "params": {"id": user_id}},
        
        # Source 2: Lexxy (Updated SG Scraper)
        {"url": "https://api.lexxy.my.id/api/check/ff", "params": {"id": user_id}},
        
        # Source 3: Sandipan (Global Specialist)
        {"url": "https://sandipanmaji.tech/ff/api.php", "params": {"id": user_id}},
        
        # Source 4: Shizune (Backup)
        {"url": "https://api.shizune.my.id/api/game/ff", "params": {"id": user_id}}
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
        "Referer": "https://www.codashop.com/en-sg/free-fire"
    }

    for source in api_sources:
        try:
            res = requests.get(source["url"], params=source["params"], timeout=6, headers=headers)
            if res.status_code == 200:
                data = res.json()
                
                # Check for nickname in every possible JSON location
                nickname = (
                    data.get("nickname") or 
                    data.get("name") or 
                    (data.get("data") if isinstance(data.get("data"), dict) else {}).get("nickname") or
                    (data.get("result") if isinstance(data.get("result"), dict) else {}).get("nickname")
                )

                # IMPORTANT: If nickname is empty or just the ID itself, SKIP to next API
                if nickname and str(nickname).strip() and str(nickname) != str(user_id):
                    name_clean = str(nickname).strip()
                    # Filter out error strings
                    if not any(err in name_clean.lower() for err in ["not found", "invalid", "error"]):
                        return jsonify({
                            "status": True,
                            "nickname": name_clean
                        })
        except Exception:
            continue

    return jsonify({
        "status": False, 
        "message": "Name currently hidden by SG Server. Please try again later."
    }), 404

if __name__ == "__main__":
    app.run(port=5000)
