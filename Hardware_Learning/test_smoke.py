"""Smoke tests for the Hardware Learning Flask app (running on port 8000)."""
import json, urllib.request, sys

BASE = 'http://127.0.0.1:8000'
passed = 0
failed = 0

def test(name, method, path, body=None, expect_status=200, check=None):
    global passed, failed
    url = BASE + path
    data = json.dumps(body).encode('utf-8') if body else None
    headers = {'Content-Type': 'application/json'} if body else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            status = r.status
            resp = r.read().decode()
    except urllib.error.HTTPError as e:
        status = e.code
        resp = e.read().decode()
    ok = status == expect_status
    if ok and check:
        ok = check(json.loads(resp) if resp.strip().startswith('{') or resp.strip().startswith('[') else resp)
    tag = 'PASS' if ok else 'FAIL'
    if ok:
        passed += 1
    else:
        failed += 1
    print(f'  [{tag}] {name}  (HTTP {status})')

print('=== Hardware Learning Smoke Tests ===\n')

# 1. Root page
test('GET / returns 200', 'GET', '/')

# 2. Components API
test('GET /api/components returns JSON array', 'GET', '/api/components',
     check=lambda d: isinstance(d, list) and len(d) >= 5)

# 3. Questions API
test('GET /api/questions returns JSON array', 'GET', '/api/questions',
     check=lambda d: isinstance(d, list) and len(d) >= 1)

# 4. Review add
test('POST /api/review/add succeeds', 'POST', '/api/review/add',
     body={'name': 'test_component'},
     check=lambda d: d.get('ok') is True)

# 5. Review list
test('GET /api/review/list returns array', 'GET', '/api/review/list',
     check=lambda d: isinstance(d, list))

# 6. Wiring attempt — correct
test('POST /api/wiring_attempt (correct)', 'POST', '/api/wiring_attempt',
     body={'question_id':'q3','from':'router.wan','to':'switch.sw_port1','ok':True},
     check=lambda d: d.get('ok') is True and d.get('saved') is True)

# 7. Wiring attempt — incorrect (should also add to review)
test('POST /api/wiring_attempt (incorrect)', 'POST', '/api/wiring_attempt',
     body={'question_id':'q3','from':'router.wan','to':'switch.sw_port2','ok':False},
     check=lambda d: d.get('ok') is True)

# 8. Components refresh
test('POST /api/components/refresh', 'POST', '/api/components/refresh',
     check=lambda d: d.get('ok') is True)

# 9. Components save (update router connectors)
test('POST /api/components/save', 'POST', '/api/components/save',
     body={'id':'router','connectors':[{'id':'wan','x':607.8,'y':220.9},{'id':'lan1','x':611.4,'y':220.9}]},
     check=lambda d: d.get('ok') is True)

# 10. Static SVG image
test('GET /static/images/router.svg returns 200', 'GET', '/static/images/router.svg')

# 11. Static JS
test('GET /static/js/app.js returns 200', 'GET', '/static/js/app.js')

# 12. Static CSS
test('GET /static/css/style.css returns 200', 'GET', '/static/css/style.css')

print(f'\n=== Results: {passed} passed, {failed} failed ===')
sys.exit(0 if failed == 0 else 1)
