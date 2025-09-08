import requests

BASE_URL = 'http://localhost:8000'
EMPLOYEE_ID = 1

def auth_header(token):
    return {'Authorization': f'Bearer {token}'}

def get_token(email, password):
    r = requests.post(f'{BASE_URL}/auth/login', json={'email': email, 'password': password})
    r.raise_for_status()
    return r.json()['access_token']

# Get tokens
ADMIN_JWT = get_token('admin@app.com', 'supersecure123')
DEMO_JWT = get_token('demo@company.com', 'password123')
print(f'Admin token: {ADMIN_JWT[:20]}...')
print(f'Demo token: {DEMO_JWT[:20]}...')

def safe_get(url, token):
    try:
        r = requests.get(url, headers=auth_header(token))
        return r
    except Exception as e:
        print(f'Exception on GET {url}: {e}')
        return None

def safe_post(url, data, token):
    try:
        r = requests.post(url, json=data, headers=auth_header(token))
        return r
    except Exception as e:
        print(f'Exception on POST {url}: {e}')
        return None

def safe_put(url, data, token):
    try:
        r = requests.put(url, json=data, headers=auth_header(token))
        return r
    except Exception as e:
        print(f'Exception on PUT {url}: {e}')
        return None

print('\n=== Pre-test cleanup ===')
r = safe_get(f'{BASE_URL}/attendance/active/{EMPLOYEE_ID}', ADMIN_JWT)
if r and r.status_code == 200:
    records = r.json()
    for record in records:
        print(f'Found active record: {record}')
        r_out = safe_put(f'{BASE_URL}/attendance/clock-out', {'employee_id': EMPLOYEE_ID, 'attendance_id': record['id']}, ADMIN_JWT)
        if r_out:
            print(f'Clock-out cleanup result: {r_out.status_code}')
else:
    print('No active attendance records.')

print('\n=== Admin Tests ===')
print('Clock-in:')
r = safe_post(f'{BASE_URL}/attendance/clock-in', {'employee_id': EMPLOYEE_ID, 'notes': 'Starting shift'}, ADMIN_JWT)
attendance = None
if r and r.status_code == 201:
    attendance = r.json()
    print(f'Success: {attendance}')
else:
    print(f'Failed: {r.status_code if r else "request failed"} - {r.text if r else ""}')

if attendance:
    print('Break start:')
    r = safe_post(f'{BASE_URL}/attendance/break-start', {'attendance_id': attendance['id'], 'break_type': 'lunch'}, ADMIN_JWT)
    if r and r.status_code == 201:
        brk = r.json()
        print(f'Success: {brk}')
    else:
        print(f'Failed: {r.status_code if r else "request failed"} - {r.text if r else ""}')

    print('Break end:')
    r = safe_post(f'{BASE_URL}/attendance/break-end', {'attendance_id': attendance['id']}, ADMIN_JWT)
    if r and r.status_code == 200:
        brk = r.json()
        print(f'Success: {brk}')
    else:
        print(f'Failed: {r.status_code if r else "request failed"} - {r.text if r else ""}')

    print('Clock-out:')
    r = safe_put(f'{BASE_URL}/attendance/clock-out', {'employee_id': EMPLOYEE_ID, 'attendance_id': attendance['id']}, ADMIN_JWT)
    if r and r.status_code == 200:
        print(f'Success: {r.json()}')
    else:
        print(f'Failed: {r.status_code if r else "request failed"} - {r.text if r else ""}')

print('Attendance retrieval:')
r = safe_get(f'{BASE_URL}/attendance/{EMPLOYEE_ID}', ADMIN_JWT)
if r and r.status_code == 200:
    print(f'Success: {r.json()}')
else:
    print(f'Failed: {r.status_code if r else "request failed"} - {r.text if r else ""}')

print('\n=== Demo User Tests ===')
print('Attendance retrieval:')
r = safe_get(f'{BASE_URL}/attendance/{EMPLOYEE_ID}', DEMO_JWT)
if r and r.status_code == 200:
    print(f'Success: {r.json()}')
else:
    print(f'Failed: {r.status_code if r else "request failed"} - {r.text if r else ""}')

print('Break start (should fail):')
r = safe_post(f'{BASE_URL}/attendance/break-start', {'attendance_id': 1, 'break_type': 'lunch'}, DEMO_JWT)
if r and r.status_code == 403:
    print(f'Expected failure: {r.json()}')
else:
    print(f'Unexpected: {r.status_code if r else "request failed"} - {r.text if r else ""}')

print('Break end (should fail):')
r = safe_post(f'{BASE_URL}/attendance/break-end', {'attendance_id': 1}, DEMO_JWT)
if r and r.status_code == 403:
    print(f'Expected failure: {r.json()}')
else:
    print(f'Unexpected: {r.status_code if r else "request failed"} - {r.text if r else ""}')

print('\n=== Post-test cleanup ===')
r = safe_get(f'{BASE_URL}/attendance/active/{EMPLOYEE_ID}', ADMIN_JWT)
if r and r.status_code == 200:
    records = r.json()
    if records:
        print(f'Active records found: {records}')
        for record in records:
            r_out = safe_put(f'{BASE_URL}/attendance/clock-out', {'employee_id': EMPLOYEE_ID, 'attendance_id': record['id']}, ADMIN_JWT)
            if r_out:
                print(f'Cleanup clock-out result: {r_out.status_code}')
    else:
        print('No active records.')
else:
    print('Cleanup check failed.')
