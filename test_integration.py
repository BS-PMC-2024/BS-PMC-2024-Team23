import pytest,json

from main import app, db, Users


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config['SECRET_KEY'] = 'test_secret_key'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

    with app.app_context():
        db.drop_all()


def test_register_and_login_integration(client):

    response = client.post('/register', data=dict(
        user_type="Trainee",
        first_name="Integration",
        last_name="Test",
        email="integration.test@example.com",
        password="password123",
        confirm_password="password123",
        gender="Male",
        age="28",
        weight="70",
        height="175",
        fitness_level="Intermediate",
        training_frequency="3"
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b'Registration successful!' in response.data

    response = client.post('/login', data=dict(
        email="integration.test@example.com",
        password="password123"
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b'Welcome' in response.data


def test_login_and_create_program_integration(client):

    with app.app_context():
        user = Users(
            user_type="Trainee",
            first_name="Integration",
            last_name="Program",
            email="integration.program@example.com",
            password="password123",
            age=30,
            weight=70.0,
            height=175.0,
            about_me='Integration program user',
            program='',
            gender="Male",
            fitness_level="Intermediate",
            training_frequency=3,
            fitness_goal="Muscle Gain"
        )
        db.session.add(user)
        db.session.commit()

    response = client.post('/login', data=dict(
        email="integration.program@example.com",
        password="password123"
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b'Welcome' in response.data

    response = client.post('/create_program', follow_redirects=True)
    assert response.status_code == 201

    data = json.loads(response.data)
    assert 'program' in data
    assert 'Exercise Program' in data['program']

