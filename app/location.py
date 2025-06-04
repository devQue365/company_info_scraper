import http.client
import json
import urllib.parse

# Threshold : 100 requests / Day (rich results)
def gm__1(company, location):
    try:
        conn = http.client.HTTPSConnection("google-map-places.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': "7ee1c65373msh181b4a01f21d239p1e5ff7jsnc2f07e071e6d",
            'x-rapidapi-host': "google-map-places.p.rapidapi.com"
        }
        query_params = {
            'query': f'{company},{location}',
            'radius': 50000, # (50,000 m -> 50 km)
            'language': 'en',
            'type': 'establishment|point_of_interest',

        }
        # get url safe query
        url_safe_query = urllib.parse.urlencode(query_params)
        conn.request("GET", f"/maps/api/place/textsearch/json?{url_safe_query}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        output_dict = json.loads(data)
        results = output_dict.get('results')
        # initialize a container to hold results
        container = []
        for result in results:
            # get the types
            types = result.get('types',[])
            # perform filtering
            if any(['electronics_store' in types, 'store' in types]):
                continue
            else:
                # get geometry key
                geometry = result.get('geometry', {}) # return a dictionary
                # get latitude and longitude values -> location field
                location = geometry.get('location', {}) # return a dictionary
                location_info = {
                    # get business_status, place_id, plus_code, gloval_code
                    'business_status': result.get('business_status', ''),
                    'place_id': result.get('place_id', ''),
                    'plus_code': result.get('plus_code', {}).get('compound_code', ''),
                    'global_code': result.get('plus_code', {}).get('global_code', ''),
                    # get name and address
                    'name': result.get('name', ''),
                    'address': result.get('formatted_address', ''),
                    # get latitude and longitude, viewport (northeast and southwest)
                    'location': location,
                    'northeast': geometry.get('viewport', {}).get('northeast', {}),
                    'southwest': geometry.get('viewport', {}).get('southwest', {}),
                    # get open_now & types
                    'open_now': result.get('opening_hours', {}).get('open_now', None),
                    'rating': result.get('rating', ''),
                    'user_ratings_total': result.get('user_ratings_total', ''),
                    'type': types
                }
                container.append(location_info)
        return container
    except Exception as e:
        return {'error': str(e)}

# Threshold - 1000 requests / MO 
def gm__2(company, location):
    conn = http.client.HTTPSConnection("google-map-scraper1.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "7ee1c65373msh181b4a01f21d239p1e5ff7jsnc2f07e071e6d",
        'x-rapidapi-host': "google-map-scraper1.p.rapidapi.com"
    }
    query_params = {
        'query': f'{company}, {location}'
    }
    # get url_safe_query
    url_safe_query = urllib.parse.urlencode(query_params)
    conn.request("GET", f"/api/autocomplete/search?{url_safe_query}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    output_dict = json.loads(data)
    # go to the data section
    data = output_dict.get('data', {})
    # go to the results section
    results = data.get('results', {}) # we get a list here
    def summarize():
        nonlocal results
        # initialize a container to hold results
        container = []
        # traverse each result and extract the required fields
        for r in results:
            # get id
            place_id = r.get('id', '')
            address = r.get('title', '').lower()
            if((company + ' ').lower() not in address):
                continue
            latitude = r.get('latitude', '')
            longitude = r.get('longitude', '')
            country_code = r.get('country_code')
            is_place = r.get('is_place')
            location_info = {
                'place_id': place_id,
                'address': address,
                'latitude': latitude,
                'longitude': longitude,
                'country_code': country_code,
                'is_place': is_place
            }
            container.append(location_info)
        return container
    return summarize()

# Threshold - 1000 requests / MO -> may/may not give all results [uses autocomplete predictions but will give relevant ones only]
def gm__backup(company, location):
    conn = http.client.HTTPSConnection("google-place-autocomplete-and-place-info.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': 
        "7ee1c65373msh181b4a01f21d239p1e5ff7jsnc2f07e071e6d",
        'x-rapidapi-host': "google-place-autocomplete-and-place-info.p.rapidapi.com"
    }
    query_params = {
        'input': f'{company},{location}'
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
        nonlocal query_params
        # initialize container
        container = []
        predictions = output_dict.get('predictions')
        for p in predictions:
            types = p.get('types', [])
            name = p.get('structured_formatting', {}).get('main_text', '').lower()
            # filter out the results based on types and presence of required keyword
            allowed_types = ['establishment', 'point_of_interest', 'premise', 'subpremise']
            if(any(t not in allowed_types for t in types) or (company.lower() not in name)):
                continue     
            description = p.get('description','').lower()
            place_id = p.get('place_id', '')
            address = p.get('structured_formatting', {}).get('secondary_text', '').lower()
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



