import http.client
import requests
import urllib.parse
from app.Parser import customizedParser
import json
''' 
Display real-time job listings 
start from best ones - glassdoor | indeed
'''
# GlassDoor API - 200 requests / MO 
# [makes 2 X requests / API Call] -> 100 requests in total (practical threshold)
def glassDoor__v1(company, job_title, location):
    try:
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
        if "data" not in res or not res["data"]:
            return {"error": "No job data found"}
        # for glassDoor API we will be transforming the result into more structured form
        def extract_salary(output_dict):
            results = output_dict['data']['aggregateSalaryResponse']['results']
            company_name = next((result['employer']['name'] for result in results),None)
            location = output_dict.get('data',{}).get('aggregateSalaryResponse',{}).get('queryLocation',{}).get('name',{})
            # Initialize results container
            container = []
            # we will traverse through all job entries
            for job in results:
                pay_period = job['payPeriod']
                # we will only process annual salaries
                if pay_period == 'ANNUAL':
                    job_title = job['jobTitle']['text']
                    currency = job['currency']['code']
                    base_mean = job['basePayStatistics']['mean']
                    total_additional_mean = job['totalAdditionalPayStatistics']['mean']
                    percentiles = {p['ident']: p['value'] for p in job['totalPayStatistics']['percentiles']}
                    
                    # salary summary
                    container.append({
                        # basic information
                        'job_title': job_title,
                        'company_name': company_name,
                        'location': location,
                        # base salary ranges
                        'min_base_salary': round(base_mean * 0.81, 2),  # estimated ~19% below mean
                        'median_base_salary': round(base_mean, 2),
                        'max_base_salary': round(base_mean * 1.23, 2),  # estimated ~23% above mean
                        # additional-pay range
                        'mean_additional_pay': round(total_additional_mean, 2),
                        # general salary ranges
                        'min_salary': round(percentiles.get('P25', 0), 2),
                        'median_salary': round(percentiles.get('P50', 0), 2),
                        'max_salary': round(percentiles.get('P75', 0), 2),
                        'salary_range': f"{currency} {round(percentiles.get('P25', 0), 2)} - {currency} {round(percentiles.get('P75', 0), 2)}",
                        'salary_currency': currency,
                        'salary_period': 'YEAR',
                        'provider': 'glassdoor__v1',
                        'type': 'postings',
                    })
            return container
        return extract_salary(res)
    except Exception as e:
        return {"error": str(e)} #"Job data not available ..."}
# [makes 2 X requests / API Call] -> 100 requests in total (practical threshold)
def glassDoor__v2(company, job_title, location):
    try:
        conn = http.client.HTTPSConnection("real-time-glassdoor-data.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': "7ee1c65373msh181b4a01f21d239p1e5ff7jsnc2f07e071e6d",
            'x-rapidapi-host': "real-time-glassdoor-data.p.rapidapi.com"
        }
        # first get the company ID --> [1st API call]
        query_params = {
            'query': company,
            'limit': 1,
            'domain': 'www.glassdoor.com'
        }
        url_safe_query = urllib.parse.urlencode(query_params)
        # make a request to get company_id
        conn.request("GET", f"/company-search?{url_safe_query}", headers=headers)
        res = conn.getresponse()
        data = res.read() # byte-string
        output_dict = json.loads(data) # dict-format
        # go to the data section
        data = output_dict.get('data',{})
        company_id = data[0].get('company_id',None)

        # Now start for salary-info search ---> [2nd API Call]
        query_params = {
            'company_id': company_id,
            'job_title': job_title,
            'location': location,
            'location_type' : 'ANY',
            'years_of_experience' : 'ALL',
            'domain': 'www.glassdoor.com'
        }
        url_safe_query = urllib.parse.urlencode(query_params)
        # request to get salary data
        conn.request("GET", f"/company-salaries?{url_safe_query}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        output_dict = json.loads(data) # dict-format

        # convert it into structured format
        def getStructuredFormat():
            nonlocal output_dict
            # get the parameters section
            parameters = output_dict.get('parameters',{})
            # get the data section
            data = output_dict.get('data',{})
            # get the required fields
            currency = data.get('salary_currency', '')
            min_sal = data.get('min_salary', 0.0)
            max_sal = data.get('max_salary', 0.0)

            format = {
                # basic information
                'job_title': parameters.get('job_title', None),
                'company_name': data.get('company_name', None),
                'location': parameters.get('location', None),
                # base-salary range
                'min_base_salary': data.get('min_base_salary', 0.0),
                'median_base_salary': data.get('median_base_salary', 0.0),
                'max_base_salary': data.get('max_base_salary', 0.0),
                # additional-pay range
                'min_additional_pay': data.get('min_additional_pay', 0.0),
                # median-additional-pay = mean-salary
                'median_additional_pay': data.get('median_additional_pay', 0.0),
                'max_additional_pay': data.get('max_additional_pay', 0.0),
                # general-salary range
                'min_salary': min_sal,
                'median_salary': data.get('median_salary', 0.0),
                'max_salary': max_sal,
                # other information
                'salary_range': f'{currency} {min_sal} - {currency} {max_sal}',
                'salary_count': data.get('salary_count', None),
                'salary_currency': currency,
                'salary_period': data.get('salary_period', None),
                'provider': 'glassDoor__v2',
                'type': 'estimate',
            }
            return format
        return getStructuredFormat()
    except Exception as e:
        return {"error": str(e)}# "Job data not available ..."}

# JSearch - 200 requests / MO
def jsearch(company, job_title, location):
    try:
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
        if "data" not in res or not res["data"]:
            return {"error": "Job data not available ..."}
        salary_data = res['data'][0]
        return {
            # basic information
            'job_title': salary_data.get("job_title", None),
            'company_name': salary_data.get("company", None),
            'location': salary_data.get("location", None),
            # base salary range
            'min_base_salary': salary_data.get('min_base_salary', 0.0),
            'median_base_salary': salary_data.get('median_base_salary', 0.0),
            'max_base_salary': salary_data.get('max_base_salary', 0.0),
            # additional-pay range
            'min_additional_pay': salary_data.get('min_additional_pay', 0.0),
            'median_additional_pay': salary_data.get('median_additional_pay', 0.0),
            'max_additional_pay': salary_data.get('max_additional_pay', None),
            # general salary range
            'min_salary': salary_data.get('min_salary', 0.0),
            'median_salary': salary_data.get('median_salary', 0.0),
            'max_salary': salary_data.get('max_salary', 0.0),
            'salary_range': f"{salary_data['salary_currency']} {salary_data['min_salary']:,} - {salary_data['salary_currency']} {salary_data['max_salary']:,}",
            'salary_count': salary_data.get('salary_count', None),
            'salary_currency': salary_data["salary_currency"],
            'salary_period': salary_data['salary_period'],
            'provider': 'jsearch',
            'type': 'estimate',
        }
    except Exception as e:
        return {"error": str(e)} # "Job data not available ..."}

# Job_Salary_Data_API - 50 requests / MO
def job_salary_data_api(company, job_title, location, API_KEY=None):
    try:
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
        item = res['data'][0]
        return {
            # basic information
            'job_title': item['job_title'],
            'company_name': item['company'],
            'location': item['location'],
            # base-salary range
            'min_base_salary': item['min_base_salary'],
            'median_base_salary': item['median_base_salary'],
            'max_base_salary': item['max_base_salary'],
            # additional-pay range
            'min_additional_pay': item['min_additional_pay'],
            'median_additional_pay': item['median_additional_pay'],
            'max_additional_pay': item['max_additional_pay'],
            # general-salary range
            'min_salary': item['min_salary'],
            'median_salary': item['median_salary'],
            'max_salary': item['max_salary'],
            # other information
            'salary_range': f'{item.get('salary_currency', '')} {item.get('min_salary', 0.0)} - {item.get('salary_currency','')} {item.get('max_salary', 0.0)}',
            'salary_count': item['salary_count'],
            'salary_currency': item['salary_currency'],
            'salary_period': item['salary_period'],
            'provider': 'job_salary_data',
            'type': 'estimate',
    }
    except Exception as e:
        return {"error": "Job data not available ..."}

# CareerJet API - 1000 requests / hour -> type : postings
# CareerJet API - 1000 requests / hour -> type : postings
def career_jet_api(company, job_title, location):
    try:
        url = "http://public.api.careerjet.net/search"
        params = {
            "locale_code": "en_US",
            "keywords": f"{company} {job_title}",
            "location": location,
            "affid": "09a7e99d93482b93310a29944476cd33",  
            "user_ip": "1.2.3.4",        
            "user_agent": "Mozilla/5.0", 
            "pagesize": 10,              
            "page": 1
        }
        response = requests.get(url, params=params)
        data = response.json()
        # if there are no jobs based on the request made
        if "jobs" not in data or not data["jobs"]:
            return {"error": "Job data not available ..."}
        # If we got job data then let us filter it as careerJet does not prefer searching based on company filter
        filtered_jobs = [job for job in data.get("jobs", [])if job.get("company", "").lower() == company.lower()]
        # if no filtered jobs exist
        if not filtered_jobs:
            return {"error": "Job data not available ..."}
        # else replace with the filtered jobs
        data['jobs'] = filtered_jobs

        def extract_job_summary(output_dict):
            container = []
            salary_period = {
                'Y': 'YEAR',
                'A': 'ANNUM',
                'M': 'MONTH',
                'W': 'WEEK',
                'D': 'DAY',
                'H': 'HOUR'
            }
            # traverse each job posting
            for job in output_dict.get("jobs", []):
                # filter based on availablility of salary
                if job.get('salary'):
                    # get the job title
                    job_title = job.get('title', '')
                    try:
                        min_salary = float(job.get("salary_min", 0.0))
                        max_salary = float(job.get("salary_max", 0.0))
                    except (ValueError, TypeError):
                        continue
                    currency = job.get("salary_currency_code")
                    if not (min_salary == max_salary):
                        salary_range = f'{currency} {min_salary} - {currency} {max_salary}'
                    else: 
                        salary_range = ''
                        min_salary = ''
                        max_salary = ''
                    # for parsing description
                    parser = customizedParser()
                    description = job.get('description', '')
                    parser.feed(description)
                    description = ''.join(parser.result)
                    job_info = {
                        # basic information
                        'job_title': job_title,
                        'company_name': job.get('company', ''),
                        'location': job.get('locations', ''),
                        
                        # [No base-salary information !!] ---- Note
                        # [No additional-pay information !!] ---- Note

                        # General-salary information
                        'salary': job.get('salary'),
                        'salary_min': min_salary,
                        'salary_max': max_salary,
                        'salary_range': salary_range,
                        'description': description,
                        'date_posted': job.get('date', ''),
                        'url': job.get('url', ''),
                        'salary_currency': currency,
                        'salary_period': salary_period.get(job.get('salary_type','A'), ''),
                        'type': 'postings',
                    }

                    container.append(job_info)
            return container
        job_summary = extract_job_summary(data)
        if(job_summary):
            return job_summary
        else:
            raise Exception
    except Exception as e:
        return {"error": "Job data not available ..."}
# [makes 2 X requests / API Call] -> 100 requests in total (practical threshold)
def glassDoor__v2(company, job_title, location):
    try:
        conn = http.client.HTTPSConnection("real-time-glassdoor-data.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': "7ee1c65373msh181b4a01f21d239p1e5ff7jsnc2f07e071e6d",
            'x-rapidapi-host': "real-time-glassdoor-data.p.rapidapi.com"
        }
        # first get the company ID --> [1st API call]
        query_params = {
            'query': company,
            'limit': 1,
            'domain': 'www.glassdoor.com'
        }
        url_safe_query = urllib.parse.urlencode(query_params)
        # make a request to get company_id
        conn.request("GET", f"/company-search?{url_safe_query}", headers=headers)
        res = conn.getresponse()
        data = res.read() # byte-string
        output_dict = json.loads(data) # dict-format
        # go to the data section
        data = output_dict.get('data',{})
        company_id = data[0].get('company_id',None)

        # Now start for salary-info search ---> [2nd API Call]
        query_params = {
            'company_id': company_id,
            'job_title': job_title,
            'location': location,
            'location_type' : 'ANY',
            'years_of_experience' : 'ALL',
            'domain': 'www.glassdoor.com'
        }
        url_safe_query = urllib.parse.urlencode(query_params)
        # request to get salary data
        conn.request("GET", f"/company-salaries?{url_safe_query}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        output_dict = json.loads(data) # dict-format

        # convert it into structured format
        def getStructuredFormat():
            nonlocal output_dict
            # get the parameters section
            parameters = output_dict.get('parameters',{})
            # get the data section
            data = output_dict.get('data',{})
            # get the required fields
            currency = data.get('salary_currency', '')
            min_sal = data.get('min_salary', 0.0)
            max_sal = data.get('max_salary', 0.0)

            format = {
                # basic information
                'job_title': parameters.get('job_title', None),
                'company_name': data.get('company_name', None),
                'location': parameters.get('location', None),
                # base-salary range
                'min_base_salary': data.get('min_base_salary', 0.0),
                'median_base_salary': data.get('median_base_salary', 0.0),
                'max_base_salary': data.get('max_base_salary', 0.0),
                # additional-pay range
                'min_additional_pay': data.get('min_additional_pay', 0.0),
                # median-additional-pay = mean-salary
                'median_additional_pay': data.get('median_additional_pay', 0.0),
                'max_additional_pay': data.get('max_additional_pay', 0.0),
                # general-salary range
                'min_salary': min_sal,
                'median_salary': data.get('median_salary', 0.0),
                'max_salary': max_sal,
                # other information
                'salary_range': f'{currency} {min_sal} - {currency} {max_sal}',
                'salary_count': data.get('salary_count', None),
                'salary_currency': currency,
                'salary_period': data.get('salary_period', None),
                'provider': 'glassDoor__v2',
                'type': 'estimate',
            }
            return format
        return getStructuredFormat()
    except Exception as e:
        return {"error": str(e)}# "Job data not available ..."}

# JSearch - 200 requests / MO
def jsearch(company, job_title, location):
    try:
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
        if "data" not in res or not res["data"]:
            return {"error": "Job data not available ..."}
        salary_data = res['data'][0]
        return {
            # basic information
            'job_title': salary_data.get("job_title", None),
            'company_name': salary_data.get("company", None),
            'location': salary_data.get("location", None),
            # base salary range
            'min_base_salary': salary_data.get('min_base_salary', 0.0),
            'median_base_salary': salary_data.get('median_base_salary', 0.0),
            'max_base_salary': salary_data.get('max_base_salary', 0.0),
            # additional-pay range
            'min_additional_pay': salary_data.get('min_additional_pay', 0.0),
            'median_additional_pay': salary_data.get('median_additional_pay', 0.0),
            'max_additional_pay': salary_data.get('max_additional_pay', None),
            # general salary range
            'min_salary': salary_data.get('min_salary', 0.0),
            'median_salary': salary_data.get('median_salary', 0.0),
            'max_salary': salary_data.get('max_salary', 0.0),
            'salary_range': f"{salary_data['salary_currency']} {salary_data['min_salary']:,} - {salary_data['salary_currency']} {salary_data['max_salary']:,}",
            'salary_count': salary_data.get('salary_count', None),
            'salary_currency': salary_data["salary_currency"],
            'salary_period': salary_data['salary_period'],
            'provider': 'jsearch',
            'type': 'estimate',
        }
    except Exception as e:
        return {"error": str(e)} # "Job data not available ..."}

# Job_Salary_Data_API - 50 requests / MO
def job_salary_data_api(company, job_title, location, API_KEY=None):
    try:
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
        item = res['data'][0]
        return {
            # basic information
            'job_title': item['job_title'],
            'company_name': item['company'],
            'location': item['location'],
            # base-salary range
            'min_base_salary': item['min_base_salary'],
            'median_base_salary': item['median_base_salary'],
            'max_base_salary': item['max_base_salary'],
            # additional-pay range
            'min_additional_pay': item['min_additional_pay'],
            'median_additional_pay': item['median_additional_pay'],
            'max_additional_pay': item['max_additional_pay'],
            # general-salary range
            'min_salary': item['min_salary'],
            'median_salary': item['median_salary'],
            'max_salary': item['max_salary'],
            # other information
            'salary_range': f'{item.get('salary_currency', '')} {item.get('min_salary', 0.0)} - {item.get('salary_currency','')} {item.get('max_salary', 0.0)}',
            'salary_count': item['salary_count'],
            'salary_currency': item['salary_currency'],
            'salary_period': item['salary_period'],
            'provider': 'job_salary_data',
            'type': 'estimate',
    }
    except Exception as e:
        return {"error": "Job data not available ..."}

# CareerJet API - 1000 requests / hour -> type : postings
def career_jet_api(company, job_title, location):
    try:
        url = "http://public.api.careerjet.net/search"
        params = {
            "locale_code": "en_US",
            "keywords": f"{company} {job_title}",
            "location": location,
            "affid": "09a7e99d93482b93310a29944476cd33",  
            "user_ip": "1.2.3.4",        
            "user_agent": "Mozilla/5.0", 
            "pagesize": 10,              
            "page": 1
        }
        response = requests.get(url, params=params)
        data = response.json()
        # if there are no jobs based on the request made
        if "jobs" not in data or not data["jobs"]:
            return {"error": "Job data not available ..."}
        # If we got job data then let us filter it as careerJet does not prefer searching based on company filter
        filtered_jobs = [job for job in data.get("jobs", [])if job.get("company", "").lower() == company.lower()]
        # if no filtered jobs exist
        if not filtered_jobs:
            return {"error": "Job data not available ..."}
        # else replace with the filtered jobs
        data['jobs'] = filtered_jobs

        def extract_job_summary(output_dict):
            container = []
            salary_period = {
                'Y': 'YEAR',
                'A': 'ANNUM',
                'M': 'MONTH',
                'W': 'WEEK',
                'D': 'DAY',
                'H': 'HOUR'
            }
            # traverse each job posting
            for job in output_dict.get("jobs", []):
                # filter based on availablility of salary
                if job.get('salary'):
                    # get the job title
                    job_title = job.get('title', '')
                    try:
                        min_salary = float(job.get("salary_min", 0.0))
                        max_salary = float(job.get("salary_max", 0.0))
                    except (ValueError, TypeError):
                        continue
                    currency = job.get("salary_currency_code")
                    if not (min_salary == max_salary):
                        salary_range = f'{currency} {min_salary} - {currency} {max_salary}'
                    else: 
                        salary_range = ''
                        min_salary = ''
                        max_salary = ''
                    # for parsing description
                    parser = customizedParser()
                    description = job.get('description', '')
                    parser.feed(description)
                    description = ''.join(parser.result)
                    job_info = {
                        # basic information
                        'job_title': job_title,
                        'company_name': job.get('company', ''),
                        'location': job.get('locations', ''),
                        
                        # [No base-salary information !!] ---- Note
                        # [No additional-pay information !!] ---- Note

                        # General-salary information
                        'salary': job.get('salary'),
                        'salary_min': min_salary,
                        'salary_max': max_salary,
                        'salary_range': salary_range,
                        'description': description,
                        'date_posted': job.get('date', ''),
                        'url': job.get('url', ''),
                        'salary_currency': currency,
                        'salary_period': salary_period.get(job.get('salary_type','A'), ''),
                        'type': 'postings',
                    }

                    container.append(job_info)
            return container
        job_summary = extract_job_summary(data)
        if(job_summary):
            return job_summary
        else:
            raise Exception
    except Exception as e:
        return {"error": "Job data not available ..."}