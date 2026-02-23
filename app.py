from flask import Flask, render_template, request, redirect, url_for
from flask_login import (
    LoginManager, UserMixin,
    login_user, logout_user,
    login_required, current_user
)
import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

connection = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = connection[os.getenv("DB_NAME")]

app = Flask(__name__)
app.secret_key = "dev" # change this to an environment variable later

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # redirect here if not logged in

class User(UserMixin):
    def __init__(self, user):
        self.id = user["_id"]
        self.email = user["email"]
        self.username = user["username"]

@login_manager.user_loader
def load_user(user_id):
    # session stores user's _id; load user by _id
    try:
        oid = ObjectId(user_id) if isinstance(user_id, str) else user_id
        user = db.users.find_one({"_id": oid})
        if user:
            return User(user)
    except Exception:
        pass
    return None

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        # check the database
        user = db.users.find_one({"email": email})
        if user and user["password"] == password:
            login_user(User(user))
            return redirect(url_for("home"))

        return render_template("login.html", error="Invalid email or password.")

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not email or not username or not password:
            return render_template("signup.html", error="All fields are required.")

        if db.users.find_one({"email": email}):
            return render_template("signup.html", error="Email already taken.")

        db.users.insert_one({
            "email": email,
            "username": username,
            "password": password,
        })

        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def home():
    return render_template("home.html")

@app.route("/create-recipe")
@login_required
def create_recipe():
    return render_template("create_recipe.html")

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")

@app.route("/search")
@login_required
def search():
    return render_template("search.html")

if __name__ == "__main__":
    app.run(debug=True)