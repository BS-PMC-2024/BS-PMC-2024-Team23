import random

from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
import secrets
from openAIManager import call_openAI, accpected_result, ask_openai, ai_suggestions, get_ai_diet_suggestions
from openAIManager import call_openAI, accpected_result, ask_openai, call_openAI_for_fact, get_ai_suggestions
from openAIManager import call_openAI, accpected_result,ask_openai,call_openAI_for_fact,get_muscles_sugg_from_openai
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://myuser:mypassword@localhost:5432/mydatabase"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Model for Users
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50))
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    user_type = db.Column(db.String(50))
    fitness_goal = db.Column(db.String(30))
    about_me = db.Column(db.Text, nullable=True)
    program = db.Column(db.Text, nullable=True)
    fitness_level = db.Column(db.String(50))
    training_frequency = db.Column(db.Integer)

    progress = db.relationship('UserProgress', order_by='UserProgress.week_number', back_populates='user')

    def __init__(self, user_type, first_name, last_name, email, password, age, weight, height, about_me,
                 program, gender, fitness_level, training_frequency, fitness_goal):
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
        self.gender = gender
        self.fitness_level = fitness_level
        self.training_frequency = training_frequency
        self.fitness_goal = fitness_goal

    def check_password(self, password):
        return self.password == password


class UserProgress(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, nullable=False)
    week_number = db.Column(db.Integer, primary_key=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    fitness_goal = db.Column(db.String(30), nullable=False)
    training_frequency = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    workout_count = db.Column(db.Integer, nullable=False)
    avg_training_frequency = db.Column(db.Integer, nullable=False, default=0.0)
    avg_weight_change = db.Column(db.Float, nullable=False, default=0.0)
    ai_suggestions = db.Column(db.Text, nullable=True, default='')
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    user = db.relationship('Users', back_populates='progress')


# Model for Topics
class Topics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    clicks = db.Column(db.Integer, default=0)

    def __init__(self, title, description):
        self.title = title
        self.description = description
        self.clicks = 0

@app.route("/record_click", methods=["POST"])
def record_click():
    data = request.get_json()
    topic_id = data.get("topic_id")

    if topic_id:
        topic = Topics.query.get(topic_id)
        if topic:
            topic.clicks += 1
            db.session.commit()
            return jsonify({"success": True}), 200
    return jsonify({"success": False}), 400

@app.context_processor
def inject_user():
    user_email = session.get("email")
    user = Users.query.filter_by(email=user_email).first() if user_email else None
    return dict(current_user=user)


@app.route("/")
def home():
    return render_template("LoginPage.html")



@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        return handle_login_post()
    else:
        return handle_login_get()


def handle_login_post():
    session.permanent = False
    email = request.form.get("email")
    password = request.form.get("password")

    found_user = Users.query.filter_by(email=email).first()

    if found_user and found_user.check_password(password):
        set_user_session(found_user)

        if user_goals_complete(found_user):
            return redirect_based_on_user_type(found_user)

        return redirect_based_on_user_type(found_user)

    else:
        flash("User not found or incorrect password. Please register.", "danger")
        return redirect(url_for("home"))


def handle_login_get():
    if "user" in session:
        flash("Already logged in.", "info")
        email = session.get("email")
        found_user = Users.query.filter_by(email=email).first()
        """
        if found_user:
            if user_goals_complete(found_user):
                return redirect(url_for("interactive_feedback"))
"""
        return redirect_based_on_user_type(found_user)

    return render_template("LoginPage.html")


def set_user_session(user):
    session["user"] = user.first_name
    session["email"] = user.email
    session["user_type"] = user.user_type
    session["user_id"] = user.id


def user_goals_complete(user):
    return all([user.fitness_goal, user.fitness_level, user.training_frequency, user.user_type != "Admin"])


def redirect_based_on_user_type(user):
    if user.user_type == "Coach":
        return redirect(url_for("coach"))
    elif user.user_type == "Trainee":
        return redirect(url_for("user"))
    elif user.user_type == "Admin":
        return redirect(url_for("admin"))
    else:
        flash("Invalid user type", "danger")
        return redirect(url_for("home"))

@app.route("/admin", methods=["GET"])
def admin():
    if "user" in session and session.get("user_type") == "Admin":
        search_query = request.args.get('search_query')

        if search_query:
            users = Users.query.filter(
                (Users.id == search_query) | (Users.email.like(f"%{search_query}%"))
            ).all()
        else:
            users = Users.query.all()


        total_users = Users.query.count()
        total_coaches = Users.query.filter_by(user_type="Coach").count()
        total_trainees = Users.query.filter_by(user_type="Trainee").count()

        return render_template("admin.html", values=users, total_users=total_users,
                               total_coaches=total_coaches, total_trainees=total_trainees)
    else:
        flash("You are not authorized to view this page", "danger")
        return redirect(url_for("login"))


@app.route("/user", methods=["GET"])
def user():
    if "user" in session:
        email = session["email"]
        topics = Topics.query.all()
        user = Users.query.filter_by(email=email).first()
        return render_template("user.html", training_frequency=user.training_frequency, goal=user.fitness_goal,
                               fitness_level=user.fitness_level, email=email, topics=topics)
    else:
        return redirect(url_for("login"))


@app.route("/user/save", methods=["POST"])
def save_user_data():
    if "user" in session:
        email = session["email"]
        user = Users.query.filter_by(email=email).first()
        topics = Topics.query.all()

        goal = request.form["goal"]
        fitness_level = request.form["fitness_level"]
        training_frequency = request.form["training_frequency"]

        if (user.fitness_goal != goal or
                user.fitness_level != fitness_level or
                user.training_frequency != training_frequency):
            user.fitness_goal = goal
            user.fitness_level = fitness_level
            user.training_frequency = training_frequency
            db.session.commit()
            flash("Information updated successfully!", "success")
        return redirect(url_for("create_program"))
    else:
        return redirect(url_for("login"))


@app.route("/fetch_expected_result", methods=["POST"])
def fetch_expected_result():
    if "user" in session:
        email = session["email"]
        user = Users.query.filter_by(email=email).first()
        name = f"{user.first_name} {user.last_name}"
        if user and user.program:
            try:
                time_frame = request.json.get('time_frame', '1 month')
                expected_result = accpected_result(user.program, time_frame,user.weight,user.height,name,user.gender)
                return jsonify({"expected_result": expected_result}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        else:
            return jsonify({"error": "No program found for the user"}), 404
    else:
        return jsonify({"error": "User not authenticated"}), 401


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
        user_feedback = request.form.get("feedback")
        print(f"Feedback received: {user_feedback}")
        return redirect(url_for("user"))
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
        gender = request.form["gender"]
        age = request.form["age"]
        weight = request.form["weight"]
        height = request.form["height"]
        fitness_level = request.form.get("fitness_level", None)
        training_frequency = request.form.get("training_frequency", None)
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for("register"))

        # Check if email already exists
        existing_user = Users.query.filter_by(email=email).first()
        if existing_user:
            flash("Email is already taken", "error")
            return redirect(url_for("register"))

        new_user = Users(user_type, first_name, last_name, email, password, age, weight, height, about_me='',
                         program='no prog yet', gender=gender, fitness_level=fitness_level,
                         training_frequency=training_frequency, fitness_goal=None)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful!", "success")

        if user_type == "Coach":
            return redirect(url_for("coach"))
        elif user_type == "Trainee":
            return redirect(url_for("user"))
        else:
            flash("Invalid user type", "danger")
            return redirect(url_for("register"))

    return render_template("register.html")




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
            user.training_frequency = request.form.get("training_frequency", user.training_frequency)
            user.fitness_level = request.form.get("fitness_level", user.fitness_level)
            user.fitness_goal = request.form.get("fitness_goal", user.fitness_goal)

            db.session.commit()
            flash("User details updated successfully!", "success")
            return redirect(url_for("user"))

        return render_template("edit_user.html", user=user)
    else:
        flash("You are not logged in", "danger")
        return redirect(url_for("login"))

@app.route("/trainee", methods=["GET", "POST"])
def trainee():
    if "user" in session and session.get("user_type") == "Trainee":
        email = session["email"]
        user = Users.query.filter_by(email=email).first()
        muscles = ["Chest", "Back", "Legs", "Arms", "Shoulders", "Abs"]

        suggestion = None

        if request.method == "POST":
            selected_muscle = request.form.get("muscle_type")
            try:
                suggestion = get_muscles_sugg_from_openai(selected_muscle)
                print(f"Fetched suggestion for {selected_muscle} from OpenAI: {suggestion}")
            except Exception as e:
                suggestion = "Unable to fetch suggestion at this moment."
                print(f"Error fetching suggestion: {e}")

        return render_template("trainee.html", muscles=muscles, suggestion=suggestion)
    else:
        flash("Access restricted to Trainee users only", "danger")
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

        if found_user:
            if found_user.user_type == "Coach":
                return redirect(url_for("coach"))
            elif found_user.user_type == "Trainee":
                return redirect(url_for("user"))
            elif found_user.user_type == "Admin":
                return redirect(url_for("admin"))
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
            user_id = request.form.get("user_id")

            if not user_id:
                flash("User ID is required.", "danger")
                return redirect(url_for("remove_users"))

            try:
                user_id = int(user_id)
            except ValueError:
                flash("Invalid User ID. Please enter a valid number.", "danger")
                return redirect(url_for("remove_users"))

            user_to_remove = db.session.get(Users, user_id)

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




@app.route("/coach", methods=["GET", "POST"])
def coach():
    if "user" in session:
        email = session["email"]
        user = Users.query.filter_by(email=email).first()
        topics = Topics.query.all()

        if request.method == "POST":
            user.about_me = request.form["about_text"]
            db.session.commit()
            flash("About Me updated successfully!", "success")
            return redirect(url_for("coach"))

        try:
            fact = get_random_fact_from_openai()
            print(f"Fetched fact from OpenAI: {fact}")
        except Exception as e:
            fact = "Unable to fetch fact at this moment."
            print(f"Error fetching fact: {e}")

        return render_template("coach.html", coach_info=user.about_me, topics=topics, fact=fact)
    else:
        flash("You are not logged in", "danger")
        return redirect(url_for("login"))

@app.route("/get_fact", methods=["GET"])
def get_fact():
    if "user" in session:
        try:
            fact = get_random_fact_from_openai()
            print(f"Fetched fact from OpenAI: {fact}")
            return jsonify({"fact": fact}), 200
        except Exception as e:
            print(f"Error fetching fact: {e}")
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "No user in session"}), 403

def get_random_fact_from_openai():
    fact = call_openAI_for_fact()
    return fact


@app.route("/coaching_suggestions", methods=["GET", "POST"])
def coaching_suggestions():
    if "user" in session and session.get("user_type") == "Coach":
        if request.method == "POST":
            class_type = request.form.get("class_type")
            class_level = request.form.get("class_level")

            try:
                suggestions = get_ai_suggestions(class_type, class_level)
                return render_template("coaching_suggestions.html", suggestions=suggestions, class_type=class_type,
                                       class_level=class_level)
            except Exception as e:
                flash(f"An error occurred: {str(e)}", "danger")
                return render_template("coaching_suggestions.html", suggestions=None)

        return render_template("coaching_suggestions.html", suggestions=None)
    else:
        flash("You need to be logged in as a Coach to access this feature.", "danger")
        return redirect(url_for("login"))


@app.route("/edit_user_admin", methods=["GET", "POST"])
def edit_user_admin():
    if "user" in session and session.get("user_type") == "Admin":
        users = Users.query.all()
        selected_user = None

        if request.method == "POST":
            user_id = request.form.get("user_id")

            if not user_id:
                flash("No user selected. Please select a valid user.", "danger")
                return redirect(url_for("edit_user_admin"))

            selected_user = db.session.get(Users, user_id)
            print(f"User ID: {user_id}")
            print(f"Selected User: {selected_user}")

            if selected_user:
                selected_user.first_name = request.form.get("first_name")
                selected_user.last_name = request.form.get("last_name")
                selected_user.email = request.form.get("email")
                selected_user.password = request.form.get("password")
                selected_user.age = request.form.get("age")
                selected_user.weight = request.form.get("weight")
                selected_user.height = request.form.get("height")
                selected_user.user_type = request.form.get("user_type")

                db.session.commit()
                flash("User details updated successfully", "success")
                return redirect(url_for("edit_user_admin"))
            else:
                flash("Selected user not found. Please try again.", "danger")

        elif request.method == "GET" and "user_id" in request.args:
            user_id = request.args.get("user_id")
            if user_id:
                selected_user = db.session.get(Users, user_id)

        return render_template("edit_user_admin.html", users=users, selected_user=selected_user)
    else:
        flash("You are not authorized to view this page", "danger")
        return redirect(url_for("login"))

@app.route("/create_program", methods=["GET"])
def render_create_program():
    if "user" in session:
        email = session["email"]
        user = Users.query.filter_by(email=email).first()
        program_exists = bool(user.program)

        return render_template("create_program.html", program=user.program, program_exists=program_exists)
    else:
        return redirect(url_for("login"))


@app.route("/create_program", methods=["POST"])
def create_program():
    if "user" in session:
        email = session["email"]
        user = Users.query.filter_by(email=email).first()
        name = f"{user.first_name} {user.last_name}"

        try:
            print("calling OpenAI API...")
            response = call_openAI(name, user.age, user.gender, user.weight, user.height,
                                   user.fitness_goal, user.training_frequency, user.fitness_level)
            print(f"Response received from OpenAI: {response}")

            if response:
                user.program = response
                db.session.commit()
                return jsonify({"program": response}), 201
            else:
                return jsonify({"error": "No program data received"}), 500
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "No user in session"}), 403

@app.route("/ai_muscles")
def ai_muscles():
    if "user" not in session or session.get("user_type") != 'Trainee':
        return redirect(url_for("login"))

    return render_template("trainee.html")
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


@app.route("/interactive_feedback", methods=["GET", "POST"])
def interactive_feedback():
    if "user" not in session:
        return redirect(url_for("login"))

    # Retrieve the logged-in user's information
    userid = session.get("user_id")
    user = Users.query.filter_by(id=userid).first()
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        week_number = request.form.get("week_number", type=int)
        weight = request.form.get("weight", type=float)
        workout_count = request.form.get("workout_count", type=int)

        if not all([week_number, weight, workout_count]):
            flash("Invalid input. Please fill out all fields.", "danger")
            return redirect(url_for("interactive_feedback"))

        existing_entry = UserProgress.query.filter_by(user_id=user.id, week_number=week_number).first()

        if existing_entry:
            update_progress(existing_entry, weight, workout_count, user)
            flash("Progress updated successfully!", "success")
        else:
            create_new_progress(user, week_number, weight, workout_count)
            flash("Progress added successfully!", "success")

        db.session.commit()

    start_date, end_date = get_data_range_from_request(request)

    progress_entries = get_filtered_progress_entries(user.id, start_date, end_date)

    avg_training_frequency, avg_weight_change = calculate_averages(progress_entries)

    weeks, weights, workout_counts = extract_progress_data(progress_entries)

    ai_suggestions_text = generate_ai_suggestions(user, avg_training_frequency, avg_weight_change)

    user.ai_suggestions = ai_suggestions_text
    db.session.commit()

    return render_template(
        "interactive_feedback.html",
        user=user,
        weeks=weeks,
        weights=weights,
        workout_counts=workout_counts,
        avg_training_frequency=avg_training_frequency,
        avg_weight_change=avg_weight_change,
        progress_entries=progress_entries,
        start_date=format_date(start_date),
        end_date=format_date(end_date),
        suggestions=ai_suggestions_text
    )


def get_data_range_from_request(request):
    start_date = request.form.get("start_date", None)
    end_date = request.form.get("end_date", None)

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

    return start_date, end_date

def get_filtered_progress_entries(user_id, start_date, end_date):
    query = UserProgress.query.filter_by(user_id=user_id)
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        query = query.filter(UserProgress.date.between(start_date, end_date))
    return query.order_by(UserProgress.week_number).all()


def calculate_averages(progress_entries):
    total_weeks = len(progress_entries)
    if total_weeks == 0:
        return 0, 0

    total_workouts = sum(entry.workout_count for entry in progress_entries)

    # Ensure entries are sorted by week_number
    progress_entries = sorted(progress_entries, key=lambda entry: entry.week_number)

    # Calculate total weight change between the first and last week
    total_weight_change = progress_entries[-1].weight - progress_entries[0].weight if total_weeks > 1 else 0

    avg_training_frequency = total_workouts / total_weeks
    avg_weight_change = total_weight_change / total_weeks
    return avg_training_frequency, avg_weight_change


def extract_progress_data(progress_entries):
    """Extract week numbers, weights, and workout counts from progress entries for chart display."""
    # Sort entries to ensure correct order
    progress_entries = sorted(progress_entries, key=lambda entry: entry.week_number)
    weeks = [entry.week_number for entry in progress_entries]
    weights = [entry.weight for entry in progress_entries]
    workout_counts = [entry.workout_count for entry in progress_entries]
    return weeks, weights, workout_counts


def generate_ai_suggestions(user, avg_training_frequency, avg_weight_change):
    """ Generate AI suggestions based on user data and calculated averages. """
    return ai_suggestions(user_name=user.first_name,
        age=user.age,
        gender=user.gender,
        weight=user.weight,
        height=user.height,
        fitness_goal=user.fitness_goal,
        avg_training_frequency=avg_training_frequency,
        avg_weight_change=avg_weight_change,
        training_frequency=user.training_frequency,
        fitness_level=user.fitness_level,
        program=user.program
    )


def format_date(date):
    return date.strftime('%Y-%m-%d') if date else ''

@app.route("/user/result", methods=["POST"])
def user_accepted_result():
    return render_template("accepted_result.html")




@app.route("/add_progress", methods=["POST"])
def add_progress():
    if "user" not in session:
        return redirect(url_for("login"))

    email = session["email"]
    user = Users.query.filter_by(email=email).first()

    week_number = request.form.get("week_number")
    weight = request.form.get("weight")
    workout_count = request.form.get("workout_count")
    training_frequency = user.training_frequency

    if not all([week_number, weight, workout_count]):
        flash("Invalid input. Please fill out all fields.", "danger")
        return redirect(url_for("interactive_feedback"))

    existing_progress = UserProgress.query.filter_by(user_id=user.id, week_number=week_number).first()

    if existing_progress:
        update_progress(existing_progress, weight, workout_count, user)
        flash("Progress updated successfully!", "success")
    else:
        create_new_progress(user, week_number, weight, workout_count)
        flash("Progress added successfully!", "success")

    db.session.commit()

    return redirect(url_for("interactive_feedback"))


def update_progress(progress, weight, workout_count, user) -> None:
    progress.weight = float(weight)
    progress.workout_count = int(workout_count)
    progress.first_name = user.first_name
    progress.last_name = user.last_name
    progress.fitness_goal = user.fitness_goal
    progress.training_frequency = user.training_frequency

    db.session.commit()

    # Recalculate averages for all entries
    progress_entries = get_filtered_progress_entries(user.id, None, None)
    avg_training_frequency, avg_weight_change = calculate_averages(progress_entries)

    # Update all entries with new averages
    for entry in progress_entries:
        entry.avg_training_frequency = avg_training_frequency
        entry.avg_weight_change = avg_weight_change

    db.session.commit()



def create_new_progress(user, week_number, weight, workout_count) -> None:
    new_progress = UserProgress(
        user_id=user.id,
        week_number=int(week_number),
        first_name=user.first_name,
        last_name=user.last_name,
        fitness_goal=user.fitness_goal,
        training_frequency=user.training_frequency,
        weight=float(weight),
        workout_count=int(workout_count)
    )
    db.session.add(new_progress)

def get_previous_progress(user_id):

    previous_progress = UserProgress.query.filter_by(user_id=user_id).order_by(UserProgress.week_number.desc()).limit(5).all()
    progress_data = [{
        "week_number": entry.week_number,
        "weight": entry.weight,
        "workout_count": entry.workout_count
    } for entry in previous_progress]

    return progress_data


def create_users_table():
    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table('users'):
            db.create_all()
            print("Users table created!")
        else:
            print("Users table already exists!")

def create_user_progress_table():
    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table('user_progress'):
            db.create_all()
            print("UserProgress table created!")
        else:
            print("UserProgress table already exists!")


@app.route("/ask_openai", methods=["GET", "POST"])
def ask_openai_view():
    if "user" in session:
        if request.method == "POST":
            prompt = request.form.get('prompt')
            try:
                response = ask_openai(prompt)
                return render_template("ask_openai.html", result=response)
            except Exception as e:
                flash(f"An error occurred: {str(e)}", "danger")
                return render_template("ask_openai.html", result=None)
        return render_template("ask_openai.html")
    else:
        flash("You need to be logged in to access this feature.", "danger")
        return redirect(url_for("login"))

@app.route("/diet_suggestions", methods=["GET", "POST"])
def diet_suggestions():
    if "user" in session:
        if request.method == "POST":
            # Retrieve form data
            user_id = session["user_id"]
            user = Users.query.get(user_id)

            diet_type = request.form.get("diet_type")
            try:
                # Generate AI diet suggestions
                suggestions = get_ai_diet_suggestions(user.height, user.weight, user.age, user.fitness_goal, diet_type)
                return render_template("diet_suggestions.html", suggestions=suggestions, diet_type=diet_type)
            except Exception as e:
                flash(f"An error occurred: {str(e)}", "danger")
                return render_template("diet_suggestions.html", suggestions=None)

        return render_template("diet_suggestions.html", suggestions=None)
    else:
        flash("You need to be logged in as a Coach to access this feature.", "danger")
        return redirect(url_for("login"))


def load_fake_data():
    fake_names = ['John', 'Jane', 'Alice', 'Bob', 'Charlie']
    fake_domains = ['gmail.com']
    genders = ['MALE', 'FEMALE']
    fake_goals = ['Weight Loss', 'Muscle Gain', 'Maintain weight']
    with app.app_context():
        for i in range(7):
            user = Users(
                first_name=random.choice(fake_names),
                last_name=random.choice(fake_names),
                email=f'{i}@{random.choice(fake_domains)}',
                password='1',
                gender=random.choice(genders),
                age=random.randint(18, 65),
                weight=random.uniform(50.0, 100.0),
                height=random.uniform(150.0, 200.0),
                user_type=random.choice(['Admin', 'Trainee', 'Coach']),
                about_me='Just a fun user.',
                program='Sample Program',
                fitness_level=random.choice(['Beginner', 'Intermediate', 'Advanced']),
                training_frequency=random.randint(1, 7),
                fitness_goal=random.choice(fake_goals)
            )
            try:
                db.session.add(user)
                db.session.commit()
            except SQLAlchemyError as e:
                print(f"Error adding user {i}: {e}")
                db.session.rollback()

    print("Fake data loaded!")



if __name__ == "__main__":
    #create_users_table()
    #create_topics_table()
    #create_user_progress_table()
    #load_fake_data()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5001)
