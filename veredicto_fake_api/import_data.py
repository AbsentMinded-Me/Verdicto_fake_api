# import_data.py

import json

def load_legal_data(file_path="fake_legal_data.json"):
    """
    Loads Indian legal documents dataset from JSON file.
    
    Args:
        file_path (str): Path to JSON file.
    
    Returns:
        list: List of legal document dictionaries.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return []
    except json.JSONDecodeError:
        print("Error: Invalid JSON format.")
        return []

# Test Run
if __name__ == "__main__":
    dataset = load_legal_data()
    print(f"Loaded {len(dataset)} legal documents.")
    for doc in dataset[:2]:  # show first 2 only
        print(doc)

