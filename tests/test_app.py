from app import app


def test_home_route():
    # Use Flask test client to simulate requests
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code < 400


def test_source_route():
    with app.test_client() as client:
        response = client.get('/src')
        assert response.status_code < 300


def test_lyrics_route():
    with app.test_client() as client:
        response = client.get('/lyrics?title=使一颗心免于哀伤')
        assert response.status_code < 500
