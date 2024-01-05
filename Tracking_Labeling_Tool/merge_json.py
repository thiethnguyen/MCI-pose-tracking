import os
import json
from pathlib import Path


def get_all_files_recursively_by_ext(root, ext):
    found = []
    for path in Path(root).rglob('*.{}'.format(ext)):
        found.append(str(path))
    return sorted(found)


# Specify the folder path where JSON files are located
input_folder = 'output_jsons'  # Replace with the path to your folder

# Initialize an empty dictionary to store the consolidated data
consolidated_data = {}

label_jsons = get_all_files_recursively_by_ext(input_folder, "json")
label_jsons = sorted(label_jsons, key=lambda x: int(Path(x).stem.split("_")[-1]))

# Iterate through all JSON files in the folder
for filename in label_jsons:
    # if filename.endswith('.json'):
    # Generate the frame ID from the filename (e.g., 'frame_1.json' -> '1')
    frame_id = filename.split('_')[-1].split('.')[0]

    # Load the JSON data from the file
    with open(filename, 'r') as json_file:
        frame_data = json.load(json_file)

    # Add the frame data to the consolidated data dictionary
    consolidated_data[str(int(frame_id) + 1)] = frame_data[str(int(frame_id) + 1)]

# Now, consolidated_data contains the original JSON structure with data from all JSON files
# You can use consolidated_data for further processing or analysis
# For example, you can convert it back to a JSON string using json.dumps(consolidated_data)
output_folder = 'ori_json'
# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
# Generate a JSON filename for the frame (e.g., frame_1.json)
ori_filename = os.path.join(output_folder, f"base_name_ori.json")

# Save the frame data to a JSON file
with open(ori_filename, "w") as json_file:
    json.dump(consolidated_data, json_file)
