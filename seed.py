"Functions to parse data."

def parse_address_from_result(address, address2):

    address = address1 + " " + address2.replace(",", "")

    return address[:-6].replace(" ", "%20")

def parse_address_from_homepage(address, city, state):

    address = address + " " + city + " " + state

    return address.replace(" ", "%20")
