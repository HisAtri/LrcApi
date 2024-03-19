from app import app


def test_home_route():
    # Use Flask test client to simulate requests
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code < 400


def test_source_route():
    with app.test_client() as client:
        response = client.get('/src/index.html')
        assert response.status_code < 300
