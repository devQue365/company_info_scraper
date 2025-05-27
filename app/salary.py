import http.client
import urllib.parse
from pprint import pprint
import json

def jsearch(company, job_title, location):
    conn = http.client.HTTPSConnection("jsearch.p.rapidapi.com")
    url = "jsearch.p.rapidapi.com"
    headers = {
    'x-rapidapi-key': "7ee1c65373msh181b4a01f21d239p1e5ff7jsnc2f07e071e6d",
    'x-rapidapi-host': "jsearch.p.rapidapi.com"
    }
    params = {
    'company': company,
    'job_title': job_title,
    'location' : location,
    'location_type': 'ANY',
    'years_of_experience': 'ALL',
    }
    url_safe_query = urllib.parse.urlencode(params)
    conn.request("GET", f"/company-job-salary?{url_safe_query}", headers=headers)
    res = conn.getresponse()
    data = res.read() # -> type() : str
    # get the result in dictionary form 
    res = json.loads(data)
    salary_data = res['data'][0]
    return {
        "company": salary_data["company"],
        "job_title": salary_data["job_title"],
        "location": salary_data["location"],
        "salary_range": f"{salary_data['salary_currency']} {int(salary_data['min_salary']):,} - {int(salary_data['max_salary']):,} per {salary_data['salary_period'].lower()}",
        "median_salary": f"{salary_data['salary_currency']} {int(salary_data['median_salary']):,}",
        "salary_count": salary_data["salary_count"],
        "confidence": salary_data["confidence"]
    }

