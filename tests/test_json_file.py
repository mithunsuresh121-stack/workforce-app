import json

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

# Write JSON to a file
with open('test_output.json', 'w') as f:
    json.dump(data, f)

# Read the file back and print the content
with open('test_output.json', 'r') as f:
    content = f.read()
    print("File content:", repr(content))

# Also try to parse it back
try:
    parsed = json.loads(content)
    print("Parsed successfully:", parsed)
except Exception as e:
    print("Error parsing:", e)
