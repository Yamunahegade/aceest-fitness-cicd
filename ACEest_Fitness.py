"""ACEest Fitness & Gym - Flask application (base version).

Replace/extend the routes below with the functionality from your
Assignment 1 code base (workouts, members, programs, BMI, etc.).
"""
import os
from flask import Flask, jsonify, request

VERSION = os.environ.get("APP_VERSION", "1.1.0")

PROGRAMS = {
    "Fat Loss (FL)": {"workout": "Back Squat, Cardio, Bench, Deadlift", "calorie_factor": 22},
    "Muscle Gain (MG)": {"workout": "Squat, Bench, Deadlift, Press", "calorie_factor": 35},
    "Beginner (BG)": {"workout": "Circuit Training, Full Body", "calorie_factor": 26},
}


def create_app():
    app = Flask(__name__)
    app.config["MEMBERS"] = []
    app.config["WORKOUTS"] = []

    @app.get("/")
    def index():
        return jsonify(app="ACEest Fitness & Gym", version=VERSION)

    @app.get("/health")
    def health():
        return jsonify(status="ok", version=VERSION), 200

    @app.get("/version")
    def version():
        return jsonify(version=VERSION)

    @app.get("/programs")
    def programs():
        return jsonify(PROGRAMS)

    @app.post("/members")
    def add_member():
        data = request.get_json(silent=True) or {}
        name, program = data.get("name"), data.get("program")
        if not name or program not in PROGRAMS:
            return jsonify(error="name and a valid program are required"), 400
        member = {"id": len(app.config["MEMBERS"]) + 1, "name": name, "program": program}
        app.config["MEMBERS"].append(member)
        return jsonify(member), 201

    @app.get("/members")
    def list_members():
        return jsonify(app.config["MEMBERS"])

    @app.post("/workouts")
    def add_workout():
        data = request.get_json(silent=True) or {}
        try:
            minutes = int(data.get("duration"))
        except (TypeError, ValueError):
            return jsonify(error="duration must be an integer"), 400
        if not data.get("workout") or minutes <= 0:
            return jsonify(error="workout and positive duration required"), 400
        entry = {"workout": data["workout"], "duration": minutes}
        app.config["WORKOUTS"].append(entry)
        return jsonify(entry), 201

    @app.get("/workouts")
    def list_workouts():
        return jsonify(app.config["WORKOUTS"])

    @app.get("/bmi")
    def bmi():
        try:
            w, h = float(request.args["weight"]), float(request.args["height"])
            if w <= 0 or h <= 0:
                raise ValueError
        except (KeyError, ValueError):
            return jsonify(error="weight (kg) and height (m) must be positive numbers"), 400
        value = round(w / (h * h), 1)
        cat = "Underweight" if value < 18.5 else "Normal" if value < 25 else "Overweight" if value < 30 else "Obese"
        return jsonify(bmi=value, category=cat)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
