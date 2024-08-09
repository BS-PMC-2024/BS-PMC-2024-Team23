from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = "hello"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
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

    def __init__(self, user_type, first_name, last_name, email, password, age, weight, height):
        self.user_type = user_type
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.age = age
        self.weight = weight
        self.height = height

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

        return render_template("admin.html", values=users, total_users=total_users, total_coaches=total_coaches, total_trainees=total_trainees)
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
        return render_template("user.html", email=email, topics=topics)
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

        new_user = Users(user_type, first_name, last_name, email, password, age, weight, height)
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

    return render_template("LoginPage.html")

@app.route("/coach", methods=["GET", "POST"])
def coach():
    if "user" in session:
        email = session["email"]
        user = Users.query.filter_by(email=email).first()
        topics = Topics.query.all()  # לקבל את כל הנושאים

        if request.method == "POST":
            user.about_me = request.form["about_text"]
            db.session.commit()
            flash("About Me updated successfully!", "success")
            return redirect(url_for("coach"))

        return render_template("coacher.html", coach_info=user.about_me, topics=topics)
    else:
        flash("You are not logged in", "danger")
        return redirect(url_for("login"))

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

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
