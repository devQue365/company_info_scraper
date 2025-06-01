import http.client
import json
# 100 requests / day
def gmapv2(company_name, location):
    conn = http.client.HTTPSConnection("google-map-places-new-v2.p.rapidapi.com")
    payload = "{\"input\":\"" + company_name + "office in" + location + "\",\"locationBias\":{\"circle\":{\"center\":{\"latitude\":40,\"longitude\":-110},\"radius\":10000}},\"includedPrimaryTypes\":[],\"includedRegionCodes\":[],\"languageCode\":\"\",\"regionCode\":\"\",\"origin\":{\"latitude\":0,\"longitude\":0},\"inputOffset\":0,\"includeQueryPredictions\":true,\"sessionToken\":\"\"}"

    headers = {
        'x-rapidapi-key': "7ee1c65373msh181b4a01f21d239p1e5ff7jsnc2f07e071e6d",
        'x-rapidapi-host': "google-map-places-new-v2.p.rapidapi.com",
        'Content-Type': "application/json",
        'X-Goog-FieldMask': "*"
    }

    conn.request("POST", "/v1/places:autocomplete", payload, headers)

    res = conn.getresponse()
    data = res.read()
    output_dict = json.loads(data)
    def summarizedResults():
        nonlocal output_dict
        suggestions = output_dict.get('suggestions', [])
        formatted = {}

        for idx, item in enumerate(suggestions, start=1):
            prediction = item.get('placePrediction', {})
            place_id = prediction.get('placeId')
            name = prediction.get('structuredFormat', {}).get('mainText', {}).get('text')
            address = prediction.get('structuredFormat', {}).get('secondaryText', {}).get('text')
            distance = prediction.get('distanceMeters')
            types = prediction.get('types', [])

            formatted[f'office_{idx}'] = {
                'name': name,
                'address': address,
                'place_id': place_id,
                'distance_meters': distance,
                'types': types
            }

        return formatted
    return summarizedResults()