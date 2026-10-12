import pytest
from app import create_app
from app.extensions import db
@pytest.fixture()
def app():
    app=create_app({'TESTING':True,'SECRET_KEY':'test-secret','SQLALCHEMY_DATABASE_URI':'sqlite://','WTF_CSRF_ENABLED':False,'S3_BUCKET_NAME':''})
    yield app
    with app.app_context(): db.session.remove(); db.drop_all()
@pytest.fixture()
def client(app): return app.test_client()
def test_home(client):
    r=client.get('/'); assert r.status_code==200 and b'AWS Community Registration Portal' in r.data
def test_dashboard_needs_login(client):
    r=client.get('/dashboard'); assert r.status_code in (302,401)
def test_register(client):
    r=client.post('/register',data={'full_name':'Test Member','email':'member@example.com','password':'A-strong-test-password','confirm_password':'A-strong-test-password'},follow_redirects=True)
    assert r.status_code==200 and b'Registration successful' in r.data
def test_duplicate_email(client):
    data={'full_name':'Test Member','email':'member@example.com','password':'A-strong-test-password','confirm_password':'A-strong-test-password'}
    client.post('/register',data=data); r=client.post('/register',data=data)
    assert r.status_code==400 and b'already exists' in r.data
