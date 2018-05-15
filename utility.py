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