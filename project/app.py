
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///foodstand.db")



@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of recipes"""
    # Retrieve the user's recipes from the database
    recipes = db.execute("SELECT * FROM recipes WHERE creator_id = ?", session["user_id"])

    # For each recipe, retrieve the corresponding ingredient data
    for recipe in recipes:
        recipe_id = recipe['recipe_id']
        ingredients = db.execute("SELECT * FROM ingredient_data WHERE recipe_id = ?", recipe_id)
        recipe['ingredients'] = ingredients

    # Render the HTML template and pass the recipes data to it
    return render_template("index.html", recipes=recipes)


@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    """Edit a recipe"""

    # Get the recipe ID from the request
    recipe_id = request.form.get("recipe_id")

    # Get the recipe data from the database
    recipe_data = db.execute("SELECT * FROM recipes WHERE recipe_id = ? AND creator_id = ?", recipe_id, session["user_id"])
    print(recipe_data)
    if len(recipe_data) != 1:
        # Recipe not found or user is not the creator of the recipe
        return apology("invalid recipe")

    # Make ingredients list
    ingredients = []
    result = db.execute("SELECT * FROM ingredient_data WHERE recipe_id = ?", recipe_id)
    for row in result:
        ingredients.append(row)

    if request.method == "POST":
        # Check for misusage
        if not (request.form.get("dishName")):
            # this may mean that post came from index page. Unsure how to check more efficiently,
            # so this will redirect to edit page
            return render_template("edit.html", recipe_data=recipe_data, ingredients=ingredients)

        if not (request.form.get("ingredient0")):
            return apology("missing ingredients")

        if not (request.form.get("quantity0")):
            return apology("missing quantities")

        if not (request.form.get("instructions")):
            return apology("missing instructions")

        # Update the recipe data in the database
        db.execute("""UPDATE recipes SET recipe_name = ?, recipe_instructions = ?,
                    recipe_description = ?, recipe_type = ?
                    WHERE recipe_id = ? AND creator_id = ?""", request.form.get("dishName"), request.form.get("instructions"), request.form.get("description"), request.form.get("type"), recipe_id, session["user_id"])

        # Delete existing ingredients for this recipe
        db.execute("DELETE FROM ingredient_data WHERE recipe_id = :recipe_id", recipe_id=recipe_id)

        # Insert new ingredients for this recipe
        form_data = request.form
        for i in range(len(form_data)//4):
            ingredient_name = form_data[f'ingredient{i}']
            quantity = float(form_data[f'quantity{i}'])
            unit = form_data[f'unit{i}']
            db.execute("INSERT INTO ingredient_data(recipe_id, ingredient, quantity, unit) VALUES(?, ?, ?, ?)", recipe_id, ingredient_name, quantity, unit)


    else:
        render_template("edit.html", recipe_data=recipe_data, ingredients=ingredients)


@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    # Get the recipe_id from the form submission
    recipe_id = request.form.get("recipe_id")

    # Check that the recipe exists and that the current user is the creator of the recipe
    recipe_data = db.execute("SELECT * FROM recipes WHERE recipe_id = ? AND creator_id = ?", recipe_id, session["user_id"])
    if len(recipe_data) != 1:
        # Recipe not found or user is not the creator of the recipe
        return apology("invalid recipe or user")

    # Delete the corresponding records in the ingredient_data table
    db.execute("DELETE FROM ingredient_data WHERE recipe_id = ?", recipe_id)

    # Delete the recipe from the recipes table
    db.execute("DELETE FROM recipes WHERE recipe_id = ? AND creator_id = ?", recipe_id, session["user_id"])
    # Redirect back to the index page
    return redirect("/")


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Create a new recipe for the portfolio"""

    if request.method == "POST":
        # Check for misusage
        if not (request.form.get("dishName")):
            return apology("missing dish name")

        if not (request.form.get("ingredient0")):
            return apology("missing ingredients")

        if not (request.form.get("quantity0")):
            return apology("missing quantities")

        if not (request.form.get("instructions")):
            return apology("missing instructions")

        # Place important details into both databases
        db.execute("INSERT INTO recipes(creator_id, recipe_name, recipe_instructions, recipe_description, recipe_type) VALUES(?, ?, ?, ?, ?);", session["user_id"], request.form.get("dishName"), request.form.get("instructions"), request.form.get("description"), request.form.get("type"))
        row = db.execute("SELECT * FROM recipes ORDER BY recipe_id DESC LIMIT 1;")

        # Extract the rowid from the returned row
        recipe_id = row[0]["recipe_id"]

        form_data = request.form
        for i in range((len(form_data) - 4) // 3):
            ingredient_name = form_data[f'ingredient{i}']
            quantity = float(form_data[f'quantity{i}'])
            unit = form_data[f'unit{i}']
            db.execute("INSERT INTO ingredient_data(recipe_id, ingredient, quantity, unit) VALUES(?, ?, ?, ?)", recipe_id, ingredient_name, quantity, unit)

        # Return to home
        return redirect("/")


    else:
        return render_template("create.html")


@app.route("/lookup", methods=["GET", "POST"])
@login_required
def lookup():
    """Get recipe list"""
    if request.method == "POST":
        # Ensure recipe is typed
        if not request.form.get("recipe"):
            return apology("must provide recipe name", 400)


        recipe_list = db.execute("SELECT * FROM recipes WHERE name LIKE ?", request.form.get("recipe"))
        # Ensure recipe exists
        if recipe_list < 1:
            return apology("no results")

        # return recipe page
        return render_template("recipes_found.html", recipes=recipe_list)


    else:
        return render_template("lookup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)

        # Ensure password was submitted
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)


        username = request.form.get("username")
        # rows for same username
        rows = db.execute("SELECT * FROM users WHERE username = ?;", username)

        # Ensure db doesn't have username
        if len(rows) != 0:
            return apology(f"The username '{username}' already exists. Please try another.")

        # If all terms meet requirements, hash password and add to db
        hashed_password = generate_password_hash(request.form.get("password"))
        id = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hashed_password)

        # Setup user session and send to homepage, otherwise send to register page
        session["user_id"] = id
        return redirect("/")

    else:
        return render_template("register.html")
