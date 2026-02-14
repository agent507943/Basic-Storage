import json, urllib.request
url='http://127.0.0.1:8000/api/wiring_attempt'
data={'question_id':'q3','from':'router.wan','to':'switch.sw_port1','ok':True}
req=urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type':'application/json'})
with urllib.request.urlopen(req) as r:
    print(r.status)
    print(r.read().decode())
