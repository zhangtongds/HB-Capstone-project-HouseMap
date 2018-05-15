import requests


def get_property_id(data):
    """Get propperty id from property API response."""
    
    return data['property'][0]['identifier']['obPropId']

def get_ten_digits_zipcode(data):
    """Get ten digits zipcode from property API response. """
    
    return data['property'][0]['address']['postal1'] + "-" + data['property'][0]['address']['postal2']

def get_five_digits_zipcode(data):
    """Get five digits zipcode from property API response."""

    return data['property'][0]['address']['postal1']

def get_sale_history(data):
    """Get a list of sales date and amount tuples from sales API response"""
    
    sale_history = [] # creat a list of sales history to pass to the front end.
    for sale in data['property'][0]['salehistory']:
        sale_history.append((sale['amount']['salerecdate'], sale['amount']['saleamt']))
    return sale_history

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
    """Getting property id and sale amount history from a property."""
    
    property_sales = []   
    for item in data['property']:
        lst_0 = item['identifier']['obPropId']
        lst_1 = item['sale']['amount']['saleamt']
        if lst_1 != 0:
            property_sales.append([lst_0,lst_1])
    return property_sales

def get_area_sale_trend(data):
    """Getting sales trend for a zipcode."""
    
    area_trend = []
    for item in data['salestrends']:
        year = item['daterange']['end']
        avg_price = item['SalesTrend']['avgsaleprice']
        home_count = item['SalesTrend']['homesalecount']
        med_price = item['SalesTrend']['medsaleprice']
        area_trend.append([year, avg_price, home_count, med_price])

    return area_trend


