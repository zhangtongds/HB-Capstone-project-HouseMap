import pprint
import os
from jinja2 import StrictUndefined
import requests
# import httplib
from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension
from model import User, Favorite, Search, Property, Sale, connect_to_db, db
from seed import parse_address_from_homepage
import json

app = Flask(__name__)
app.secret_key = "ABC"
ONBOARD_KEY=os.environ['ONBOARD_KEY']

ONBOARD_URL = "http://search.onboard-apis.com"

# conn = httplib.HTTPSConnection("search.onboard-apis.com") 

headers = { 
    'accept': "application/json", 
    'apikey': ONBOARD_KEY, 
    } 


@app.route("/")
def homepage():
    """Show homepage."""

    return render_template("homepage.html")

@app.route("/register", methods=['GET'])
def show_registration():
    """Shows registration form"""

    return render_template("register.html")

@app.route('/register', methods=['POST'])
def register_form():

    email = request.form.get("user-email")
    password = request.form.get("user-password")
    print email
    found_email = User.query.filter(User.email == email).first()
    print found_email
    print "============"

    if found_email:
        flash("You alreday have an account, please log in.")
        return redirect('/login')
    else:
        user = User(email=email, password=password)
        # print user
        # print "============"
        db.session.add(user)
        db.session.commit()
        flash("You successfully made an account.")
        return redirect('/')

@app.route("/login", methods=['GET'])
def show_login():
    """Shows login page"""

    return render_template("login.html")

@app.route("/login", methods=['POST'])
def verify_login():
    email = request.form.get("user-email")
    password = request.form.get("user-password")
    # print email
    found_user = User.query.filter(User.email== email).first()
    # print find_user

    if found_user:
        if found_user.password == password:   
            session['user_id'] = found_user.user_id
            # print found_user
            flash("You were successfully logged in")
            # return redirect("/users/" + str(find_user.user_id))
            return redirect("/")  # this is a temp place holder

        else:
            flash('Please enter a valid email/password')
            return redirect('/login')
    else:
        flash('Please enter a valid email/password')
        return redirect('/login')

@app.route("/logout")
def process_logout():
    """Log user out."""

    del session['user_id']
    flash("You were successfully logged out.")
    return redirect("/")


@app.route("/search")
def get_user_input():
    """Get user input information."""
    info_type = request.args.get("info_type")
    
    if info_type == 'address':
        address = request.args.get("address")
        city = request.args.get("city")
        state = request.args.get("state")
        # print address, city, state
        address1 = address.replace(" ", "%20")
        address2 = city + "%2C%20" + state
        reaquest_url = "/propertyapi/v1.0.0/property/detail?address1=" + address1 + "&address2=" + address2
        response = requests.get(ONBOARD_URL + reaquest_url, headers=headers) 
        data = response.json()
        # json_string = json.dumps(data)
        # data = json.loads(json_string)
        # print pprint.pprint(data)
        session['property_id'] = data['property'][0]['identifier']['obPropId']
        print session['property_id']
    return render_template("search-results.html")



if __name__ == "__main__":

    connect_to_db(app)
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(app)
    app.run(host = '0.0.0.0')