from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
DATA_FILE = "ranking.json"

# 初回用：空のランキングファイル作成
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

@app.route("/submit", methods=["POST"])
def submit_score():
    data = request.get_json()
    print("Received:", data)

    name = data.get("name")
    score = data.get("score")

    if not name or score is None:
        return jsonify({"success": False, "error": "Invalid data"}), 400

    with open(DATA_FILE, 'r') as f:
        scores = json.load(f)

    scores.append({"name": name, "score": score})
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]

    with open(DATA_FILE, 'w') as f:
        json.dump(scores, f)

    return jsonify({"success": True})

@app.route("/ranking", methods=["GET"])
def get_ranking():
    with open(DATA_FILE, 'r') as f:
        scores = json.load(f)
    
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]
    # ここで配列を"ranking"キーに入れて返す
    return jsonify({"ranking": scores})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
