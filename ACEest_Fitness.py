"""ACEest Fitness & Gym - entry point (assignment naming convention).

The application itself lives in app.py; earlier desktop versions of the
product are kept in legacy/. Run with:  python ACEest_Fitness.py
"""
from app import app, create_app  # noqa: F401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
