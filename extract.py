import json

def read_and_format_json(json_file_path, set_name):
    # Load JSON data from the file
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Check if the set exists in the JSON data
    # set_data = data[set_name]
    # Assuming 'clue' and 'words' are the keys for clues and words list
    clue = data['clues'][set_name][0]
    clue_num = data['clues'][set_name][1]
    words = data['words'][set_name]

    # Print the formatted output
    print(f"[{clue}][{clue_num}]")
    print(', '.join(f'"{word}"' for word in words))

# Example usage
json_file_path = 'words.json'  # Replace with your JSON file path
set_name = 'Set-4'  # Replace with the set you want to extract
read_and_format_json(json_file_path, set_name)
