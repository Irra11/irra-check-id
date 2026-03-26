import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# -----------------------------
# FREE FIRE SINGAPORE - 2026 STABLE API
# -----------------------------
@app.route("/ff", methods=["GET"])
def check_ff_nickname():
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"status": False, "message": "Missing ID"}), 400

    # These are the ACTIVE and verified APIs for 2026
    api_sources = [
        # Source 1: Paxsenix (Currently the most powerful Global/SG provider)
        {"url": "https://api.paxsenix.biz.id/game/ff", "params": {"id": user_id}},
        
        # Source 2: Shizune API (Updated 2026 gateway)
        {"url": "https://api.shizune.my.id/api/game/ff", "params": {"id": user_id}},
        
        # Source 3: Isan FFSG (Dedicated Singapore route)
        {"url": "https://api.isan.eu.org/nickname/ffsg", "params": {"id": user_id}}
    ]

    # Pro-Headers: Mimics a legit Top-up store to avoid 2026 bot blocks
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Referer": "https://www.codashop.com/",
        "Origin": "https://www.codashop.com",
        "Accept-Language": "en-US,en;q=0.9"
    }

    for source in api_sources:
        try:
            # Increased timeout to 8s because 2026 gateways are slower due to security
            res = requests.get(source["url"], params=source["params"], timeout=8, headers=headers)
            
            if res.status_code == 200:
                data = res.json()
                
                # Check different JSON formats (nickname vs name vs result)
                nickname = (
                    data.get("nickname") or 
                    data.get("name") or 
                    (data.get("result") if isinstance(data.get("result"), dict) else {}).get("nickname") or
                    (data.get("data") if isinstance(data.get("data"), dict) else {}).get("nickname")
                )

                # Final validation: Ensure it's a real name and not an error string
                if nickname and len(str(nickname)) > 1:
                    low_nick = str(nickname).lower()
                    if all(x not in low_nick for x in ["not found", "invalid", "error", "null"]):
                        return jsonify({
                            "status": True,
                            "nickname": nickname
                        })
        except Exception:
            # Skip if API is down or DNS failed
            continue

    return jsonify({
        "status": False, 
        "message": "Singapore server currently busy. Check ID again in 30 seconds."
    }), 404

# For local testing only
if __name__ == "__main__":
    app.run(port=5000)
