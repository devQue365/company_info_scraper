# **Scraping API**
## Switching Logic (Based on salary data)
- Here in our API, I have used multiple APIs' to get the salary data based on the request made by the user.
- The APIs' used are :-
    - Jsearch API (Rapid API) {200 requests / MO}
    - GlassDoor API (Rapid API) {200 requests / MO}
    - JobSalaryData API (Rapid API) {50 requests / MO}
    - CareerJet API (Official website) {1000 requests / Hr}
- Now, our job is to design a system which could handle switching between APIs' based on different scenarios :-
    - If the API's end limit is reached, we want to hop on to the next available API.
    - If the active API fails to fetch results then the job is passed on to the next available active API.
## <u>Approach Used :-</u>
- Simply mantain a database (Here, I used SQLite for simplicity).
- The database consists of API Usage schema which hold records for each and every API we have used (One schema for each purpose like for Salary extraction).
- Here, I have used SQLAlchemy for communicating between python and SQL server.
- I have tried to implement the system with the goal of complete abstraction from the users.
![API Working](api_snapshot.png)
![SQLite snapshot](ss1.png)
- Here as we can see Jsearch API could not fetch the result and thus, we hopped on to the next available active API (here GlassDoor API).<br>
>**Note:** Here I have initially considered the ```used_requests = 0``` for simplicity and testing.