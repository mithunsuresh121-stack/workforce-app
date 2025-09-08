def custom_json_dumps(data):
    """
    Custom JSON serialization function to work around the system-level JSON issue.
    """
    if isinstance(data, dict):
        items = []
        for key, value in data.items():
            # Recursively serialize values
            serialized_value = custom_json_dumps(value)
            items.append(f'"{key}": {serialized_value}')
        return '{' + ', '.join(items) + '}'
    elif isinstance(data, list):
        items = [custom_json_dumps(item) for item in data]
        return '[' + ', '.join(items) + ']'
    elif isinstance(data, str):
        return f'"{data}"'
    elif isinstance(data, (int, float)):
        return str(data)
    elif data is None:
        return 'null'
    elif isinstance(data, bool):
        return 'true' if data else 'false'
    else:
        # Fallback to string representation for other types
        return f'"{str(data)}"'

# Test the custom JSON serialization
if __name__ == "__main__":
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
    
    result = custom_json_dumps(data)
    print("Custom JSON Output:", result)
