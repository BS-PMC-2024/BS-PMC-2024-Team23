from flask import Flask, redirect, url_for, render_template, request, session, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = "hello"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    first_name = db.Column("first_name", db.String(100))
    last_name = db.Column("last_name", db.String(100))
    email = db.Column("email", db.String(100))
    password = db.Column("password", db.String(100))
    age = db.Column("age", db.Integer)
    weight = db.Column("weight", db.Float)
    height = db.Column("height", db.Float)
    user_type = db.Column("user_type", db.String(50))  # שדה סוג המשתמש החדש
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
                return redirect(url_for("admin"))  # הוספת ההפניה לדף Admin
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
                return redirect(url_for("admin"))  # הוספת ההפניה לדף Admin
        return render_template("LoginPage.html")


@app.route("/admin")
def admin():
    if "user" in session and session.get("user_type") == "Admin":
        return render_template("admin.html", values=Users.query.all())
    else:
        flash("You are not authorized to view this page", "danger")
        return redirect(url_for("login"))


@app.route("/user", methods=["POST", "GET"])
def user():
    if "user" in session:
        user = session["user"]
        if request.method == "POST":
            email = request.form["email"]
            goal = request.form["goal"]
            session["email"] = email
            # אפשר להוסיף את ה-goal למשתמש ב-DATABASE כאן
            flash("Information updated successfully!", "success")
            return redirect(url_for("user"))

        if "email" in session:
            email = session["email"]
            flash("Already logged in", "info")
        return render_template("user.html", email=email)
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("email", None)
    flash("Sorry to see you go, bro", "info")
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
        if request.method == "POST":
            user.about_me = request.form["about_text"]  # עדכון הטקסט
            db.session.commit()
            flash("About Me updated successfully!", "success")
            return redirect(url_for("coach"))
        return render_template("coacher.html", coach_info=user.about_me)
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






if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
