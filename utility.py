import requests


def get_property_id(data):
    """Get propperty id from property detail API response."""
    
    try:
        return data['property'][0]['identifier']['obPropId']
    except KeyError:
        return None

def get_ten_digits_zipcode(data):
    """Get ten digits zipcode from property detail API response. """
    try:
        return data['property'][0]['address']['postal1'] + "-" + data['property'][0]['address']['postal2']
    except KeyError:
        return None

def get_five_digits_zipcode(data):
    """Get five digits zipcode from property detail API response."""
    try:
        return data['property'][0]['address']['postal1']
    except KeyError:
        return None

def get_sale_history(data):
    """Get a list of sales date and amount tuples from sales API response"""
    
    sale_history = {} # creat a list of sales history to pass to the front end.
    try:
        for sale in data['property'][0]['salehistory']:
            sale_history[sale['amount']['salerecdate']] = sale['amount']['saleamt']
        return sale_history
    except KeyError:
        return None

def get_result_from_api(URL, endpoint, headers, search_params):
    """Get the json response from api."""

    params_name_map = {     "geo_id" : "geoid",
                            "zipcode": "postalcode",
                            "city": "cityName",
                            # something for state here
                            "property_type": "propertyType",
                            "max_no_bed": "maxBeds",
                            "min_no_bed": "minBeds",
                            "max_no_bath": "maxBathsTotal",
                            "min_no_bath": "minBathsTotal",
                            "price_from": "minAssdTtlValue",
                            "price_to": "maxAssdTtlValue",
                            "trans_date_from": "startSaleTransDate",
                            "trans_date_to": "endSaleTransDate"}


    url_params = []
    # print search_params
    for key, value in search_params.items():
        url_param = params_name_map.setdefault(key, key)
        url_params.append("{}={}".format(url_param, value))
    # print url_params
    request_url = URL + endpoint + '&'.join(url_params)
    # print request_url
    data = requests.get(request_url, headers=headers).json() 

    return data
        
def get_area_sale_list(data):
    """Getting property id and sale amount history from property detail API call."""
    
    property_sales = []   
    try:
        for item in data['property']:
            lst_0 = item['identifier']['obPropId']
            lst_1 = item['sale']['amount']['saleamt']
            if lst_1 != 0:
                property_sales.append([lst_0,lst_1])
        return property_sales
    except KeyError:
        return None

def get_area_sale_trend(data):
    """Getting sales trend for a zipcode from sales trend API call."""
    
    area_trend = {}
    try:
        for item in data['salestrends']:
            year = item['daterange']['end']
            avg_price = item['SalesTrend']['avgsaleprice']
            home_count = item['SalesTrend']['homesalecount']
            med_price = item['SalesTrend']['medsaleprice']
            
            area_trend[year] = [avg_price, home_count, med_price]
        return area_trend
    except KeyError:
        return None

def get_full_address_from_result(data):
    """Get full result including address, city, state, zipcode from property detail API call."""
    try:
        return data['property'][0]['address']['line1'] + ", " + data['property'][0]['address']['line2']
    except KeyError:
        return None

def get_latitude_from_result(data):
    """Get latitude from property detail API call."""
    try:
        return data['property'][0]['location']['latitude']
    except KeyError:
        return None

def get_longitude_from_result(data):
    """Get longitude from property detail API call."""
    try:
        return data['property'][0]['location']['longitude']
    except KeyError:
        return None

def get_no_beds_from_result(data):
    """Get number of beds from property detail API call."""
    try:
        return data['property'][0]['building']['rooms']['beds']
    except KeyError:
        return None

def get_no_baths_from_result(data):
    """Get number of baths from property detail API call."""

    try:
        return data['property'][0]['building']['rooms']['bathstotal']
    except KeyError:
        return None

def get_county(data):
    """Get the county name from property detail API call."""

    try:
        return data['property'][0]['area']['countrysecsubd']
    except KeyError:
        return None

def get_wall_type(data):
    """Get the wall type of building from property detail API call."""

    try:
        return data['property'][0]['building']['construction']['wallType']
    except KeyError:
        return None

def get_bdlg_type(data):
    """Get the building type of building from property detail API call."""

    try:
        return data['property'][0]['building']['summary']['bldgType']
    except KeyError:
        return None

def get_lot_size(data):
    """Get the lot size from property detail API call."""

    try:
        return str(data['property'][0]['lot']['lotsize2']) + " SQFT"
    except KeyError:
        return None

def get_year_built(data):
    """Get the built year from property detail API call."""

    try:
        return data['property'][0]['summary']['yearbuilt']
    except KeyError:
        return None

def get_last_modified(data):
    """Get the last modified date from property detail API call."""

    try:
        return data['property'][0]['vintage']['lastModified']
    except KeyError:
        return None

def get_prop_size(data):
    """Get the proprerty size from property detail API call."""

    try:
        return str(data['property'][0]['building']['size']['livingsize']) + " SQFT"
    except KeyError:
        return None
