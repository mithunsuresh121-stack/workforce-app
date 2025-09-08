import simplejson as json

# Sample data to test JSON serialization
data = {
    "title": "Test Task",
    "description": "This is a test task",
    "status": "To Do",
    "due_at": None,
    "assignee_id": None,
    "id": 1,
    "company_id": 1,
    "created_at": "2025-08-24T14:37:10.399079",
    "updated_at": "2025-08-24T14:37:10.399079"
}

# Attempt to serialize the data
try:
    json_output = json.dumps(data)
    print("JSON Output:", json_output)
except Exception as e:
    print("Error during JSON serialization:", e)
