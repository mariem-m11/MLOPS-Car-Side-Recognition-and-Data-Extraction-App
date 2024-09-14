import pytest
from fastapi.testclient import TestClient

from app.appfast import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client


def test_home_page(client):
    response = client.get("/home")
    assert response.status_code == 200
    assert response.json() == {"message": "Use /predict to upload and classify the image"}


def test_invalid_file_extension(client):
    files = {
        "file": ("test.txt", b"file contents"),
    }
    response = client.post("/CarPose", files=files)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid file extension"}


def test_car_pose_prediction(client):
    files = {
        "file": ("car1.png", open("static/images/car1.png", "rb").read()),
    }
    response = client.post("/CarPose", files=files)
    assert response.status_code == 200
    assert response.json() == {"prediction": "side right complete"}
