import http.client
import urllib.parse
import requests

# Threshold : 300 Requests / MO
def ov__1(company_name : str):
    query_params = {
        "query": company_name,
        "limit": 1,
    }
    # get url_safe_query
    url_safe_query = urllib.parse.urlencode(query_params)
    url = f'https://gateway.apyflux.com/v1/company-search?{url_safe_query}'
    headers = {
        'x-app-id': '9da38c84-63ec-4167-b987-f07a8fd3d21b',
        'x-client-id': 'WpSCtxgRVtUWLO1905yPuj1lhu22',
        'x-api-key': 'pEovSWskDx0vzcvbs8EXbO9AFzVlVxPo10gJ1mDoEnM='
    }
    response = requests.get(url, headers=headers, timeout=10)
    def summarize(data):
        container = {}
        # extract general information
        container["status"] = data.get("status", '')
        container["request_id"] = data.get("request_id", '')
        container["query_parameters"] = data.get("parameters", {})

        # extract company information
        company_data = data.get("data", [{}])[0]
        container["company"] = {
            "company_id": company_data.get("company_id", ''),
            "name": company_data.get("name", ''),
            "company_link": company_data.get("company_link", ''),
            "rating": company_data.get("rating", ''),
            "review_count": company_data.get("review_count", ''),
            "salary_count": company_data.get("salary_count", ''),
            "job_count": company_data.get("job_count", ''),
            "headquarters_location": company_data.get("headquarters_location", ''),
            "logo": company_data.get("logo", ''),
            "company_size": company_data.get("company_size", ''),
            "company_size_category": company_data.get("company_size_category", ''),
            "company_description": company_data.get("company_description", ''),
            "industry": company_data.get("industry", ''),
            "website": company_data.get("website", ''),
            "company_type": company_data.get("company_type", ''),
            "revenue": company_data.get("revenue", ''),
            "year_founded": company_data.get("year_founded", ''),
            "stock": company_data.get("stock", ''),
            "ceo": company_data.get("ceo", ''),
            "ceo_rating": company_data.get("ceo_rating", ''),
            "business_outlook_rating": company_data.get("business_outlook_rating", ''),
            "career_opportunities_rating": company_data.get("career_opportunities_rating", ''),
            "compensation_and_benefits_rating": company_data.get("compensation_and_benefits_rating", ''),
            "culture_and_values_rating": company_data.get("culture_and_values_rating", ''),
            "diversity_and_inclusion_rating": company_data.get("diversity_and_inclusion_rating", ''),
            "recommend_to_friend_rating": company_data.get("recommend_to_friend_rating", ''),
            "senior_management_rating": company_data.get("senior_management_rating", ''),
            "work_life_balance_rating": company_data.get("work_life_balance_rating", ''),
        }

        # extract competitors
        container["competitors"] = [
            {"id": competitor.get("id", ''), "name": competitor.get("name", '')}
            for competitor in company_data.get("competitors", [])
        ]

        # extract office locations
        container["office_locations"] = [
            {"city": location.get("city", ''), "country": location.get("country", '')}
            for location in company_data.get("office_locations", [])
        ]

        # extract awards
        container["best_places_to_work_awards"] = [
            {"time_period": award.get("time_period", ''), "rank": award.get("rank", '')}
            for award in company_data.get("best_places_to_work_awards", [])
        ]

        # extract useful links
        container["useful_links"] = {
            "reviews_link": company_data.get("reviews_link", ''),
            "jobs_link": company_data.get("jobs_link", ''),
            "faq_link": company_data.get("faq_link", ''),
        }

        return container
    return summarize(response.json())
    # print(response.text)

def ov__2(company_name : str):
    pass
