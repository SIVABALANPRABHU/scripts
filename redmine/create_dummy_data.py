import requests
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

API_KEY = '6efc24be62ac5c39dd0b8b26ebc2d6b91c420eb3'
BASE_URL = 'http://localhost:3500'
HEADERS = {'X-Redmine-API-Key': API_KEY, 'Content-Type': 'application/json'}

def get_default_role_id():
    response = requests.get(f"{BASE_URL}/roles.json", headers=HEADERS)
    if response.status_code == 200:
        roles = response.json()["roles"]
        if roles:
            return roles[0]["id"]
    return None

def get_time_entry_activities():
    response = requests.get(f"{BASE_URL}/enumerations/time_entry_activities.json", headers=HEADERS)
    if response.status_code == 200:
        activities = response.json()["time_entry_activities"]
        return [activity["id"] for activity in activities]
    return []

def create_project(name):
    payload = {
        "project": {
            "name": name,
            "identifier": name.lower().replace(" ", "-") + str(random.randint(1000, 9999))
        }
    }
    response = requests.post(f"{BASE_URL}/projects.json", headers=HEADERS, json=payload)
    if response.status_code == 201:
        return response.json()["project"]["id"]
    else:
        print("Failed to create project:", response.text)
        return None

def create_user():
    user = {
        "user": {
            "login": fake.user_name(),
            "firstname": fake.first_name(),
            "lastname": fake.last_name(),
            "mail": fake.email(),
            "password": "password123"
        }
    }
    response = requests.post(f"{BASE_URL}/users.json", headers=HEADERS, json=user)
    if response.status_code == 201:
        return response.json()["user"]["id"]
    else:
        print("Failed to create user:", response.text)
        return None

def add_user_to_project(project_id, user_id, role_id):
    membership = {
        "membership": {
            "user_id": user_id,
            "role_ids": [role_id]
        }
    }
    response = requests.post(f"{BASE_URL}/projects/{project_id}/memberships.json", headers=HEADERS, json=membership)
    if response.status_code != 201:
        print(f"Failed to add user {user_id} to project:", response.text)

def create_issue(project_id, user_id):
    issue = {
        "issue": {
            "project_id": project_id,
            "subject": fake.sentence(nb_words=6),
            "description": fake.paragraph(),
            "assigned_to_id": user_id
        }
    }
    response = requests.post(f"{BASE_URL}/issues.json", headers=HEADERS, json=issue)
    if response.status_code == 201:
        return response.json()["issue"]["id"]
    else:
        print("Failed to create issue:", response.text)
        return None

def log_time(issue_id, user_id, activity_ids, spent_date):
    hours = round(random.uniform(1, 8), 2)
    activity_id = random.choice(activity_ids)
    time_entry = {
        "time_entry": {
            "issue_id": issue_id,
            "user_id": user_id,
            "hours": hours,
            "comments": "Worked on issue",
            "activity_id": activity_id,
            "spent_on": spent_date.strftime('%Y-%m-%d')
        }
    }
    response = requests.post(f"{BASE_URL}/time_entries.json", headers=HEADERS, json=time_entry)
    if response.status_code != 201:
        print(f"Failed to log time for issue {issue_id}:", response.text)

# -------- Main Execution --------

role_id = get_default_role_id()
if not role_id:
    print("No roles found.")
    exit()

activity_ids = get_time_entry_activities()
if not activity_ids:
    print("No time entry activities found. Please check Redmine settings.")
    exit()

project_id = create_project("Dummy Project")
if not project_id:
    exit()

user_ids = []
for _ in range(5):
    user_id = create_user()
    if user_id:
        user_ids.append(user_id)
        add_user_to_project(project_id, user_id, role_id)

for day_offset in range(30):
    date = datetime.now() - timedelta(days=day_offset)
    for _ in range(random.randint(2, 5)):
        user_id = random.choice(user_ids)
        issue_id = create_issue(project_id, user_id)
        if issue_id:
            log_time(issue_id, user_id, activity_ids, date)

print("Dummy Redmine data generation complete.")
