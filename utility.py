import requests


def get_property_id(data):
    """Get propperty id from property API response."""
    
    return data['property'][0]['identifier']['obPropId']

def get_ten_digits_zipcode(data):
    """Get ten digits zipcode from property API response. """ 
    
    return data['property'][0]['address']['postal1'] + "-" + data['property'][0]['address']['postal2']

def get_sale_history(data):
    """Get a list of sales date and amount tuples from sales API response"""
    
    sale_history = [] # creat a list of sales history to pass to the front end.
    for sale in data['property'][0]['salehistory']:
        sale_history.append((sale['amount']['salerecdate'], sale['amount']['saleamt']))
    return sale_history

def get_result_from_api(URL, endpoint, headers, search_params):
    """Get the json response from api."""

    params_name_map = { "property_type": "propertyType",
                            "max_no_bed": "maxBeds",
                            "min_no_bed": "minBeds",
                            "max_no_bath": "maxBathsTotal",
                            "min_no_bath": "minBathsTotal",
                            "price_from": "minAssdTtlValue",
                            "price_to": "maxAssdTtlValue",
                            "trans_date_from": "startSaleTransDate",
                            "trans_date_to": "endSaleTransDate"}


    url_params = []
    for key, value in search_params.items():
        url_param = params_name_map.setdefault(key, key)
        url_params.append("{}={}".format(key, value))

    request_url = URL + endpoint + '&'.join(url_params)
    data = requests.get(request_url, headers=headers).json() 

    return data
        




