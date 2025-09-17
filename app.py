from flask import Flask, request, jsonify
import json
import os
from flask_cors import CORS

app = Flask(__name__)
DATA_FILE = "ranking.json"
ENABLED_FILE = "ranking_enabled.json"

# 不適切ワードのリスト（必要に応じて編集）
BAD_WORDS = [
    "セックス","せっくす","sex","ちんこ","チンコ","chinko","うんこ","ウンコ","unko","まんこ","マンコ","manko","〇","おっぱい","オッパイ","oppai","乳首","ちくび","チクビ","chikubi","tikubi","ちんちん","ちんぽ","チンポ","chinpo","しっこ","糞","porn","fuck","pussy","bitch","えろ","エロ","ero","エ口","裸","射精","勃起","ぼっき","ヌード","nude","オナ","ペニス","penis","レイプ","中出し","フェラ","ｵｯﾊﾟｲ","ｴﾛ","0ppai","opp@i","oppa1"
]

CORS(app, resources={r"/*": {"origins": "*"}})

# 初回用：空のランキングファイル作成
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

# 初回用：ランキングON/OFF状態ファイル作成（デフォルトON）
if not os.path.exists(ENABLED_FILE):
    with open(ENABLED_FILE, 'w') as f:
        json.dump({"enabled": False}, f)

def is_name_valid(name: str) -> bool:
    """名前が不適切ワードを含まないかチェックする。小文字比較で部分一致を拒否。"""
    if not name:
        return False
    lowered = name.lower()
    for bad in BAD_WORDS:
        if bad.lower() in lowered:
            return False
    return True

@app.route("/submit", methods=["POST"])
def submit_score():
    data = request.get_json()
    print("Received:", data)

    name = data.get("name")
    score = data.get("score")

    if not name or score is None:
        return jsonify({"success": False, "error": "Invalid data"}), 400

    # 不適切ワードチェック（元の名前で判定）
    if not is_name_valid(name):
        return jsonify({"success": False, "error": "Name contains prohibited content"}), 400

    # 名前が10文字より長ければ先頭10文字で切り捨て（保存時のみ）
    if len(name) > 10:
        saved_name = name[:10]
    else:
        saved_name = name

    with open(DATA_FILE, 'r') as f:
        scores = json.load(f)

    scores.append({"name": saved_name, "score": score})
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]

    with open(DATA_FILE, 'w') as f:
        json.dump(scores, f)

    return jsonify({"success": True})

@app.route("/ranking", methods=["GET"])
def get_ranking():
    with open(DATA_FILE, 'r') as f:
        scores = json.load(f)
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]
    return jsonify({"ranking": scores})

# ランキング表示ON/OFF状態取得
@app.route("/ranking-enabled", methods=["GET"])
def get_ranking_enabled():
    if not os.path.exists(ENABLED_FILE):
        enabled = True
    else:
        with open(ENABLED_FILE, 'r') as f:
            enabled = json.load(f).get("enabled", True)
    return jsonify({"enabled": enabled})

# ランキング表示ON/OFF状態変更（管理者用）
@app.route("/ranking-enabled", methods=["POST"])
def set_ranking_enabled():
    data = request.get_json()
    enabled = bool(data.get("enabled", True))
    with open(ENABLED_FILE, 'w') as f:
        json.dump({"enabled": enabled}, f)
    return jsonify({"success": True, "enabled": enabled})

# 不正スコア削除API
@app.route("/delete-score", methods=["POST"])
def delete_score():
    data = request.get_json()
    name = data.get("name")
    score = data.get("score")

    if not name or score is None:
        return jsonify({"success": False, "error": "Invalid data"}), 400

    with open(DATA_FILE, 'r') as f:
        scores = json.load(f)

    # 該当するスコアを削除
    new_scores = [s for s in scores if not (s["name"] == name and s["score"] == score)]

    if len(new_scores) == len(scores):
        return jsonify({"success": False, "error": "Score not found"}), 404

    with open(DATA_FILE, 'w') as f:
        json.dump(new_scores, f)

    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)