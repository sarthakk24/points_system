from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os
import logging
from dotenv import load_dotenv
from score import score_word

load_dotenv()

mongo_url = os.getenv("MONGO_URL")

app = Flask(__name__)
cors = CORS(app)

client = MongoClient(mongo_url)
collection = client["aaruush"]
db = collection["points"]

logging.basicConfig(level=logging.ERROR)

@app.route("/")
def index():
    return "in-progress"

@app.route('/add_data', methods=['POST'])
def add_data():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON data in the request"}), 400

        y = db.find_one({"aaruushid": data["aaruushid"]})

        if y is None:
            entry = {
                "name": data["name"],
                "RegNo": data["RegNo"],
                "email": data["email"],
                "attended_event": [data["event"] + str(1)],
                "phone": data["phone"],
                "aaruushid": data["aaruushid"],
                "score": 2
            }
            db.insert_one(entry)
            return jsonify({"message": "New user added to history"})

        attended = y.get("attended_event")

        if (data["event"] + str(data["round"])) in attended:
            return jsonify({"message": "Already attended"})

        if data["round"] == 1:
            attended.append(data["event"] + str(1))
            db.update_one({"aaruushid": data["aaruushid"]}, {"$set": {"attended_event": attended}})
            score = score_word(attended)

            db.update_one({"aaruushid": data["aaruushid"]}, {"$set": {"score": score}})
            return jsonify({"message": "Added to history"})

        if (data["event"] + str(data["round"] - 1)) in attended:
            attended.append(data["event"] + str(data["round"]))
            score = score_word(attended)

            db.update_one({"aaruushid": data["aaruushid"]}, {"$set": {"score": score}})
            db.update_one({"aaruushid": data["aaruushid"]}, {"$set": {"attended_event": attended}})
            return jsonify({"message": "Added to history"})

        else:
            return jsonify({"message": "Not attended previous round"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_score', methods=['POST'])
def get_score():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON data in the request"}), 400

        y = db.find_one({"aaruushid": data["aaruushid"]})

        if y is None:
            return jsonify({"error": "User not found"}), 404

        name = y.get("name")
        score = y.get("score")

        return jsonify({"name": name, "score": score})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    try:
        app.run(debug=True, host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        print("Keyboard interrupt: shutting down...")
    finally:
        client.close()
