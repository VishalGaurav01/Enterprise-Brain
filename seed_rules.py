import urllib.request
import json

BASE_URL = 'http://localhost:8000/api/v1'

def login():
    req = urllib.request.Request(f'{BASE_URL}/auth/login', 
        data=json.dumps({'username': 'admin', 'password': 'Admin@123'}).encode('utf-8'), 
        headers={'Content-Type': 'application/json'})
    res = urllib.request.urlopen(req)
    return json.loads(res.read())['data']['session_token']

def create_rule(token, rule):
    req = urllib.request.Request(f'{BASE_URL}/analytics/rules', 
        data=json.dumps(rule).encode('utf-8'), 
        headers={'Content-Type': 'application/json', 'X-Token': token})
    try:
        res = urllib.request.urlopen(req)
        print(f"Created rule: {rule['rule_name']}")
    except urllib.error.HTTPError as e:
        print(f"Failed to create rule '{rule['rule_name']}': {e.read().decode()}")

def main():
    print("Logging in...")
    try:
        token = login()
        print("Logged in successfully.")
    except Exception as e:
        print("Login failed:", str(e))
        return

    rules = [
        # Employee Rules
        {
            "rule_name": "Low Employee ROI Alert",
            "entity_type": "employee",
            "condition": {"metric": "employee_roi", "operator": "<", "value": 20.0},
            "action": {"recommendation": "investigate_performance", "severity": "medium"},
            "priority": 1,
            "enabled": True
        },
        {
            "rule_name": "Employee Burnout Risk",
            "entity_type": "employee",
            "condition": {"metric": "employee_utilization", "operator": ">", "value": 90.0},
            "action": {"recommendation": "burnout_risk_alert", "severity": "high"},
            "priority": 2,
            "enabled": True
        },
        # Project Rules
        {
            "rule_name": "Low Project ROI",
            "entity_type": "project",
            "condition": {"metric": "project_roi", "operator": "<", "value": 10.0},
            "action": {"recommendation": "review_project_costs", "severity": "high"},
            "priority": 1,
            "enabled": True
        },
        {
            "rule_name": "Low Project Margin",
            "entity_type": "project",
            "condition": {"metric": "project_margin", "operator": "<", "value": 15.0},
            "action": {"recommendation": "renegotiate_vendor_contracts", "severity": "medium"},
            "priority": 2,
            "enabled": True
        },
        # Department Rules
        {
            "rule_name": "Department Budget Review",
            "entity_type": "department",
            "condition": {"metric": "department_roi", "operator": "<", "value": 30.0},
            "action": {"recommendation": "reduce_budget", "severity": "high"},
            "priority": 1,
            "enabled": True
        },
        {
            "rule_name": "Department Bonus Allocation",
            "entity_type": "department",
            "condition": {"metric": "department_roi", "operator": ">", "value": 60.0},
            "action": {"recommendation": "allocate_bonus_pool", "severity": "low"},
            "priority": 2,
            "enabled": True
        },
        # Organization Rules
        {
            "rule_name": "Organization Hiring Freeze",
            "entity_type": "organization",
            "condition": {"metric": "organization_margin", "operator": "<", "value": 20.0},
            "action": {"recommendation": "freeze_hiring", "severity": "critical"},
            "priority": 1,
            "enabled": True
        }
    ]

    print(f"\nSeeding {len(rules)} business rules...")
    for rule in rules:
        create_rule(token, rule)

if __name__ == "__main__":
    main()
