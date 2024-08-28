import pytest
from main import app, db,Users


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


def test_home_route(client):

    response = client.get('/')
    assert response.status_code == 200
    assert b'Login' in response.data


def test_about_route(client):
    response = client.get('/about')
    assert response.status_code == 200
    assert b'About' in response.data


def test_logout_without_user(client):
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You are not logged in.' in response.data


def test_feedback_route(client):
    response = client.get('/feedback')
    assert response.status_code == 200
    assert b'Feedback' in response.data



def test_admin_route_without_permission(client):
    response = client.get('/admin', follow_redirects=True)
    assert response.status_code == 200
    assert b'You are not authorized to view this page' in response.data



def test_view_route(client):
    response = client.get('/view')
    assert response.status_code == 200
    assert b'Users' in response.data


def test_register_with_valid_data(client):
    response = client.post('/register', data=dict(
        user_type="Trainee",
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        password="password123",
        confirm_password="password123",
        gender="Male",
        age="30",
        weight="75",
        height="180",
        fitness_level="Beginner",
        training_frequency="3"
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b'Registration successful!' in response.data
    with app.app_context():
        user = Users.query.filter_by(email="john.doe@example.com").first()
        assert user is not None
        assert user.first_name == "John"


def test_edit_user_details(client):

    with app.app_context():
        user = Users(
            user_type="Trainee",
            first_name="Test",
            last_name="User",
            email="edit.user@example.com",
            password="password123",
            age=25,
            weight=70.0,
            height=175.0,
            about_me='Test user',
            program='Sample program',
            gender="Male",
            fitness_level="Beginner",
            training_frequency=3,
            fitness_goal="Weight Loss"
        )
        db.session.add(user)
        db.session.commit()

    client.post('/login', data=dict(
        email="edit.user@example.com",
        password="password123"
    ), follow_redirects=True)

    response = client.post('/edit_user', data=dict(
        first_name="Updated",
        last_name="User",
        email="edit.user@example.com",
        password="newpassword123",
        age="26",
        weight="68",
        height="176",
        training_frequency="4",
        fitness_level="Intermediate",
        fitness_goal="Muscle Gain"
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b'User details updated successfully!' in response.data

    with app.app_context():
        updated_user = Users.query.filter_by(email="edit.user@example.com").first()
        assert updated_user.first_name == "Updated"
        assert updated_user.age == 26
        assert updated_user.weight == 68.0
def test_remove_user_by_admin(client):

    with app.app_context():
        admin = Users(
            user_type="Admin",
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            password="adminpassword",
            age=30,
            weight=80.0,
            height=180.0,
            about_me='Admin user',
            program='Admin program',
            gender="Male",
            fitness_level="Advanced",
            training_frequency=5,
            fitness_goal="Maintain weight"
        )
        user = Users(
            user_type="Trainee",
            first_name="Delete",
            last_name="Me",
            email="delete.me@example.com",
            password="deletepassword",
            age=22,
            weight=60.0,
            height=160.0,
            about_me='Test user',
            program='Sample program',
            gender="Female",
            fitness_level="Beginner",
            training_frequency=2,
            fitness_goal="Weight Loss"
        )
        db.session.add(admin)
        db.session.add(user)
        db.session.commit()

        user_id_to_delete = user.id

    client.post('/login', data=dict(
        email="admin@example.com",
        password="adminpassword"
    ), follow_redirects=True)

    response = client.post('/remove_users', data=dict(
        user_id=user_id_to_delete
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b'User removed successfully' in response.data

    with app.app_context():
        deleted_user = Users.query.filter_by(email="delete.me@example.com").first()
        assert deleted_user is None
def test_send_feedback(client):

    with app.app_context():
        user = Users(
            user_type="Trainee",
            first_name="Feedback",
            last_name="Sender",
            email="feedback.sender@example.com",
            password="password123",
            age=30,
            weight=70.0,
            height=175.0,
            about_me='Feedback sender user',
            program='Sample program',
            gender="Female",
            fitness_level="Beginner",
            training_frequency=2,
            fitness_goal="Weight Loss"
        )
        db.session.add(user)
        db.session.commit()

    client.post('/login', data=dict(
        email="feedback.sender@example.com",
        password="password123"
    ), follow_redirects=True)

    response = client.post('/feedback', data=dict(
        feedback="This is a test feedback!"
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b'Feedback received' in response.data or b'Feedback' in response.data



