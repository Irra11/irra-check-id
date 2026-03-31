from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": True,
        "message": "MLBB Checker Working ✅",
        "example": "/ml?id=123456&zone=1234"
    })

# -----------------------------
# MLBB CHECKER (FIXED)
# -----------------------------
@app.route("/ml", methods=["GET"])
def check_ml():
    user_id = request.args.get("id")
    zone_id = request.args.get("zone")

    if not user_id or not zone_id:
        return jsonify({
            "status": False,
            "message": "Missing ID or Zone"
        }), 400

    try:
        url = "https://api.isan.eu.org/nickname/ml"

        res = requests.get(url, params={
            "id": user_id,
            "server": zone_id
        }, timeout=8)

        # 🔥 IMPORTANT: check response first
        if res.status_code != 200:
            return jsonify({
                "status": False,
                "message": "API error"
            }), 500

        data = res.json()

        # DEBUG (optional)
        print("API RESPONSE:", data)

        nickname = data.get("nickname") or data.get("name")

        if nickname and str(nickname).strip() and str(nickname) != str(user_id):
            return jsonify({
                "status": True,
                "nickname": nickname.strip(),
                "id": user_id,
                "zone": zone_id
            })

        return jsonify({
            "status": False,
            "message": "Player not found or wrong zone"
        }), 404

    except requests.exceptions.Timeout:
        return jsonify({
            "status": False,
            "message": "API timeout"
        }), 504

    except Exception as e:
        return jsonify({
            "status": False,
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(port=5000)
