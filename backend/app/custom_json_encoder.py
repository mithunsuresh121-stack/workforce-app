import json
from typing import Any


def custom_json_dumps(obj: Any, **kwargs) -> str:
    """Custom JSON dumps function that ensures proper formatting with commas"""
    if isinstance(obj, dict):
        items = []
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                value_str = custom_json_dumps(value, **kwargs)
            else:
                value_str = json.dumps(value, **kwargs)
            items.append(f'"{key}": {value_str}')
        return "{" + ", ".join(items) + "}"
    elif isinstance(obj, list):
        items = []
        for item in obj:
            if isinstance(item, (dict, list)):
                items.append(custom_json_dumps(item, **kwargs))
            else:
                items.append(json.dumps(item, **kwargs))
        return "[" + ", ".join(items) + "]"
    else:
        return json.dumps(obj, **kwargs)


# Test the custom encoder
if __name__ == "__main__":
    test_data = {
        "test": "value",
        "number": 123,
        "boolean": True,
        "nested": {"key": "value"},
        "array": [1, 2, 3],
    }

    result = custom_json_dumps(test_data, indent=2)
    print("Custom encoder result:")
    print(result)
