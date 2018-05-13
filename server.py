import pprint
import os
from jinja2 import StrictUndefined
import requests
# import httplib
from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension
from model import User, Favorite, Search, Property, Sale, connect_to_db, db
# from seed import parse_address_from_homepage
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
    search_type = request.args.get('search_type')
    if search_type is None:
        search_type = 'postalcode'
    session['search_type'] = search_type
    field_map = {
        'postalcode': ['postalcode'],
        'address': ['address', 'city', 'state'],
        'cityName': ['cityName']
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
    print search_type
    if search_type == 'address':
        address = request.args.get("address")
        city = request.args.get("city")
        state = request.args.get("state")

        address1 = address.replace(" ", "%20")
        address2 = city + "%2C%20" + state
        request_url_prop = "/propertyapi/v1.0.0/property/detail?address1=" + address1 + "&address2=" + address2
        request_url_sale = "/propertyapi/v1.0.0/saleshistory/detail?address1="+ address1 + "&address2=" + address2
        response_prop = requests.get(ONBOARD_URL + request_url_prop, headers=headers)
        response_sale = requests.get(ONBOARD_URL + request_url_sale, headers=headers) 
        data_prop = response_prop.json()
        data_sale = response_sale.json()

        property_id = data_prop['property'][0]['identifier']['obPropId']
        zipcode = data_prop['property'][0]['address']['postal1'] + "-" + data_prop['property'][0]['address']['postal2']
        sale_history = [] # creat a list of sales history to pass to the front end.
        for sale in data_sale['property'][0]['salehistory']:
            sale_history.append((sale['amount']['salerecdate'], sale['amount']['saleamt']))
        session['search_prop'] = data_prop
        session['search_sale'] = data_sale

        return render_template("address-search-results.html", property_id=property_id, address=address, city=city, state=state, zipcode=zipcode, sale_history=sale_history)

    
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

        search_params_key = [search_type, 'property_type', 'max_no_bed','min_no_bed', 'max_no_bath', 'min_no_bath', 'price_from', 'price_to', 'trans_date_from', 'trans_date_to']
       
        url = "https://search.onboard-apis.com/propertyapi/v1.0.0/sale/snapshot?pageSize=200000&"
        url_params = []
        for search_param in search_params_key:
            value = request.args.get(search_param)
            if search_param == 'cityName':
                value = value.replace(" ", "%20")
            if value != None and value != "":
                url_params.append("{}={}".format(params_name_map.setdefault(search_param, search_param), value))
        request_url = url + '&'.join(url_params)


        print request_url
        print "=========="
        response = requests.get(request_url, headers=headers)
    
        data = response.json()
        # print pprint.pprint(data)
        property_sales = {}
    
        for item in data['property']:
            key = item['identifier']['obPropId']
            value = item['sale']['amount']['saleamt']
            property_sales[key] = value
        no_results = len(property_sales.values())
        print no_results
        if no_results >0:
            sum_price = 0.0
            no_units = 0
            max_price = [0,0]
            min_price = [0,float("inf")]
            area = None
            # print property_sales
            for key, value in property_sales.items():
                if value > max_price[1]:
                    max_price[1] = value
                    max_price[0] = key
                if value < min_price[1] and value != 0:
                    min_price[1] = value
                    min_price[0] = key
                    area = data['property'][0]['address']['line2']
                if value != 0:
                    sum_price += float(value)
                    no_units += 1

            avg_price = int(sum_price/no_units)

            return render_template("other-search-results.html", area=area, avg_price=avg_price, max_price=max_price, min_price=min_price, no_results=no_results)
        else:
            return render_template("other-search-results.html", no_results=0)

        if session.get('user_id'):
            search = Search(user_id=session['user_id'], address=address, city=city, state=state, no_of_room=no_of_room, no_of_bath=no_of_bath, price_from=price_from, price_to=price_to, trans_date_from=trans_date_from, trans_date_to=trans_date_to)
            db.session.add(search)
            db.session.commit()


@app.route("/search", methods=["POST"])
def save_search():
    print request.form.get('save_type')
    saved_property = True
    print saved_property
    print "$$$$$$$$$$$"
    return jsonify({'Result': saved_property})
            
        

    # return redirect("/")


if __name__ == "__main__":

    connect_to_db(app)
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(app)
    app.run(host = '0.0.0.0')