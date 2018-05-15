import pprint
import os
from jinja2 import StrictUndefined
import requests
# import httplib
from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension
from model import User, Favorite, Search, Property, Sale, connect_to_db, db
import utility
import json
import numpy as np


app = Flask(__name__)
app.secret_key = "ABC"
ONBOARD_KEY=os.environ['ONBOARD_KEY']

ONBOARD_URL = "http://search.onboard-apis.com"

headers = { 
    'accept': "application/json", 
    'apikey': ONBOARD_KEY, 
    } 


@app.route("/")
def homepage():
    """Show homepage."""
    search_type = request.args.get('search_type')
    if search_type is None:
        search_type = 'zipcode'
    session['search_type'] = search_type

    field_map = {
        'zipcode': ['zipcode'],
        'address': ['address', 'city', 'state'],
        'city': ['city', 'state']
    }
    allowed_fields = field_map[search_type]
    return render_template("homepage.html", allowed_fields=allowed_fields, search_type=search_type)
    # return render_template("login.html")
@app.route("/register", methods=['GET'])
def show_registration():
    """Shows registration form"""

    return render_template("register.html")

@app.route('/register', methods=['POST'])
def register_form():

    fname = request.form.get("fname")
    lname = request.form.get("lname")
    email = request.form.get("user-email")
    password = request.form.get("user-password")
    zipcode = request.form.get("zipcode")
    found_email = User.query.filter(User.email == email).first()

    if found_email:
        flash("You alreday have an account, please log in.")
        return redirect('/login')
    else:
        user = User(fname= fname, lname=lname, email=email, password=password, zipcode=zipcode)
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
            return redirect("/users/" + str(found_user.user_id))
            
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

@app.route("/users/<user_id>")
def show_page(user_id):
    """Shows users page"""
    user = User.query.filter(User.user_id == user_id).first()
    

    return render_template("user.html", user=user)


@app.route("/search")
def get_user_input():
    """Get user input information, pass to api and get the results."""

    search_type = session['search_type']
    if search_type == 'address':
        address = request.args.get("address")
        city = request.args.get("city")
        state = request.args.get("state")

        address1 = address.replace(" ", "%20")
        address2 = city + "%2C%20" + state

        property_url = "/propertyapi/v1.0.0/property/detail?"
        data_prop = utility.get_result_from_api(ONBOARD_URL, property_url, headers, {"address1": address1, "address2": address2})
        
        sale_url = "/propertyapi/v1.0.0/saleshistory/detail?"
        data_sale = utility.get_result_from_api(ONBOARD_URL, sale_url, headers, {"address1": address1, "address2": address2})

        property_id = utility.get_property_id(data_prop)
        zipcode_ten = utility.get_ten_digits_zipcode(data_prop)
        sale_history = utility.get_sale_history(data_sale)
        session['search_prop'] = data_prop
        session['search_sale'] = data_sale

        return render_template("address-search-results.html", property_id=property_id,
                                                            address=address,
                                                            city=city,
                                                            state=state,
                                                            zipcode_ten=zipcode_ten,
                                                            sale_history=sale_history)

    else:
        params_key = ['zipcode', 'city', 'state', 'property_type', 'max_no_bed', 'min_no_bed', 'max_no_bath', 'min_no_bath', 'price_from', 'price_to', 'trans_date_from', 'trans_date_to']
        sale_url = "/propertyapi/v1.0.0/sale/snapshot?pageSize=200000&"
        search_params = {}
        for search_param in params_key:
            value = request.args.get(search_param)

            if value != None and value != "":
                search_params[search_param] = value
         
        sales_data = utility.get_result_from_api(ONBOARD_URL, sale_url, headers, search_params)  
        # pprint.pprint(sales_data)
       
        property_sales = utility.get_area_sale_list(sales_data)

        no_results = len(property_sales)
        property_sales = np.array(property_sales)
        if no_results >0:
            median_price = np.median(property_sales, axis=0)
            percent_25_price = np.percentile(property_sales, 25, axis=0)
            percent_75_price = np.percentile(property_sales, 75, axis=0)
            area = sales_data['property'][0]['address']['line2']

            if search_type == 'zipcode':
                zip_code = request.args.get(search_type)
                trend_url = "https://search.onboard-apis.com/propertyapi/v1.0.0/salestrend/snapshot?geoid=ZI{}&interval=yearly&startyear=2000&endyear=2018".format(zip_code)
                trend_response = requests.get(trend_url, headers=headers)
                trend_data = trend_response.json()
                # print pprint.pprint(trend_data)
                area_trend = utility.get_area_sale_trend(trend_data)
                return render_template("other-search-results.html", median_price=median_price,
                                                                    no_results=no_results,
                                                                    area=area,
                                                                    percent_25_price=percent_25_price,
                                                                    percent_75_price=percent_75_price,
                                                                    trend_data=trend_data,
                                                                    area_trend=area_trend)

            return render_template("other-search-results.html", median_price=median_price,
                                                                no_results=no_results,
                                                                area=area,
                                                                percent_25_price=percent_25_price,
                                                                percent_75_price=percent_75_price)
        else:
            return render_template("other-search-results.html", no_results=0)
        # return redirect("/")
        

@app.route("/search", methods=["POST"])
def save_search():
    save_type = request.form.get('save_type')
    if save_type == 'search':
        # print 'Success****'
        if session.get('user_id'):
            # print 'success====='
            print session
            search = Search(
                user_id=session.get('user_id'),
                zipcode=session.get('postalcode'),
                city=session.get('city'),
                state=session.get('state'),
                trans_type=session.get('trans_type'),
                max_no_bed=session.get('max_no_bed'),
                min_no_bed=session.get('min_no_bed'),
                min_no_bath=session.get('min_no_bath'),
                max_no_bath=session.get('max_no_bath'),
                price_from=session.get('price_from'),
                price_to=session.get('price_to'),
                trans_date_from=session.get('trans_date_from'),
                trans_date_to=session.get('trans_date_to'),
                property_type=session.get('property_type')
                )
            db.session.add(search)
            db.session.commit()
            # session.clear()
     # if save_type == 'search':
     #    if session.get('user_id'):

     #        _property = Property

    return jsonify({'Result': save_type})
            
     

    


if __name__ == "__main__":

    connect_to_db(app)
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(app)
    app.run(host = '0.0.0.0')