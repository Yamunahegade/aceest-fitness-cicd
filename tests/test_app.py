import pytest
from ACEest_Fitness import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.get_json()["status"] == "ok"


def test_index_and_version(client):
    assert "version" in client.get("/").get_json()
    assert "version" in client.get("/version").get_json()


def test_programs(client):
    assert "Fat Loss (FL)" in client.get("/programs").get_json()


def test_add_member_ok(client):
    r = client.post("/members", json={"name": "Asha", "program": "Beginner (BG)"})
    assert r.status_code == 201
    assert len(client.get("/members").get_json()) == 1


@pytest.mark.parametrize("payload", [{}, {"name": "X"}, {"name": "X", "program": "nope"}])
def test_add_member_invalid(client, payload):
    assert client.post("/members", json=payload).status_code == 400


def test_add_workout(client):
    assert client.post("/workouts", json={"workout": "Run", "duration": 30}).status_code == 201
    assert client.get("/workouts").get_json()[0]["duration"] == 30


@pytest.mark.parametrize("payload", [{"workout": "Run"}, {"workout": "Run", "duration": "x"},
                                     {"workout": "Run", "duration": -5}, {"duration": 10}])
def test_add_workout_invalid(client, payload):
    assert client.post("/workouts", json=payload).status_code == 400


@pytest.mark.parametrize("w,h,cat", [(50, 1.8, "Underweight"), (70, 1.75, "Normal"),
                                     (85, 1.75, "Overweight"), (110, 1.75, "Obese")])
def test_bmi(client, w, h, cat):
    assert client.get(f"/bmi?weight={w}&height={h}").get_json()["category"] == cat


def test_bmi_invalid(client):
    assert client.get("/bmi").status_code == 400
    assert client.get("/bmi?weight=0&height=1.7").status_code == 400
