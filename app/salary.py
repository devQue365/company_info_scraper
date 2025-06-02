import http.client
import requests
import urllib.parse
from pprint import pprint
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
            # container to store output
            output = []
            # get the location
            location = output_dict.get('data',{}).get('aggregateSalaryResponse',{}).get('queryLocation',{}).get('name',{})
            # go to the results section
            results = output_dict.get('data',{}).get('aggregateSalaryResponse',{}).get('results')
            # traverse each job
            for result in results:
                # get the employer
                employer = result.get('employer', {}).get('name',{}) 
                # get the job title
                job_title = result.get('jobTitle').get('text', {})
                # get the salary currency
                currency = result.get('currency', {}).get('code',{})
                # get the salary period
                period = result.get('payPeriod', {})
                # get the base mean
                base_mean = result.get('basePayStatistics',{}).get('mean',{})
                # get the percentiles (only useful to us - p25, p50, p75)
                percentiles = result.get('totalPayStatistics',{}).get('percentiles',{}) # we get a list here
                p25 = next((p['value'] for p in percentiles if p.get('ident') == 'P25'), None)
                p50 = next((p['value'] for p in percentiles if p.get('ident') == 'P50'), None)
                p75 = next((p['value'] for p in percentiles if p.get('ident') == 'P75'), None)
                # get the salary range (p25 - p75) since, p50 is median
                # get the median salary
                median_salary = p50
                # get mean salary
                mean_salary = result.get('totalAdditionalPayStatistics',{}).get('mean', {})
                # get the ratings
                rating = result.get('employer', {}).get('ratings',{}).get('overallRating',{})
                entry = {
                    'employer': employer,
                    'job_title': job_title,
                    'location': location,
                    'currency': currency,
                    'period': period,
                    'salary_range': f'{currency} {p25} - {currency} {p75}',
                    'base_salary': f'{currency} {base_mean}',
                    'median_salary': f'{currency} {median_salary}',
                    'mean_salary': f'{currency} {mean_salary}',
                    'company_rating': rating
                }
                output.append(entry)
            return output
        salary_data = extract_salary(res)
        return salary_data
    except Exception as e:
        return {"error": "No job data found"}
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
            global output_dict
            # get the parameters section
            parameters = output_dict.get('parameters',{})
            # get the data section
            data = output_dict.get('data',{})
            # get the required fields
            currency = data.get('salary_currency', None)
            min_sal = data.get('min_salary', 0.0)
            max_sal = data.get('max_salary', 0.0)

            format = {
                'company_name': data.get('company_name', None),
                'job_title': parameters.get('job_title', None),
                'location': parameters.get('location', None),
                # base salary range
                'min_base_salary': data.get('min_base_salary', None),
                'median_base_salary': data.get('median_base_salary', None),
                'max_base_salary': data.get('max_base_salary', None),
                # general salary range
                'min_salary': min_sal,
                'median_salary': data.get('median_salary', None),
                # median-additional-pay = mean-salary
                'mean_salary': data.get('median_additional_pay', None),
                'max_salary': max_sal,
                'salary_period': data.get('salary_period', None),
                'salary_range': f'{currency} {min_sal} - {currency} {max_sal}',
                'salary_currency': data.get('salary_currency', None),
            }
            return format
        return getStructuredFormat()
    except:
        return {"error": "Job data not available ..."}
# # JSearch - 200 requests / MO
# def jsearch(company, job_title, location, API_KEY=None):
#     try:
#         conn = http.client.HTTPSConnection("jsearch.p.rapidapi.com")
#         url = "jsearch.p.rapidapi.com"
#         headers = {
#         'x-rapidapi-key': "7ee1c65373msh181b4a01f21d239p1e5ff7jsnc2f07e071e6d",
#         'x-rapidapi-host': "jsearch.p.rapidapi.com"
#         }
#         params = {
#         'company': company,
#         'job_title': job_title,
#         'location' : location,
#         'location_type': 'ANY',
#         'years_of_experience': 'ALL',
#         }
#         url_safe_query = urllib.parse.urlencode(params)
#         conn.request("GET", f"/company-job-salary?{url_safe_query}", headers=headers)
#         res = conn.getresponse()
#         data = res.read() # -> type() : str
#         # get the result in dictionary form 
#         res = json.loads(data)
#         if "jobs" not in res or not res["jobs"]:
#             return {"error": "No job data found"}
#         salary_data = res['data'][0]
#         return {
#             "employer": salary_data["company"],
#             "job_title": salary_data["job_title"],
#             "location": salary_data["location"],
#             "currency": salary_data["salary_currency"],
#             'period': salary_data['salary_period'],
#             "salary_range": f"{salary_data['salary_currency']} {int(salary_data['min_salary']):,} - {int(salary_data['max_salary']):,} per {salary_data['salary_period'].lower()}",
#             "base_salary": f"{salary_data['salary_currency']} {salary_data['median_base_salary']}",
#             "median_salary": f"{salary_data['salary_currency']} {int(salary_data['median_salary']):,}",
#             "company_rating": None
#         }
#     except Exception as e:
#         return {'error': str(e)}

# # GlassDoor API - 200 requests / MO
# def glassDoor(company, job_title, location, API_KEY=None):
#     try:
#         conn = http.client.HTTPSConnection("glassdoor-real-time.p.rapidapi.com")
#         headers = {
#             'x-rapidapi-key': "7ee1c65373msh181b4a01f21d239p1e5ff7jsnc2f07e071e6d",
#             'x-rapidapi-host': "glassdoor-real-time.p.rapidapi.com"
#         }
#         # first extract locationId
#         params = {
#             'query' : location
#         }
#         url_safe_query = urllib.parse.urlencode(params)
#         conn.request("GET", f"/jobs/location?{url_safe_query}", headers=headers)
#         res = conn.getresponse()
#         data = res.read()
#         res = json.loads(data)
#         locationId = res['data'][0]['locationId'] # we got the location ID
#         # Now extract salary data
#         params = {
#             'query' : f'{company} {job_title}',
#             'locationId': locationId,
#             'limit': 10,
#             'page': 1,
#             'sort' : 'POPULAR'
#         }
#         url_safe_query = urllib.parse.urlencode(params)
#         conn.request("GET", f"/salaries/search?{url_safe_query}", headers=headers)
#         res = conn.getresponse()
#         data = res.read()
#         res = json.loads(data)
#         if "data" not in res or not res["data"]:
#             return {"error": "No job data found"}
#         # for glassDoor API we will be transforming the result into more structured form
#         def extract_salary(output_dict):
#             # container to store output
#             output = []
#             # get the location
#             location = output_dict.get('data',{}).get('aggregateSalaryResponse',{}).get('queryLocation',{}).get('name',{})
#             # go to the results section
#             results = output_dict.get('data',{}).get('aggregateSalaryResponse',{}).get('results')
#             # traverse each job
#             for result in results:
#                 # get the employer
#                 employer = result.get('employer', {}).get('name',{}) 
#                 # get the job title
#                 job_title = result.get('jobTitle').get('text', {})
#                 # get the salary currency
#                 currency = result.get('currency', {}).get('code',{})
#                 # get the salary period
#                 period = result.get('payPeriod', {})
#                 # get the base mean
#                 base_mean = result.get('basePayStatistics',{}).get('mean',{})
#                 # get the percentiles (only useful to us - p25, p50, p75)
#                 percentiles = result.get('totalPayStatistics',{}).get('percentiles',{}) # we get a list here
#                 p25 = next((p['value'] for p in percentiles if p.get('ident') == 'P25'), None)
#                 p50 = next((p['value'] for p in percentiles if p.get('ident') == 'P50'), None)
#                 p75 = next((p['value'] for p in percentiles if p.get('ident') == 'P75'), None)
#                 # get the salary range (p25 - p75) since, p50 is median
#                 # get the median salary
#                 median_salary = p50
#                 # get mean salary
#                 mean_salary = result.get('totalAdditionalPayStatistics',{}).get('mean', {})
#                 # get the ratings
#                 rating = result.get('employer', {}).get('ratings',{}).get('overallRating',{})
#                 entry = {
#                     'employer': employer,
#                     'job_title': job_title,
#                     'location': location,
#                     'currency': currency,
#                     'period': period,
#                     'salary_range': f'{currency} {p25} - {currency} {p75}',
#                     'base_salary': f'{currency} {base_mean}',
#                     'median_salary': f'{currency} {median_salary}',
#                     'mean_salary': f'{currency} {mean_salary}',
#                     'company_rating': rating
#                 }
#                 output.append(entry)
#             return output
#         salary_data = extract_salary(res)
#         return salary_data
#     except Exception as e:
#         return {"error": "No job data found"}

# # Job_Salary_Data_API - 50 requests / MO
# def job_salary_data_api(company, job_title, location, API_KEY=None):
#     try:
#         conn = http.client.HTTPSConnection("job-salary-data.p.rapidapi.com")
#         headers = {
#             'x-rapidapi-key': "7ee1c65373msh181b4a01f21d239p1e5ff7jsnc2f07e071e6d",
#             'x-rapidapi-host': "job-salary-data.p.rapidapi.com"
#         }
#         params = {
#             'company': company,
#             'job_title': job_title,
#             'location': location,
#             'location_type': 'ANY',
#             'years_of_experience': 'ALL'
#         }
#         url_safe_query = urllib.parse.urlencode(params)
#         conn.request("GET", f"/company-job-salary?{url_safe_query}", headers=headers)
#         res = conn.getresponse()
#         data = res.read()
#         res = json.loads(data)
#         salary_data = res['data'][0]
#         return {
#             'employer': salary_data['company'],
#             'job_title': salary_data['job_title'],
#             'location': salary_data['location'],
#             'currency': salary_data['salary_currency'],
#             'period': salary_data['salary_period'],
#             'salary_range' : f'{salary_data['salary_currency']} {salary_data['min_salary']} - {salary_data['salary_currency']} {salary_data['max_salary']}',
#             'median_salary': f'{salary_data['salary_currency']} {salary_data['median_salary']}',
#             'mean_salary': f'{salary_data['salary_currency']} {round(salary_data['result']['totalPayStatistics']['mean'])}',
#             'company_rating': salary_data['result']['employer']['ratings']['overallRating']
#             # 'confidence': salary_data['confidence'],
#             # 'min_salary': salary_data['min_salary'],
#             # 'max_salary': salary_data['max_salary'],
#             # 'salary_count': salary_data['salary_count'],
#         }
#     except Exception as e:
#         return {"error": "No job data found"}

# # CareerJet API - 1000 requests / hour
# def carrer_jet_api(company, job_title, location):
#     try:
#         url = "http://public.api.careerjet.net/search"

#         params = {
#             "locale_code": "en_US",
#             "keywords": f"{company} {job_title}",
#             "location": location,
#             "affid": "09a7e99d93482b93310a29944476cd33",  
#             "user_ip": "1.2.3.4",        
#             "user_agent": "Mozilla/5.0", 
#             "pagesize": 10,              
#             "page": 1
#         }
#         response = requests.get(url, params=params)
#         data = response.json()
#         # if there are no jobs based on the request made
#         if "jobs" not in data or not data["jobs"]:
#             return {"error": "No job data found"}
#         # If we got job data then let us filter it
#         filtered_jobs = [job for job in data.get("jobs", [])if job.get("company", "").lower() == company.lower()]
#         # if no filtered jobs exist
#         if not filtered_jobs:
#             return {"error": "No job data found"}
#         # else replace with the filtered jobs
#         data['jobs'] = filtered_jobs
#         def extract_job_summary(output_dict):
#             salaries = []
#             job_list = []
#             salary_period = {
#                 'Y': 'YEAR',
#                 'A': 'ANNUM',
#                 'M': 'MONTH',
#                 'W': 'WEEK',
#                 'D': 'DAY',
#                 'H': 'HOUR'
#             }
            
#             for job in output_dict.get("jobs", []):
#                 title = job.get("title", "")
#                 job_list.append(title)
#                 try:
#                     min_salary = float(job.get("salary_min", 0))
#                     max_salary = float(job.get("salary_max", 0))

#                     if min_salary:
#                         salaries.append(min_salary)
#                     if max_salary and max_salary != min_salary:
#                         salaries.append(max_salary)
#                 except (ValueError, TypeError):
#                     continue
#             # if not salaries:
#             #     return {
#             #         'salary_range': 'N/A',
#             #         'base_salary': 'N/A',
#             #         'median_salary': 'N/A',
#             #         'mean_salary': 'N/A',
#             #     }
#             if(salaries):
#                 salaries.sort()
#                 currency = output_dict.get("salary_currency_code")
#                 salary_range = f'{currency} {min(salaries):.2f} - {currency} {max(salaries):.2f}'
#                 base_salary = f'{currency} {min(salaries):.2f}'
#                 mean_salary = sum(salaries) / len(salaries)
#                 median_salary = (
#                     salaries[len(salaries) // 2]
#                     if len(salaries) % 2 == 1
#                     else (salaries[len(salaries) // 2 - 1] + salaries[len(salaries) // 2]) / 2
#                 )
#             else:
#                 salary_range = None
#                 base_salary = None
#                 median_salary = None
#                 mean_salary = None

#             job_info = {
#                 "employer": next((p['company'] for p in output_dict.get('jobs', [])), None),
#                 # "job_title": job.get("title", "").split(",")[0],  # I removed extra qualifiers like amazon-ADS
#                 "job_title": job_list,
#                 "location": next((p['locations'] for p in output_dict.get("jobs", [])), None),
#                 "currency": next((p['salary_currency_code'] for p in output_dict.get("jobs", []) if p.get('salary_currency_code')), None),
#                 "period": salary_period.get(next((p.get("salary_type") for p in output_dict.get("jobs", [])), None),None),
#                 "salary_range": salary_range,
#                 "base_salary": base_salary,
#                 "median_salary": f'{currency} {median_salary:.2f}' if median_salary is not None else None,
#                 "mean_salary": f'{currency} {mean_salary:.2f}' if mean_salary is not None else None,
#                 "company_rating": None
#             }
#             return job_info
#         job_summary = extract_job_summary(data)
#         return job_summary
#     except Exception as e:
#         return {'error': str(e)}