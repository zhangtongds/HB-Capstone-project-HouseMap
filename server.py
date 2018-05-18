import pprint
import os
from jinja2 import StrictUndefined
import requests
# import httplib
from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension
from model import User, Search, Property, Sale, connect_to_db, db
import utility
import json
import numpy as np
import ast
import datetime


app = Flask(__name__)
app.secret_key = "ABC"
ONBOARD_KEY=os.environ['ONBOARD_KEY']

ONBOARD_URL = "http://search.onboard-apis.com/propertyapi/v1.0.0/"

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
    print user_id,"-------------"
    searches = Search.query.filter(Search.user_id == user_id).all()
    properties = Property.query.filter(Property.user_id == user_id).all()
    print searches, "!!!!!!!!"
    print properties, "**********"

    return render_template("user.html", user=user, searches=searches, properties=properties)


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

        property_url = "property/detail?"
        data_prop = utility.get_result_from_api(ONBOARD_URL, property_url, headers, {"address1": address1, "address2": address2})
        pprint.pprint(data_prop)
        sale_url = "saleshistory/detail?"

        data_sale = utility.get_result_from_api(ONBOARD_URL, sale_url, headers, {"address1": address1, "address2": address2})
        property_id = utility.get_property_id(data_prop)
        zipcode_ten = utility.get_ten_digits_zipcode(data_prop)
        full_address = utility.get_full_address_from_result(data_prop)
        latitude = utility.get_latitude_from_result(data_prop)
        longitude = utility.get_longitude_from_result(data_prop)
        no_beds = utility.get_no_beds_from_result(data_prop)
        no_baths = utility.get_no_beds_from_result(data_prop)
        address_params = {"property_id": str(property_id),
                                "address": str(full_address),
                                "latitude": str(latitude),
                                "longitude": str(longitude),
                                "no_of_room": str(no_beds),
                                "no_of_bath": str(no_baths)} 
        print address_params
        print type(latitude)                      
        if data_sale['status']['code'] == 1:
            # Success without result
            return render_template("address-search-results.html",sale_history=0, address_params=address_params)    
        else:
            sale_history = utility.get_sale_history(data_sale)
            return render_template("address-search-results.html", sale_history=sale_history, address_params=address_params)

    else:
        params_key = ['zipcode', 'city', 'property_type', 'max_no_bed', 'min_no_bed', 'max_no_bath', 'min_no_bath', 'price_from', 'price_to', 'trans_date_from', 'trans_date_to']
        sale_url = "sale/snapshot?pageSize=200000&"
        search_params = {}
        for search_param in params_key:
            value = request.args.get(search_param)
            session[search_param] = value
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
                                                                    area_trend=area_trend,
                                                                    search_params=search_params
                                                                    )

            return render_template("other-search-results.html", median_price=median_price,
                                                                no_results=no_results,
                                                                area=area,
                                                                percent_25_price=percent_25_price,
                                                                percent_75_price=percent_75_price,
                                                                search_params=search_params
                                                                )
        else:
            return render_template("other-search-results.html", no_results=0)
        # return redirect("/")
        

@app.route("/search", methods=["POST"])
def save_search():
    save_type = request.form.get('save_type')
    save_data = request.form.get('save_data')
    # Parsing the unicode into a dictionary.
    save_data = ast.literal_eval(save_data)
    if session.get('user_id'):
        if save_type == 'search':
            search = Search(
                user_id=session.get('user_id'),
                zipcode=save_data.get('zipcode'),
                city=save_data.get('city'),
                state=save_data.get('state'),
                trans_type=save_data.get('trans_type'),
                max_no_bed=save_data.get('max_no_bed'),
                min_no_bed=save_data.get('min_no_bed'),
                min_no_bath=save_data.get('min_no_bath'),
                max_no_bath=save_data.get('max_no_bath'),
                price_from=save_data.get('price_from'),
                price_to=save_data.get('price_to'),
                trans_date_from=save_data.get('trans_date_from'),
                trans_date_to=save_data.get('trans_date_to'),
                property_type=save_data.get('property_type'),
                saved_date=datetime.datetime.now(),
                saved_by_user=True
                )

            db.session.add(search)
            db.session.commit()

        if save_type == 'address':
            save_data = request.form.get('save_data')
            save_data = ast.literal_eval(save_data)
            # print save_data
            _property = Property(
                user_id=session.get('user_id'),
                property_id=save_data.get('property_id'),
                address=save_data.get('address'),
                latitude=float(save_data.get('latitude')),
                longitude=float(save_data.get('longitude')),
                no_of_beds=int(save_data.get('no_of_room')),
                no_of_baths=float(save_data.get('no_of_bath')),
                saved_date=datetime.datetime.now(),
                saved_by_user=True
                )
            db.session.add(_property)
            db.session.commit()


    return jsonify({'Result': save_data})
            
# @app.route("/map")
# def save_search():

#     return render_template("map.html")    

    


if __name__ == "__main__":

    connect_to_db(app)
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(app)
    app.run(host = '0.0.0.0')