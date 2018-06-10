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
import zillow
import random


app = Flask(__name__)
app.secret_key = "ABC"
ONBOARD_KEY = os.environ['ONBOARD_KEY']
ZILLOW_KEY = os.environ['ZWSID']
api = zillow.ValuationApi()

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
        'address': ['address'],
        'city': ['city']
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
    found_user = User.query.filter(User.email== email).first()

    if found_user:
        if found_user.password == password:   
            session['user_id'] = found_user.user_id
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
    searches = Search.query.filter(Search.user_id == user_id).all()
    properties = Property.query.filter(Property.user_id == user_id).all()

    return render_template("user.html", user=user, searches=searches, properties=properties)


@app.route("/search")
def get_user_input():
    """Get user input information, pass to api and get the results."""
    try:
        search_type = session['search_type']
        if search_type == 'address':
            address = request.args.get("address")
            if address:
                address = address.split(", ")
                city = address[1].replace(" ", "%20")
                state = address[2]
                address1 = address[0].replace(" ", "%20")
                address2 = city + "%2C%20" + state
                property_url = "property/detail?"
                data_prop = utility.get_result_from_api(ONBOARD_URL, property_url, headers, {"address1": address1, "address2": address2})
                # pprint.pprint(data_prop)
                sale_url = "saleshistory/detail?"

                data_sale = utility.get_result_from_api(ONBOARD_URL, sale_url, headers, {"address1": address1, "address2": address2})
                # pprint.pprint(data_sale)
                property_id = utility.get_property_id(data_prop)
                zipcode_ten = utility.get_ten_digits_zipcode(data_prop)
                full_address = utility.get_full_address_from_result(data_prop)
                latitude = utility.get_latitude_from_result(data_prop)
                longitude = utility.get_longitude_from_result(data_prop)
                no_beds = utility.get_no_beds_from_result(data_prop)
                no_baths = utility.get_no_beds_from_result(data_prop)

                county = utility.get_county(data_prop)
                wall_type = utility.get_wall_type(data_prop)
                bldg_type = utility.get_bdlg_type(data_prop)
                prop_size = utility.get_prop_size(data_prop)
                lot_size = utility.get_lot_size(data_prop)
                year_built = utility.get_year_built(data_prop)
                last_modified = utility.get_last_modified(data_prop)
                z_address = str(full_address)[:-6]
                z_postalcode = str(full_address)[-5:]
                # print z_address,"============",z_postalcode, "+++++++++++++++"
                # Calling Zillow API
                z_data = api.GetSearchResults(ZILLOW_KEY, z_address, z_postalcode)

                if z_data:
                    z_url = z_data.links.home_details
                print z_url
                address_params = {"property_id": str(property_id),
                                        "address": str(full_address),
                                        "latitude": str(latitude),
                                        "longitude": str(longitude),
                                        "no_of_room": str(no_beds),
                                        "no_of_bath": str(no_baths),
                                        "county": str(county),
                                        "wall_type": str(wall_type),
                                        "bldg_type": str(bldg_type),
                                        "lot_size": str(lot_size),
                                        "year_built": str(year_built),
                                        "last_modified": str(last_modified),
                                        "prop_size": str(prop_size), 
                                        "zillow_url": str(z_url)
                                        } 
                                   
                if data_sale['status']['code'] == 1:
                    # Success without result
                    return render_template("address-search-results.html", sale_history=0, address_params=address_params)    
                else:
                    sale_history = utility.get_sale_history(data_sale)
                    if sale_history:
                        for key, value in sale_history.items():
                            if value == 0:
                                del sale_history[key]
                        if sale_history != {}:
                            return render_template("address-search-results.html", sale_history=sale_history,    address_params=address_params)
                        else:
                            return render_template("address-search-results.html",sale_history=0, address_params=address_params)
    except IndexError:  
        return render_template("no-result.html")
    else:
        params_key = ['zipcode', 'city', 'property_type', 'max_no_bed', 'min_no_bed', 'max_no_bath', 'min_no_bath', 'price_from', 'price_to', 'trans_date_from', 'trans_date_to']
        sale_url = "sale/snapshot?pageSize=200000&"
        search_params = {}
        for search_param in params_key:
            value = request.args.get(search_param)
            if search_param == 'city':
                if value:
                    value = value.split(', ')[0]
            if value != None and value != "":
                search_params[search_param] = value      
        sales_data = utility.get_result_from_api(ONBOARD_URL, sale_url, headers, search_params)       
        # pprint.pprint(sales_data)
        property_sales = utility.get_area_sale_list(sales_data)
        sales_info = utility.get_pro_sale_info(sales_data)

        if property_sales:
            no_results = len(property_sales)
            property_sales = np.array(property_sales)
            if no_results >0:
                median_price = np.median(property_sales, axis=0)
                percent_25_price = np.percentile(property_sales, 25, axis=0)
                percent_75_price = np.percentile(property_sales, 75, axis=0)
                area = sales_data['property'][0]['address']['line2']

                random_ten_sale_info = []
                if sales_info:
                    random.shuffle(sales_info)
                    random_twenty_sale_info = sales_info[0:20]
                    for item in random_twenty_sale_info:
                        if item[2] < 5*median_price[1]:
                            random_ten_sale_info.append(item)
                random_ten_sale_info = random_ten_sale_info[0:10]
                if search_type == 'zipcode':
                    zip_code = request.args.get(search_type)
                    trend_url = "https://search.onboard-apis.com/propertyapi/v1.0.0/salestrend/snapshot?geoid=ZI{}&interval=yearly&startyear=2000&endyear=2018".format(zip_code)
                    trend_response = requests.get(trend_url, headers=headers)
                    trend_data = trend_response.json()
                    # print pprint.pprint(trend_data)
                    area_trend = utility.get_area_sale_trend(trend_data)
                    print percent_25_price, "===================="
                    return render_template("region-search-results.html", median_price=median_price,
                                                                        no_results=no_results,
                                                                        area=area,
                                                                        percent_25_price=percent_25_price,
                                                                        percent_75_price=percent_75_price,
                                                                        trend_data=trend_data,
                                                                        area_trend=area_trend,
                                                                        search_params=search_params,
                                                                        random_ten_sale_info=random_ten_sale_info)
                #return result for city search
                return render_template("region-search-results.html", median_price=median_price,
                                                                no_results=no_results,
                                                                area=area,
                                                                percent_25_price=percent_25_price,
                                                                percent_75_price=percent_75_price,
                                                                search_params=search_params,random_ten_sale_info=random_ten_sale_info
                                                                )
        else:
            return render_template("region-search-results.html", no_results=0)
        # return redirect("/")

@app.route("/search", methods=["POST"])
def save_search():
    save_type = request.form.get('save_type')
    save_data = request.form.get('save_data')
    address_url = request.form.get('save_url')
    searches_url = request.form.get('searches_url')
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
                saved_by_user=True,
                search_url=searches_url
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
                saved_by_user=True,
                prop_url=address_url
                )
            db.session.add(_property)
            db.session.commit()


    return jsonify({'Result': save_data})
            
@app.route('/address-sales-history.json')
def address_sales_history():
    """Return data about address sales history."""

    sales_history = request.args.get('sales_data')
    sales_history = ast.literal_eval(sales_history)
    prop_map = request.args.get('propertymap')
    data = []
    labels = []
    for i, record in sales_history.items():
        #print record[0], record[1]
        labels.append(i)
        data.append(record)
    data_dict = {
        "labels": labels,
        "datasets": [
            {
                "label": "Price History",
                "fill": True,
                "lineTension": 0.5,
                "backgroundColor": "#c45850",
                "borderColor": "#c45850",
                "borderCapStyle": 'butt',
                "borderDash": [],
                "borderDashOffset": 0.0,
                "borderJoinStyle": 'miter',
                "pointBorderColor": "rgba(151,187,205,1)",
                "pointBackgroundColor": "#fff",
                "pointBorderWidth": 1,
                "pointHoverRadius": 5,
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(151,187,205,1)",
                "pointHoverBorderWidth": 2,
                "pointHitRadius": 10,
                "data": data,
                "spanGaps": False}
        ]
    }
    return jsonify(data_dict)

@app.route('/region-sales-history.json')
def region_sales_history():
    """Return data about region sales history."""

    region_sales = request.args.get('region_history_data')
    region_sales = ast.literal_eval(region_sales)

    # print region_sales
    labels = []
    data_avg = []
    data_median = []
    data_counts = []
    for key in sorted(region_sales.keys()):
        labels.append(key)
        data_avg.append(region_sales[key][0])
        data_counts.append(region_sales[key][1])
        data_median.append(region_sales[key][2])
    # print labels,data_avg, data_median, data_counts

    data_dict = {
        "labels": labels,
        "datasets": [
            {
                "type": "line",
                "label": "Average Price",
                "fill": False,
                "lineTension": 0.5,
                "backgroundColor": "rgba(151,187,205,1)",
                "borderColor": "rgba(151,187,205,1)",
                "borderCapStyle": 'butt',
                "borderDash": [],
                "borderDashOffset": 0.0,
                "borderJoinStyle": 'miter',
                "pointBorderColor": "rgba(151,187,205,1)",
                "pointBackgroundColor": "#fff",
                "pointBorderWidth": 1,
                "pointHoverRadius": 5,
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(151,187,205,1)",
                "pointHoverBorderWidth": 2,
                "pointHitRadius": 10,
                "data": data_avg,
                "spanGaps": False,
                "yAxisID": "y-axis-1"
                },
            {
                "type": "line",
                "label": "Median Price",
                "fill": False,
                "lineTension": 0.5,
                "backgroundColor": "rgb(255, 159, 64)",
                "borderColor": "rgb(255, 159, 64)",
                "borderCapStyle": 'butt',
                "borderDash": [],
                "borderDashOffset": 0.0,
                "borderJoinStyle": 'miter',
                "pointBorderColor": "rgb(255, 159, 64)",
                "pointBackgroundColor": "#fff",
                "pointBorderWidth": 1,
                "pointHoverRadius": 5,
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(220,220,220,1)",
                "pointHoverBorderWidth": 2,
                "pointRadius": 3,
                "pointHitRadius": 10,
                "data": data_median,
                "spanGaps": False,
                "yAxisID": "y-axis-1"
                },
            
            {
                "type": "bar",
                "label": "Count",
                "fill": True,
                "backgroundColor": "#c45850",
                "borderColor": "#c45850",
                "data": data_counts,
                "yAxisID": "y-axis-2"
                }
            

        ]
    }
    return jsonify(data_dict)

@app.route('/region-prop-info.json')
def region_prop_info():
    """Return data about region property information, including sales trans date and amount, longitude and latitude."""
    region_sales = request.args.get('rand_sales_info')
    rand_prop_info = ast.literal_eval(region_sales)
    rand_prop_info.sort(key=lambda x: x[1])
    date = []
    amount = []
    for item in rand_prop_info:
        date.append(item[1])
        amount.append(item[2])
    data_dict = {
        "labels": date,
        "datasets": [
            {
                "type": "line",
                "label": "Average Price",
                "fill": False,
                "lineTension": 0.5,
                "backgroundColor": "rgba(151,187,205,1)",
                "borderColor": "rgba(151,187,205,1)",
                "borderCapStyle": 'butt',
                "borderDash": [],
                "borderDashOffset": 0.0,
                "borderJoinStyle": 'miter',
                "pointBorderColor": "rgba(151,187,205,1)",
                "pointBackgroundColor": "#fff",
                "pointBorderWidth": 1,
                "pointHoverRadius": 5,
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(151,187,205,1)",
                "pointHoverBorderWidth": 2,
                "pointHitRadius": 10,
                "data": amount,
                "spanGaps": False
                }
            ]
        }
    return jsonify(data_dict)
if __name__ == "__main__":

    connect_to_db(app)
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    # DebugToolbarExtension(app)
    app.run(host = '0.0.0.0')