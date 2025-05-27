import http.client
import urllib.parse
from pprint import pprint
import json

# JSearch - 200 requests / MO
def jsearch(company, job_title, location, API_KEY=None):
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

# GlassDoor API - 200 requests / MO
def glassDoor(company, job_title, location, API_KEY=None):
    conn = http.client.HTTPSConnection("glassdoor-real-time.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "7ee1c65373msh181b4a01f21d239p1e5ff7jsnc2f07e071e6d",
        'x-rapidapi-host': "glassdoor-real-time.p.rapidapi.com"
    }
    # first extract locationId
    params = {
        'query' : location
    }
    url_safe_query = urllib.parse.urlencode(params)
    conn.request("GET", f"/jobs/location?{url_safe_query}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    res = json.loads(data)
    locationId = res['data'][0]['locationId'] # we got the location ID
    # Now extract salary data
    params = {
        'query' : f'{company} {job_title}',
        'locationId': locationId,
        'limit': 10,
        'page': 1,
        'sort' : 'POPULAR'
    }
    url_safe_query = urllib.parse.urlencode(params)
    conn.request("GET", f"/salaries/search?{url_safe_query}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    res = json.loads(data)
    # for glassDoor API we will be transforming the result into more structured form
    def extract_salary_data(data: dict, company: str, location: str):
        results = data.get('data', {}).get('aggregateSalaryResponse', {}).get('results', [])
        company_rating = data.get('data', {}).get('employer', {}).get('overallRating', None)

        entries = []

        def fmt(salary):
            return f"USD {int(round(salary)):,}" if salary else "N/A"

        for job in results:
            job_title = job.get('jobTitle', {}).get('text', '')

            percentiles = job.get('totalPayStatistics', {}).get('percentiles', [])
            mean_salary = job.get('totalPayStatistics', {}).get('mean', None)

            perc_25 = next((p['value'] for p in percentiles if p.get('ident') == 'perc_25'), None)
            perc_50 = next((p['value'] for p in percentiles if p.get('ident') == 'perc_50'), None)
            perc_75 = next((p['value'] for p in percentiles if p.get('ident') == 'perc_75'), None)

            entry = {
                'company': company,
                'job_title': job_title,
                'location': location,
                'salary_currency': 'USD',
                'salary_period': 'annual',
                'salary_range': f"{fmt(perc_25)} - {fmt(perc_75)}" if perc_25 and perc_75 else "N/A",
                'median_salary': fmt(perc_50),
                'mean_salary': fmt(mean_salary),
                'company_rating': round(company_rating, 1) if company_rating else "N/A"
            }

            entries.append(entry)

        return entries

    
    salary_data = extract_salary_data(res, company, location)
    return salary_data

# Job_Salary_Data_API - 50 requests / MO
def job_salary_data_api(company, job_title, location, API_KEY=None):
    conn = http.client.HTTPSConnection("job-salary-data.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "7ee1c65373msh181b4a01f21d239p1e5ff7jsnc2f07e071e6d",
        'x-rapidapi-host': "job-salary-data.p.rapidapi.com"
    }
    params = {
        'company': company,
        'job_title': job_title,
        'location': location,
        'location_type': 'ANY',
        'years_of_experience': 'ALL'
    }
    url_safe_query = urllib.parse.urlencode(params)
    conn.request("GET", f"/company-job-salary?{url_safe_query}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    res = json.loads(data)
    salary_data = res['data'][0]
    return {
        'company': salary_data['company'],
        'job_title': salary_data['job_title'],
        'location': salary_data['location'],
        'salary_currency': salary_data['salary_currency'],
        'salary_period': salary_data['salary_period'],
        'salary_range' : f'{salary_data['salary_currency']} {salary_data['min_salary']} - {salary_data['salary_currency']} {salary_data['max_salary']}',
        'median_salary': f'{salary_data['salary_currency']} {salary_data['median_salary']}',
        'mean_salary': f'{salary_data['salary_currency']} {round(salary_data['result']['totalPayStatistics']['mean'])}',
        'company_rating': salary_data['result']['employer']['ratings']['overallRating']
        # 'confidence': salary_data['confidence'],
        # 'min_salary': salary_data['min_salary'],
        # 'max_salary': salary_data['max_salary'],
        # 'salary_count': salary_data['salary_count'],
    }