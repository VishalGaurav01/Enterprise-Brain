import urllib.request, json

req = urllib.request.Request('http://localhost:8000/api/v1/auth/login', 
    data=json.dumps({'username':'admin','password':'Admin@123'}).encode('utf-8'), 
    headers={'Content-Type': 'application/json'})
res = urllib.request.urlopen(req)
token = json.loads(res.read())['data']['token']

req2 = urllib.request.Request('http://localhost:8000/api/v1/departments/', headers={'X-Token': token})
res2 = urllib.request.urlopen(req2)
depts = json.loads(res2.read())['data']
print("Departments:", [d['name'] for d in depts])

req3 = urllib.request.Request('http://localhost:8000/api/v1/analytics/evaluate', 
    data=json.dumps({'rule_name':'department_profit_v1', 'department_id': depts[0]['id']}).encode('utf-8'), 
    headers={'Content-Type': 'application/json', 'X-Token': token})
try:
    res3 = urllib.request.urlopen(req3)
    print("Eval result:", json.loads(res3.read()))
except Exception as e:
    print("Eval failed:", str(e))
