import urllib.request, json

req = urllib.request.Request('http://localhost:8000/api/v1/auth/login', 
    data=json.dumps({'username':'admin','password':'Admin@123'}).encode('utf-8'), 
    headers={'Content-Type': 'application/json'})
res = urllib.request.urlopen(req)
token = json.loads(res.read())['data']['session_token']

req2 = urllib.request.Request('http://localhost:8000/api/v1/departments/', headers={'X-Token': token})
res2 = urllib.request.urlopen(req2)
depts = json.loads(res2.read())['data']
dept_id = depts[0]['id']

# 1. Create a business rule
rule_payload = {
    "rule_name": "Reduce Budget if ROI < 40",
    "entity_type": "department",
    "condition": {
        "metric": "department_roi",
        "operator": "<",
        "value": 40.0
    },
    "action": {
        "recommendation": "reduce_budget"
    },
    "priority": 1,
    "enabled": True
}
req3 = urllib.request.Request('http://localhost:8000/api/v1/analytics/rules', 
    data=json.dumps(rule_payload).encode('utf-8'), 
    headers={'Content-Type': 'application/json', 'X-Token': token})
try:
    res3 = urllib.request.urlopen(req3)
    print("Created rule:", json.loads(res3.read()))
except urllib.error.HTTPError as e:
    print("HTTPError:", e.read().decode())

# 2. Evaluate rules
eval_payload = {
    "entity_type": "department",
    "department_id": dept_id
}
req4 = urllib.request.Request('http://localhost:8000/api/v1/analytics/evaluate', 
    data=json.dumps(eval_payload).encode('utf-8'), 
    headers={'Content-Type': 'application/json', 'X-Token': token})
try:
    res4 = urllib.request.urlopen(req4)
    print("Eval result:", json.loads(res4.read()))
except Exception as e:
    print("Eval failed:", str(e))
