import random
from flask import Flask
from flask import redirect, url_for, render_template, request, session, flash, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

from gender import Gender
from openAIManager import call_openAI

app = Flask(__name__)
app.secret_key = "hello"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://myuser:mypassword@localhost:5432/mydatabase"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # השתנה מ-_id ל-id
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100))
    age = db.Column(db.Integer)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    user_type = db.Column(db.String(50))  # שדה סוג המשתמש החדש
    about_me = db.Column(db.Text, nullable=True)  # עמודה חדשה שתשמור את הטקסט על המאמן
    program = db.Column(db.Text, nullable=True)

    def __init__(self, user_type, first_name, last_name, email, password, age, weight, height, about_me, program):
        self.user_type = user_type
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.age = age
        self.weight = weight
        self.height = height
        self.about_me = about_me
        self.program = program

    def check_password(self, password):
        return self.password == password


class Topics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __init__(self, title, description):
        self.title = title
        self.description = description


@app.context_processor
def inject_user():
    """הפונקציה הזאת מוודאת שהמשתמש הנוכחי יועבר לכל תבנית."""
    user_email = session.get("email")
    user = Users.query.filter_by(email=user_email).first() if user_email else None
    return dict(current_user=user)


@app.route("/")
def home():
    return render_template("LoginPage.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        email = request.form["email"]
        password = request.form["password"]
        found_user = Users.query.filter_by(email=email).first()

        if found_user and found_user.check_password(password):
            session["user"] = found_user.first_name
            session["email"] = found_user.email
            session["user_type"] = found_user.user_type

            if found_user.user_type == "Coach":
                return redirect(url_for("coach"))
            elif found_user.user_type == "Trainee":
                return redirect(url_for("user"))
            elif found_user.user_type == "Admin":
                return redirect(url_for("admin"))
        else:
            flash("User not found or incorrect password. Please register.", "danger")
            return redirect(url_for("home"))
    else:
        if "user" in session:
            flash("Already logged in.", "info")
            if session.get("user_type") == "Coach":
                return redirect(url_for("coach"))
            elif session.get("user_type") == "Trainee":
                return redirect(url_for("user"))
            elif session.get("user_type") == "Admin":
                return redirect(url_for("admin"))
        return render_template("LoginPage.html")


@app.route("/admin", methods=["GET"])
def admin():
    if "user" in session and session.get("user_type") == "Admin":
        search_query = request.args.get('search_query')

        if search_query:
            # Search by ID or Email
            users = Users.query.filter(
                (Users.id == search_query) | (Users.email.like(f"%{search_query}%"))
            ).all()
        else:
            users = Users.query.all()

        # Counters
        total_users = Users.query.count()
        total_coaches = Users.query.filter_by(user_type="Coach").count()
        total_trainees = Users.query.filter_by(user_type="Trainee").count()

        return render_template("admin.html", values=users, total_users=total_users, total_coaches=total_coaches,
                               total_trainees=total_trainees)
    else:
        flash("You are not authorized to view this page", "danger")
        return redirect(url_for("login"))


@app.route("/user", methods=["POST", "GET"])
def user():
    if "user" in session:
        email = session["email"]
        user = Users.query.filter_by(email=email).first()
        topics = Topics.query.all()  # לקבל את כל הנושאים

        if request.method == "POST":
            # עדכון פרטי המשתמש
            goal = request.form["goal"]
            # אפשר להוסיף את ה-goal למשתמש ב-DATABASE כאן (אם יש צורך)
            # user.goal = goal  # דוגמה לעדכון המטרה (בהנחה שיש שדה כזה ב-database)
            db.session.commit()
            flash("Information updated successfully!", "success")
            return redirect(url_for("user"))

        # הצגת מידע אישי ודפי נושאים
        return render_template("user.html", email=email, topics=topics, program=user.program)
    else:
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    if "user" in session:
        session.pop("user", None)
        session.pop("email", None)
        flash("Bye, see you next time", "info")
    else:
        flash("You are not logged in.", "danger")
    return redirect(url_for("login"))


@app.route("/view")
def view():
    return render_template("view.html", values=Users.query.all())


@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        # Handle form submission
        user_feedback = request.form.get("feedback")
        # Here you could save the feedback to a database or send an email to admins
        # For demonstration, we'll just print it to the console
        print(f"Feedback received: {user_feedback}")
        return redirect(url_for("user"))  # Redirect to home or another page after submission
    return render_template("feedback.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        user_type = request.form["user_type"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        password = request.form["password"]
        age = request.form["age"]
        weight = request.form["weight"]
        height = request.form["height"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for("register"))

        # Check if email already exists
        existing_user = Users.query.filter_by(email=email).first()
        if existing_user:
            flash("Email is already taken", "error")
            return redirect(url_for("register"))

        new_user = Users(user_type, first_name, last_name, email, password, age, weight, height, about_me="", program="No program yet...")
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful!", "success")

        # Redirect based on user type
        if user_type == "Coach":
            return redirect(url_for("coach"))
        elif user_type == "Trainee":
            return redirect(url_for("user"))
        else:
            flash("Invalid user type", "danger")
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/coach", methods=["GET", "POST"])
def coach():
    if "user" in session:
        email = session["email"]
        user = Users.query.filter_by(email=email).first()
        topics = Topics.query.all()  # קבלת כל הנושאים

        if request.method == "POST":
            user.about_me = request.form["about_text"]
            db.session.commit()
            flash("About Me updated successfully!", "success")
            return redirect(url_for("coach"))

        try:
            # הוספת העובדה מה-API
            fact = get_random_fact_from_openai()
        except Exception as e:
            fact = "Unable to fetch fact at this moment."

        return render_template("coacher.html", coach_info=user.about_me, topics=topics, fact=fact)
    else:
        flash("You are not logged in", "danger")
        return redirect(url_for("login"))


@app.route("/get_fact", methods=["GET"])
def get_fact():
    if "user" in session:
        try:
            # קריאה ל-AI כדי לקבל עובדה אקראית
            fact = get_random_fact_from_openai()  # הפונקציה שתקרא ל-OpenAI כדי לקבל את העובדה
            return jsonify({"fact": fact}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": str("no user in session")}), 500

def get_random_fact_from_openai():
    # לוגיקה לביצוע קריאה ל-OpenAI ולקבל עובדה אקראית
    prompt = "Give me a random fitness or well-being fact."
    response = call_openAI_simple(prompt)  # פונקציה שכבר קיימת אצלך ומבצעת את הקריאה
    return response
@app.route("/edit_user", methods=["POST", "GET"])
def edit_user():
    if "user" in session:
        email = session["email"]
        user = Users.query.filter_by(email=email).first()

        if request.method == "POST":
            user.first_name = request.form["first_name"]
            user.last_name = request.form["last_name"]
            user.email = request.form["email"]
            user.password = request.form["password"]
            user.age = request.form["age"]
            user.weight = request.form["weight"]
            user.height = request.form["height"]

            db.session.commit()
            flash("User details updated successfully!", "success")
            return redirect(url_for("user"))

        return render_template("edit_user.html", user=user)
    else:
        flash("You are not logged in", "danger")
        return redirect(url_for("login"))


@app.route("/user")
def user_home():
    if "user" in session:
        user_email = session["email"]
        found_user = Users.query.filter_by(email=user_email).first()

        if found_user.user_type == "Coach":
            return redirect(url_for("coach"))
        else:
            return render_template("user.html", email=user_email)
    else:
        flash("You are not logged in", "danger")
        return redirect(url_for("login"))


@app.route("/home")
def home_redirect():
    if "user" in session:
        user_email = session["email"]
        found_user = Users.query.filter_by(email=user_email).first()

        if found_user.user_type == "Coach":
            return redirect(url_for("coach"))
        elif found_user.user_type == "Trainee":
            return redirect(url_for("user"))
        else:
            flash("Unknown user type", "danger")
            return redirect(url_for("login"))
    else:
        flash("You are not logged in", "danger")
        return redirect(url_for("login"))


@app.route("/remove_users", methods=["GET", "POST"])
def remove_users():
    if "user" in session and session.get("user_type") == "Admin":
        if request.method == "POST":
            user_id = request.form["user_id"]
            user_to_remove = Users.query.get(user_id)

            if user_to_remove:
                db.session.delete(user_to_remove)
                db.session.commit()
                flash("User removed successfully", "success")
            else:
                flash("User not found", "danger")

        users = Users.query.all()
        return render_template("remove_users.html", users=users)
    else:
        flash("You are not authorized to view this page", "danger")
        return redirect(url_for("login"))


@app.route("/edit_user_admin", methods=["GET", "POST"])
def edit_user_admin():
    if "user" in session and session.get("user_type") == "Admin":
        users = Users.query.all()
        selected_user = None

        if request.method == "POST":
            user_id = request.form.get("user_id")
            selected_user = Users.query.get(user_id)

            if "first_name" in request.form:
                selected_user.first_name = request.form["first_name"]
                selected_user.last_name = request.form["last_name"]
                selected_user.email = request.form["email"]
                selected_user.password = request.form["password"]
                selected_user.age = request.form["age"]
                selected_user.weight = request.form["weight"]
                selected_user.height = request.form["height"]
                selected_user.user_type = request.form["user_type"]

                db.session.commit()
                flash("User details updated successfully", "success")
                return redirect(url_for("edit_user_admin"))

        return render_template("edit_user_admin.html", users=users, selected_user=selected_user)
    else:
        flash("You are not authorized to view this page", "danger")
        return redirect(url_for("login"))


@app.route("/create_program", methods=["POST"])
def create_program():
    if "user" in session:
        email = session["email"]
        user = Users.query.filter_by(email=email).first()
        name = f"{user.first_name} {user.last_name}"
        gender = Gender.MALE

        # Call the function with collected data
        try:
            print("calling openAI api...")
            response = call_openAI(name, user.age, gender, user.weight, user.height, user.about_me)
            print("response received")
            user.program = response
            db.session.commit()
            return jsonify({"program": response}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": str("no user in session")}), 500


@app.route("/manage_topics", methods=["GET", "POST"])
def manage_topics():
    if "user" in session and session.get("user_type") == "Admin":
        if request.method == "POST":
            action = request.form.get("action")
            title = request.form.get("title")
            description = request.form.get("description")
            topic_id = request.form.get("topic_id")

            if action == "add":
                new_topic = Topics(title=title, description=description)
                db.session.add(new_topic)
                db.session.commit()
                flash("Topic added successfully!", "success")
            elif action == "edit" and topic_id:
                topic = Topics.query.get(topic_id)
                if topic:
                    topic.title = title
                    topic.description = description
                    db.session.commit()
                    flash("Topic updated successfully!", "success")
                else:
                    flash("Topic not found.", "danger")
            elif action == "delete" and topic_id:
                topic = Topics.query.get(topic_id)
                if topic:
                    db.session.delete(topic)
                    db.session.commit()
                    flash("Topic deleted successfully!", "success")
                else:
                    flash("Topic not found.", "danger")

        topics = Topics.query.all()
        return render_template("manage_topics.html", topics=topics)
    else:
        flash("You are not authorized to view this page", "danger")
        return redirect(url_for("login"))


def create_users_table():
    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table('users'):
            db.create_all()
            print("Users table created!")
        else:
            print("Users table already exists!")




def load_fake_data():
    fake_names = ['Maor', 'Matan', 'Alice', 'Bob', 'Charlie']
    fake_domains = ['gmail.com']
    with app.app_context():  # Ensure we are within the application context

        for i in range(5):  # Creating 5 fake users
            user = Users(
                first_name=random.choice(fake_names),
                last_name=random.choice(fake_names),
                email=f'{i}@{random.choice(fake_domains)}',
                password='1',
                age=random.randint(18, 65),
                weight=random.uniform(50.0, 100.0),
                height=random.uniform(150.0, 200.0),
                user_type=random.choice(['Admin', 'Trainee']),
                about_me='Just a fun user.',
                program='Sample Program'
            )
            try:
                db.session.add(user)
                db.session.commit()
            except SQLAlchemyError as e:
                print(f"Error adding user {i}: {e}")
                db.session.rollback()

    print("Fake data loaded!")


if __name__ == "__main__":
    # # Print all files in Templates folder
    # templates_dir = os.path.join(os.getcwd(), 'Templates')  # Get absolute path
    # for filename in os.listdir(templates_dir):
    #     print(filename)
    create_users_table()
    load_fake_data()
    with app.app_context():
        db.create_all()
    app.run(debug=False, host='0.0.0.0', port=5001)
