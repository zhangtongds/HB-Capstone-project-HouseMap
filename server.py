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

# conn = httplib.HTTPSConnection("search.onboard-apis.com") 

headers = { 
    'accept': "application/json", 
    'apikey': ONBOARD_KEY, 
    } 


@app.route("/")
def homepage():
    """Show homepage."""
    search_type = request.args.get('search_type')
    if search_type is None:
        search_type = 'postalcode'
    session['search_type'] = search_type
    field_map = {
        'postalcode': ['postalcode'],
        'address': ['address', 'city', 'state'],
        'cityName': ['city','state']
    }
    allowed_fields = field_map[search_type]
    return render_template("homepage.html", allowed_fields=allowed_fields, search_type=search_type)

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
    """Get user input information."""
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

        return render_template("address-search-results.html", property_id=property_id, address=address, city=city, state=state, zipcode_ten=zipcode_ten, sale_history=sale_history)
        # return redirect("/")

    
    else:
        params_name_map = { "property_type": "propertyType",
                            "max_no_bed": "maxBeds",
                            "min_no_bed": "minBeds",
                            "max_no_bath": "maxBathsTotal",
                            "min_no_bath": "minBathsTotal",
                            "price_from": "minAssdTtlValue",
                            "price_to": "maxAssdTtlValue",
                            "trans_date_from": "startSaleTransDate",
                            "trans_date_to": "endSaleTransDate"}

        search_params_key = [search_type, 'property_type', 'max_no_bed', 'min_no_bed', 'max_no_bath', 'min_no_bath', 'price_from', 'price_to', 'trans_date_from', 'trans_date_to']
       
        url = "https://search.onboard-apis.com/propertyapi/v1.0.0/sale/snapshot?pageSize=200000&"
        url_params = []
        city = request.args.get('city')
        state = request.args.get('state')
        for search_param in search_params_key:
            value = request.args.get(search_param)
            # print search_param, value
            session[search_param] = value
            print search_param, session[search_param]            
            if search_param == 'cityName':
                request_url = url + '&'.join(url_params)
                request_url = request_url + 'cityName=' + city
                
            if value != None and value != "":
                value = value.replace(" ", "%20")
                url_params.append("{}={}".format(params_name_map.setdefault(search_param, search_param), value))
            if search_param == 'postalcode':
                request_url = url + '&'.join(url_params)
        
        sales_response = requests.get(request_url, headers=headers) 
        sales_data = sales_response.json()
        # print pprint.pprint(sales_data)
        property_sales = []
    
        for item in sales_data['property']:
            lst_0 = item['identifier']['obPropId']
            lst_1 = item['sale']['amount']['saleamt']
            if lst_1 != 0:
                property_sales.append([lst_0,lst_1])
        no_results = len(property_sales)
        property_sales = np.array(property_sales)
        if no_results >0:
            median_price = np.median(property_sales, axis=0)
            percent_25_price = np.percentile(property_sales, 25, axis=0)
            percent_75_price = np.percentile(property_sales, 75, axis=0)
            area = sales_data['property'][0]['address']['line2']
         
            if search_type == 'postalcode':
                zip_code = request.args.get(search_type)
                trend_url = "https://search.onboard-apis.com/propertyapi/v1.0.0/salestrend/snapshot?geoid=ZI{}&interval=yearly&startyear=2000&endyear=2018".format(zip_code)
                trend_response = requests.get(trend_url, headers=headers)
                trend_data = trend_response.json()
                # print pprint.pprint(trend_data)
                area_trend = []
                for item in trend_data['salestrends']:
                    year = item['daterange']['end']
                    avg_price = item['SalesTrend']['avgsaleprice']
                    home_count = item['SalesTrend']['homesalecount']
                    med_price = item['SalesTrend']['medsaleprice']
                    area_trend.append([year, avg_price, home_count, med_price])
                return render_template("other-search-results.html", median_price=median_price, no_results=no_results, area=area, percent_25_price=percent_25_price, percent_75_price=percent_75_price, trend_data=trend_data, area_trend=area_trend)

            return render_template("other-search-results.html", median_price=median_price, no_results=no_results, area=area, percent_25_price=percent_25_price, percent_75_price=percent_75_price)
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