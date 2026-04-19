from flask import Flask, render_template, request, jsonify
from agent import analyze_incident
from memory import save_memory, ensure_bank_exists

app = Flask(__name__)

# Initialize memory
ensure_bank_exists()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    user_input = data.get("incident")

    if not user_input:
        return jsonify({"result": "No input provided"}), 400

    result = analyze_incident(user_input)

    return jsonify({"result": result})


if __name__ == "__main__":
    app.run(debug=True)