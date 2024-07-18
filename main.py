from flask import Flask, redirect, url_for, render_template, request, session, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "hello"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    first_name = db.Column("first_name", db.String(100))
    last_name = db.Column("last_name", db.String(100))
    email = db.Column("email", db.String(100))
    password = db.Column("password", db.String(100))
    age = db.Column("age", db.Integer)
    weight = db.Column("weight", db.Float)
    height = db.Column("height", db.Float)

    def __init__(self, first_name, last_name, email, password, age, weight, height):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.age = age
        self.weight = weight
        self.height = height


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        session["user"] = user
        found_user = Users.query.filter_by(first_name=user).first()
        if found_user:
            session["email"] = found_user.email
        else:
            usr = Users(user, "", "", "", 0, 0, 0)
            db.session.add(usr)
            db.session.commit()
            get_flashed_messages(with_categories=True)
            flash("You've logged successfully, bro")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            get_flashed_messages(with_categories=True)
            flash("Already logged in, bro")
            return redirect(url_for("user"))

        return render_template("login.html")


@app.route("/user", methods=["POST", "GET"])
def user():
    email = None
    if "user" in session:
        user = session["user"]
        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_user = Users.query.filter_by(first_name=user).first()
            found_user.email = email
            db.session.commit()
            get_flashed_messages(with_categories=True)
            flash("Email was saved!, bro")
        else:
            if "email" in session:
                email = session["email"]
                get_flashed_messages(with_categories=True)
                flash("Already logged in, bro")
        return render_template("user.html", email=email)
    else:
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("email", None)
    get_flashed_messages(with_categories=True)
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

        new_user = Users(first_name, last_name, email, password, age, weight, height)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful!", "success")
        return redirect(url_for("login"))
    return render_template("LoginPage.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
