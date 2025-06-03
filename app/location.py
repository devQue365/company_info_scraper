import http.client
import json
import urllib.parse
# 'Google Place Autocomplete and Place Info - 1000 requests / MO
def gplace(company_name, location):
    conn = http.client.HTTPSConnection("google-place-autocomplete-and-place-info.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "7ee1c65373msh181b4a01f21d239p1e5ff7jsnc2f07e071e6d",
        'x-rapidapi-host': "google-place-autocomplete-and-place-info.p.rapidapi.com"
    }
    query_params = {
        'input': f'{company_name} offices in {location}'
    }
    # get the url-safe-query
    url_safe_query = urllib.parse.urlencode(query_params)
    # request connection to the auto-complete endpoint
    conn.request("GET", f"/maps/api/place/autocomplete/json?{url_safe_query}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    output_dict = json.loads(data)
    def summarize():
        nonlocal output_dict
        # initialize container
        container = []
        predictions = output_dict.get('predictions')
        for p in predictions:
            description = p.get('description','')
            place_id = p.get('place_id', '')
            name = p.get('structured_formatting', {}).get('main_text', '')
            address = p.get('structured_formatting', {}).get('secondary_text', '')
            types = p.get('types', [])
            job_info = {
                'place_id': place_id,
                'name': name,
                'address': address,
                'description': description,
                'types': types,
            }
            container.append(job_info)
        return container
    return summarize()

# Google map places (v2) - 100 requests / day
def gmapv2(company_name, location):
    conn = http.client.HTTPSConnection("google-map-places-new-v2.p.rapidapi.com")
    payload = "{\"input\":\"" + company_name + "offices in" + location + "\",\"locationBias\":{\"circle\":{\"center\":{\"latitude\":40,\"longitude\":-110},\"radius\":10000}},\"includedPrimaryTypes\":[],\"includedRegionCodes\":[],\"languageCode\":\"\",\"regionCode\":\"\",\"origin\":{\"latitude\":0,\"longitude\":0},\"inputOffset\":0,\"includeQueryPredictions\":true,\"sessionToken\":\"\"}"
    headers = {
        'x-rapidapi-key': "7ee1c65373msh181b4a01f21d239p1e5ff7jsnc2f07e071e6d",
        'x-rapidapi-host': "google-map-places-new-v2.p.rapidapi.com",
        'Content-Type': "application/json",
        'X-Goog-FieldMask': "*"
    }
    # request connection to the autocomplete endpoint
    conn.request("POST", "/v1/places:autocomplete", payload, headers)
    res = conn.getresponse()
    data = res.read()
    output_dict = json.loads(data)
    def summarize():
        nonlocal output_dict
        # container to hold data
        container = []
        suggestions = output_dict.get('suggestions')
        for s in suggestions:
            place_predictions = s.get('placePrediction', {})
            text = place_predictions.get('text', {})
            # get place_id
            place_id = place_predictions.get('placeId', '')
            # description
            description = text.get('text', '')
            # name
            name = place_predictions.get('structuredFormat', {}).get('mainText', {}).get('text')
            # address
            address = place_predictions.get('structuredFormat', {}).get('secondaryText', {}).get('text')
            # types
            types = place_predictions.get('types', '')
            # get job_info
            job_info = {
                'place_id': place_id,
                'name': name,
                'address': address,
                'description': description,
                'types': types,
            }
            container.append(job_info)
        return container
    return summarize()